"""Delivery Data Fetcher Module - Fetch NSE delivery/bhavcopy data with batch caching"""

import requests
import pandas as pd
import io
import zipfile
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..utils.retry import retry_with_backoff
from ..utils.validators import validate_symbol, sanitize_symbol, validate_date

logger = logging.getLogger(__name__)


class DeliveryDataFetcher:
    """Fetch NSE delivery data (bhavcopy) with batch caching for 50-100x speedup"""
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    
    def __init__(self):
        """Initialize delivery data fetcher"""
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._cache = {}
        self._warmup_complete = False
    
    def warmup_cache(self, days: int = 10, max_workers: int = 5):
        """
        Pre-download and cache multiple bhavcopy files concurrently
        This provides 50-100x speedup by avoiding per-stock fetches
        
        Args:
            days: Number of past trading days to cache
            max_workers: Concurrent download threads
        """
        logger.info(f"Warming up delivery data cache for {days} days...")
        
        dates = []
        current_date = self._get_previous_trading_day()
        
        # Generate list of dates to fetch
        attempts = 0
        while len(dates) < days and attempts < days * 3:
            if current_date.weekday() < 5:  # Skip weekends
                dates.append(current_date)
            current_date -= timedelta(days=1)
            attempts += 1
        
        # Download concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.fetch_delivery_data, date): date
                for date in dates
            }
            
            successful = 0
            for future in as_completed(futures):
                date = futures[future]
                try:
                    df = future.result()
                    if df is not None:
                        successful += 1
                except Exception as e:
                    logger.debug(f"Failed to cache {date}: {str(e)}")
        
        self._warmup_complete = True
        logger.info(f"Cache warmup complete: {successful}/{len(dates)} files cached")
        return successful
    
    @retry_with_backoff(max_attempts=2, base_delay=1.0)
    def fetch_delivery_data(self, date: datetime = None) -> Optional[pd.DataFrame]:
        """
        Fetch delivery data for a specific date
        
        Args:
            date: Date to fetch data for (defaults to previous trading day)
        
        Returns:
            DataFrame with delivery data or None if failed
        """
        if date is None:
            date = self._get_previous_trading_day()
        
        # Check cache
        cache_key = date.strftime("%Y%m%d")
        if cache_key in self._cache:
            return self._cache[cache_key].copy()
        
        try:
            df = self._download_bhavcopy(date)
            if df is not None and not df.empty:
                # Cache the result
                self._cache[cache_key] = df.copy()
                return df
            
            logger.debug(f"No delivery data for {date.strftime('%Y-%m-%d')}")
            return None
            
        except Exception as e:
            logger.debug(f"Error fetching delivery data for {date.strftime('%Y-%m-%d')}: {str(e)}")
            return None
    
    def _download_bhavcopy(self, date: datetime) -> Optional[pd.DataFrame]:
        """Download and parse NSE bhavcopy file with better error handling"""
        # Format: https://archives.nseindia.com/products/content/sec_bhavdata_full_DDMMYYYY.csv
        date_str = date.strftime("%d%m%Y")
        url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Parse CSV
            df = pd.read_csv(io.StringIO(response.text))
            
            # Strip whitespace from column names AND values (NSE files have leading spaces everywhere)
            df.columns = df.columns.str.strip()
            
            # Strip whitespace from all string columns
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.strip()
            
            # Robust column handling - check if SERIES exists before filtering
            if 'SERIES' in df.columns:
                df = df[df['SERIES'] == 'EQ']  # Only equity series
            else:
                logger.debug(f"No SERIES column in bhavcopy for {date_str}, using full dataset")
            
            # Select relevant columns if they exist
            columns_map = {}
            if 'SYMBOL' in df.columns:
                columns_map['SYMBOL'] = 'symbol'
            if 'TTL_TRD_QNTY' in df.columns:
                columns_map['TTL_TRD_QNTY'] = 'traded_qty'
            if 'DELIV_QTY' in df.columns:
                columns_map['DELIV_QTY'] = 'delivery_qty'
            if 'DELIV_PER' in df.columns:
                columns_map['DELIV_PER'] = 'delivery_percentage'
            
            if not columns_map:
                logger.debug(f"No expected columns found in bhavcopy for {date_str}")
                return None
            
            df = df.rename(columns=columns_map)
            df = df[list(columns_map.values())]
            
            # Convert to numeric
            for col in ['delivery_percentage', 'traded_qty', 'delivery_qty']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove NaN
            df = df.dropna(subset=['symbol'] if 'symbol' in df.columns else [])
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"Failed to download bhavcopy for {date_str}: {str(e)}")
            return None
        except Exception as e:
            logger.debug(f"Error parsing bhavcopy for {date_str}: {str(e)}")
            return None
    
    def fetch_delivery_trend(
        self, 
        symbol: str, 
        days: int = 90,
        spike_threshold: float = 2.0
    ) -> Optional[Dict[str, any]]:
        """
        Fetch delivery trend with QUANTITY analysis (smart money detection)
        
        This tracks absolute delivery QUANTITY, not just percentage.
        A spike in delivery quantity indicates institutional accumulation.
        
        Args:
            symbol: Stock symbol
            days: Number of days to analyze (default 90 for 3-month baseline)
            spike_threshold: Multiplier for spike detection (2.0 = 2x normal)
        
        Returns:
            Dictionary with quantity analysis, spike detection, and trend
        """
        clean_symbol = sanitize_symbol(symbol)
        if not clean_symbol:
            logger.debug(f"Invalid symbol: {symbol}")
            return None
        
        # If cache not warmed up, do it now
        if not self._warmup_complete and len(self._cache) < days:
            self.warmup_cache(days=days, max_workers=10)
        
        delivery_data = []
        
        # Fast lookup from cached bhavcopy files
        for cache_key in sorted(self._cache.keys(), reverse=True)[:days]:
            df = self._cache[cache_key]
            if 'symbol' in df.columns:
                symbol_data = df[df['symbol'] == clean_symbol]
                if not symbol_data.empty:
                    delivery_data.append({
                        'date': datetime.strptime(cache_key, "%Y%m%d"),
                        'delivery_percentage': symbol_data.iloc[0].get('delivery_percentage', 0),
                        'delivery_qty': symbol_data.iloc[0].get('delivery_qty', 0),
                        'traded_qty': symbol_data.iloc[0].get('traded_qty', 0)
                    })
        
        if not delivery_data:
            return None
        
        # Extract quantities and percentages
        quantities = [d['delivery_qty'] for d in delivery_data if d['delivery_qty'] > 0]
        percentages = [d['delivery_percentage'] for d in delivery_data if d['delivery_percentage'] > 0]
        
        if not quantities:
            return None
        
        # QUANTITY ANALYSIS (This is the smart money indicator)
        latest_qty = quantities[0]
        avg_qty = sum(quantities) / len(quantities)
        
        # Historical baseline (exclude latest for comparison)
        baseline_qty = sum(quantities[1:]) / len(quantities[1:]) if len(quantities) > 1 else avg_qty
        
        # Spike detection - Is current delivery quantity unusual?
        qty_spike_ratio = latest_qty / baseline_qty if baseline_qty > 0 else 1.0
        has_qty_spike = qty_spike_ratio >= spike_threshold
        
        # Percentage analysis
        latest_pct = percentages[0] if percentages else 0
        avg_pct = sum(percentages) / len(percentages) if percentages else 0
        
        return {
            'symbol': clean_symbol,
            
            # QUANTITY METRICS (Smart money tracking)
            'latest_delivery_qty': latest_qty,
            'avg_delivery_qty': avg_qty,
            'baseline_delivery_qty': baseline_qty,
            'qty_spike_ratio': qty_spike_ratio,
            'has_qty_spike': has_qty_spike,
            
            # PERCENTAGE METRICS (Traditional)
            'latest_delivery_pct': latest_pct,
            'avg_delivery_pct': avg_pct,
            
            # TREND
            'qty_trend': self._calculate_trend([d['delivery_qty'] for d in delivery_data]),
            'pct_trend': self._calculate_trend(percentages),
            
            'data_points': len(delivery_data),
            'lookback_days': days
        }
    
    def _calculate_trend(self, percentages: List[float]) -> str:
        """Calculate delivery percentage trend"""
        if len(percentages) < 2:
            return "insufficient_data"
        
        # Simple linear regression or comparison
        first_half = sum(percentages[:len(percentages)//2]) / (len(percentages)//2)
        second_half = sum(percentages[len(percentages)//2:]) / (len(percentages) - len(percentages)//2)
        
        diff = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
        
        if diff > 5:
            return "rising"
        elif diff < -5:
            return "falling"
        else:
            return "stable"
    
    def _get_previous_trading_day(self) -> datetime:
        """Get the previous trading day (excluding weekends)"""
        current = datetime.now()
        
        # Go back one day
        previous = current - timedelta(days=1)
        
        # Skip weekends
        while previous.weekday() >= 5:  # Saturday = 5, Sunday = 6
            previous -= timedelta(days=1)
        
        return previous
    
    def clear_cache(self):
        """Clear cached delivery data"""
        self._cache.clear()
        logger.info("Delivery data cache cleared")
