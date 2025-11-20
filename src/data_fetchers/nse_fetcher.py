#!/usr/bin/env python3
"""
NSE Data Fetcher Module
Automatically fetches NSE stock symbols and delivery data (bhavcopy)
"""

import requests
import pandas as pd
import io
import zipfile
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import time
import json
import os
from pathlib import Path


class NSEDataFetcher:
    """Fetch NSE stock symbols and delivery data."""
    
    # NSE headers to mimic browser - improved headers
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.nseindia.com/'
    }
    
    CACHE_FILE = "data/nse_symbols_cache.json"
    CACHE_TTL_HOURS = 24  # Cache validity: 24 hours
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._cookies_initialized = False
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session by visiting NSE homepage to get cookies."""
        try:
            # Visit homepage first
            response = self.session.get('https://www.nseindia.com', timeout=10, allow_redirects=True)
            time.sleep(2)  # Increased wait time for cookies
            
            # Visit a static page to ensure cookies are set
            self.session.get('https://www.nseindia.com/market-data/live-equity-market', timeout=10)
            time.sleep(1)
            
            self._cookies_initialized = True
        except Exception:
            # Silently continue - will use fallback if APIs fail
            pass
    
    def fetch_all_nse_symbols(self, silent: bool = False, force_refresh: bool = False) -> List[str]:
        """
        Fetch all NSE equity symbols with intelligent caching.
        
        Args:
            silent: If True, suppress error messages
            force_refresh: If True, bypass cache and fetch fresh data
        
        Returns:
            List of stock symbols
        """
        # Try loading from cache first (unless force refresh)
        if not force_refresh:
            cached_symbols = self._load_from_cache(silent)
            if cached_symbols:
                return cached_symbols
        
        # Cache miss or force refresh - fetch from NSE
        symbols = []
        
        # Method 1: Try fetching from NSE equity list
        try:
            symbols = self._fetch_from_equity_list()
            if symbols:
                if not silent:
                    print(f"✓ Fetched {len(symbols)} symbols from NSE equity list")
                self._save_to_cache(symbols)
                return symbols
        except Exception as e:
            if not silent:
                # Only show a simplified message
                pass
        
        # Method 2: Try fetching from market data
        try:
            symbols = self._fetch_from_market_data()
            if symbols:
                if not silent:
                    print(f"✓ Fetched {len(symbols)} symbols from NSE market data")
                self._save_to_cache(symbols)
                return symbols
        except Exception as e:
            if not silent:
                pass
        
        # Method 3: Try loading old cache regardless of age (offline fallback)
        if not force_refresh:
            cached_symbols = self._load_from_cache(silent, ignore_ttl=True)
            if cached_symbols:
                if not silent:
                    print(f"⚠️  NSE unreachable - using cached symbols ({len(cached_symbols)} stocks)")
                return cached_symbols
        
        # Method 4: All methods failed and no cache available
        if not silent:
            print("❌ Unable to fetch NSE symbols (no network and no cache)")
            print("💡 Run with internet once to populate cache")
        
        return []
    
    def _load_from_cache(self, silent: bool = False, ignore_ttl: bool = False) -> Optional[List[str]]:
        """
        Load symbols from cache file if valid.
        
        Args:
            silent: If True, suppress messages
            ignore_ttl: If True, load cache regardless of age (offline mode)
        
        Returns:
            List of symbols or None if cache invalid
        """
        try:
            if not os.path.exists(self.CACHE_FILE):
                return None
            
            with open(self.CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            
            # Validate cache structure
            if 'symbols' not in cache_data or 'last_updated' not in cache_data:
                return None
            
            # Check cache age
            if not ignore_ttl:
                last_updated = datetime.fromisoformat(cache_data['last_updated'])
                age_hours = (datetime.now() - last_updated).total_seconds() / 3600
                
                if age_hours > self.CACHE_TTL_HOURS:
                    if not silent:
                        print(f"ℹ️  Cache expired ({age_hours:.1f}h old, refreshing...)")
                    return None
            
            symbols = cache_data['symbols']
            if not silent:
                age_hours = (datetime.now() - datetime.fromisoformat(cache_data['last_updated'])).total_seconds() / 3600
                print(f"✓ Loaded {len(symbols)} symbols from cache ({age_hours:.1f}h old)")
            
            return symbols
            
        except Exception as e:
            if not silent:
                print(f"⚠️  Cache load failed: {str(e)}")
            return None
    
    def _save_to_cache(self, symbols: List[str]) -> None:
        """
        Save symbols to cache file.
        
        Args:
            symbols: List of symbols to cache
        """
        try:
            # Create data directory if needed
            os.makedirs(os.path.dirname(self.CACHE_FILE), exist_ok=True)
            
            cache_data = {
                'last_updated': datetime.now().isoformat(),
                'symbols': symbols,
                'count': len(symbols),
                'source': 'NSE API'
            }
            
            with open(self.CACHE_FILE, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            # Silently fail - caching is optional
            pass
    
    def _fetch_from_equity_list(self) -> List[str]:
        """Fetch symbols from NSE official equity CSV (most reliable method)."""
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Parse CSV
            lines = response.text.strip().split('\n')
            
            if len(lines) < 2:
                raise Exception("Empty or invalid CSV response")
            
            symbols = []
            for line in lines[1:]:  # Skip header
                parts = line.split(',')
                if len(parts) > 0 and parts[0].strip():
                    symbol = parts[0].strip()
                    # Filter out special characters and ensure valid trading symbols
                    if symbol and symbol.replace('&', '').replace('-', '').isalnum():
                        symbols.append(symbol)
            
            if not symbols:
                raise Exception("No symbols found in CSV")
            
            return symbols
            
        except Exception as e:
            raise Exception(f"Failed to fetch from equity CSV: {str(e)}")
    
    def _fetch_from_market_data(self) -> List[str]:
        """Fetch symbols from NSE derivative (F&O) list CSV."""
        url = "https://www.nseindia.com/api/master-quote"
        
        try:
            # Reinitialize session if needed
            if not self._cookies_initialized:
                self._initialize_session()
                
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            data = response.json()
            symbols = set()
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'symbol' in item:
                        symbol = item['symbol']
                        if symbol and symbol not in ['NIFTY', 'BANKNIFTY', 'NIFTY 50', 'NIFTY BANK']:
                            symbols.add(symbol)
            elif isinstance(data, dict) and 'data' in data:
                for item in data['data']:
                    if 'symbol' in item:
                        symbol = item['symbol']
                        if symbol and symbol not in ['NIFTY', 'BANKNIFTY', 'NIFTY 50', 'NIFTY BANK']:
                            symbols.add(symbol)
            
            if not symbols:
                raise Exception("No symbols found in response")
            
            return list(symbols)
            
        except Exception as e:
            raise Exception(f"Failed to fetch from market data: {str(e)}")
    
    
    def fetch_bhavcopy(self, date: Optional[datetime] = None) -> Optional[pd.DataFrame]:
        """
        Fetch NSE bhavcopy (delivery data) for a specific date.
        
        Args:
            date: Date for which to fetch bhavcopy (defaults to last trading day)
            
        Returns:
            DataFrame with delivery data or None if failed
        """
        if date is None:
            date = self._get_last_trading_day()
        
        # Try multiple methods to fetch bhavcopy
        methods = [
            self._fetch_bhavcopy_from_archives,
            self._fetch_bhavcopy_from_reports,
        ]
        
        for method in methods:
            try:
                df = method(date)
                if df is not None and not df.empty:
                    print(f"✓ Fetched bhavcopy for {date.strftime('%Y-%m-%d')} ({len(df)} records)")
                    return df
            except Exception as e:
                print(f"Bhavcopy fetch method failed: {e}")
                continue
        
        print(f"⚠️  Could not fetch bhavcopy for {date.strftime('%Y-%m-%d')}")
        return None
    
    def _get_last_trading_day(self) -> datetime:
        """Get the last trading day (skip weekends)."""
        today = datetime.now()
        
        # Go back until we find a weekday
        date = today
        while date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            date -= timedelta(days=1)
        
        # If today is a weekday but market might not have closed, go back one day
        if date.date() == today.date() and today.hour < 16:
            date -= timedelta(days=1)
            while date.weekday() >= 5:
                date -= timedelta(days=1)
        
        return date
    
    def _fetch_bhavcopy_from_archives(self, date: datetime) -> Optional[pd.DataFrame]:
        """Fetch bhavcopy from NSE archives (equity bhavcopy)."""
        date_str = date.strftime('%d%m%Y')
        month = date.strftime('%b').upper()
        year = date.strftime('%Y')
        
        # NSE bhavcopy URL format
        filename = f"cm{date_str}bhav.csv.zip"
        url = f"https://archives.nseindia.com/content/historical/EQUITIES/{year}/{month}/{filename}"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Extract CSV from ZIP
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                csv_filename = f"cm{date_str}bhav.csv"
                with z.open(csv_filename) as f:
                    df = pd.read_csv(f)
                    
                    # Filter for EQ series only
                    if 'SERIES' in df.columns:
                        df = df[df['SERIES'] == 'EQ']
                    
                    return df
        except Exception as e:
            raise Exception(f"Archives fetch failed: {e}")
    
    def _fetch_bhavcopy_from_reports(self, date: datetime) -> Optional[pd.DataFrame]:
        """Fetch bhavcopy from NSE reports (delivery positions)."""
        date_str = date.strftime('%d%m%Y')
        month = date.strftime('%b').upper()
        year = date.strftime('%Y')
        
        # Delivery report URL
        filename = f"MTO_{date_str}.DAT"
        url = f"https://archives.nseindia.com/archives/equities/mto/{filename}"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Parse the DAT file (it's actually a CSV)
            df = pd.read_csv(io.StringIO(response.text))
            return df
        except Exception as e:
            raise Exception(f"Reports fetch failed: {e}")
    
    def fetch_multiple_bhavcopy(self, days: int = 3) -> Dict[str, pd.DataFrame]:
        """
        Fetch bhavcopy for multiple days.
        
        Args:
            days: Number of past trading days to fetch
            
        Returns:
            Dictionary mapping date strings to DataFrames
        """
        bhavcopy_data = {}
        current_date = self._get_last_trading_day()
        
        fetched = 0
        attempts = 0
        max_attempts = days * 3  # Try up to 3x the requested days
        
        while fetched < days and attempts < max_attempts:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Skip weekends
            if current_date.weekday() < 5:
                df = self.fetch_bhavcopy(current_date)
                if df is not None:
                    bhavcopy_data[date_str] = df
                    fetched += 1
            
            current_date -= timedelta(days=1)
            attempts += 1
        
        return bhavcopy_data
    
    def get_delivery_data(self, symbol: str, bhavcopy_df: pd.DataFrame) -> Optional[Dict]:
        """
        Extract delivery data for a specific symbol from bhavcopy.
        
        Args:
            symbol: Stock symbol
            bhavcopy_df: Bhavcopy DataFrame
            
        Returns:
            Dictionary with delivery metrics or None
        """
        try:
            # Find the symbol in bhavcopy
            symbol_col = None
            for col in bhavcopy_df.columns:
                if col.upper() in ['SYMBOL', 'SYMB']:
                    symbol_col = col
                    break
            
            if symbol_col is None:
                return None
            
            # Filter for the symbol
            stock_data = bhavcopy_df[bhavcopy_df[symbol_col].str.upper() == symbol.upper()]
            
            if stock_data.empty:
                return None
            
            row = stock_data.iloc[0]
            
            # Extract delivery data (column names vary)
            deliv_qty = None
            traded_qty = None
            deliv_pct = None
            
            # Try different column name variations
            for col in ['DELIV_QTY', 'NO_OF_TRADES', 'QTY_PER_TRADE']:
                if col in bhavcopy_df.columns:
                    deliv_qty = row.get(col)
                    break
            
            for col in ['TTL_TRD_QNTY', 'TOTTRDQTY', 'TRADED_QTY']:
                if col in bhavcopy_df.columns:
                    traded_qty = row.get(col)
                    break
            
            for col in ['DELIV_PER', 'DELIV_PCT', '%DELY QTY TO TRADED QTY']:
                if col in bhavcopy_df.columns:
                    deliv_pct = row.get(col)
                    break
            
            # Calculate delivery percentage if not directly available
            if deliv_pct is None and deliv_qty and traded_qty and traded_qty > 0:
                deliv_pct = (deliv_qty / traded_qty) * 100
            
            if deliv_pct is not None:
                return {
                    'deliverable_qty': deliv_qty,
                    'traded_qty': traded_qty,
                    'delivery_pct': float(deliv_pct)
                }
            
            return None
            
        except Exception as e:
            print(f"Error extracting delivery data for {symbol}: {e}")
            return None


if __name__ == "__main__":
    # Test the fetcher
    fetcher = NSEDataFetcher()
    
    print("Testing NSE Data Fetcher")
    print("=" * 80)
    
    # Test symbol fetching
    print("\n1. Fetching NSE symbols...")
    symbols = fetcher.fetch_all_nse_symbols()
    print(f"   Total symbols: {len(symbols)}")
    print(f"   Sample: {symbols[:10]}")
    
    # Test bhavcopy fetching
    print("\n2. Fetching bhavcopy...")
    bhavcopy = fetcher.fetch_bhavcopy()
    if bhavcopy is not None:
        print(f"   Rows: {len(bhavcopy)}")
        print(f"   Columns: {list(bhavcopy.columns)}")
        
        # Test delivery data extraction
        if symbols:
            print(f"\n3. Testing delivery data extraction for {symbols[0]}...")
            delivery = fetcher.get_delivery_data(symbols[0], bhavcopy)
            if delivery:
                print(f"   Delivery %: {delivery['delivery_pct']:.2f}%")
