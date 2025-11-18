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


class NSEDataFetcher:
    """Fetch NSE stock symbols and delivery data."""
    
    # NSE headers to mimic browser
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session by visiting NSE homepage to get cookies."""
        try:
            self.session.get('https://www.nseindia.com', timeout=10)
            time.sleep(1)  # Give time for cookies to set
        except Exception as e:
            print(f"Warning: Could not initialize NSE session: {e}")
    
    def fetch_all_nse_symbols(self) -> List[str]:
        """
        Fetch all NSE equity symbols.
        
        Returns:
            List of stock symbols
        """
        symbols = []
        
        # Method 1: Try fetching from NSE equity list
        try:
            symbols = self._fetch_from_equity_list()
            if symbols:
                print(f"✓ Fetched {len(symbols)} symbols from NSE equity list")
                return symbols
        except Exception as e:
            print(f"Method 1 failed: {e}")
        
        # Method 2: Try fetching from market data
        try:
            symbols = self._fetch_from_market_data()
            if symbols:
                print(f"✓ Fetched {len(symbols)} symbols from NSE market data")
                return symbols
        except Exception as e:
            print(f"Method 2 failed: {e}")
        
        # Method 3: Fallback to hardcoded popular stocks
        print("⚠️  Using fallback list of popular NSE stocks")
        symbols = self._get_fallback_symbols()
        
        return symbols
    
    def _fetch_from_equity_list(self) -> List[str]:
        """Fetch symbols from NSE equity list API."""
        url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            symbols = []
            if 'data' in data:
                for item in data['data']:
                    if 'symbol' in item:
                        symbols.append(item['symbol'])
            
            return symbols
        except Exception as e:
            raise Exception(f"Failed to fetch from equity list: {e}")
    
    def _fetch_from_market_data(self) -> List[str]:
        """Fetch symbols from NSE market data."""
        url = "https://www.nseindia.com/api/allIndices"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            symbols = set()
            if 'data' in data:
                for item in data['data']:
                    if 'symbol' in item and item['symbol'] not in ['NIFTY 50', 'NIFTY BANK']:
                        symbols.add(item['symbol'])
            
            return list(symbols)
        except Exception as e:
            raise Exception(f"Failed to fetch from market data: {e}")
    
    def _get_fallback_symbols(self) -> List[str]:
        """Return a curated list of popular NSE stocks as fallback."""
        return [
            # Nifty 50 stocks
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
            'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
            'LT', 'BAJFINANCE', 'ASIANPAINT', 'AXISBANK', 'MARUTI',
            'HCLTECH', 'WIPRO', 'TITAN', 'ULTRACEMCO', 'NESTLEIND',
            'SUNPHARMA', 'BAJAJFINSV', 'ADANIENT', 'ONGC', 'NTPC',
            'TATAMOTORS', 'POWERGRID', 'TATASTEEL', 'M&M', 'TECHM',
            'COALINDIA', 'JSWSTEEL', 'INDUSINDBK', 'DRREDDY', 'GRASIM',
            'BRITANNIA', 'APOLLOHOSP', 'ADANIPORTS', 'CIPLA', 'DIVISLAB',
            'EICHERMOT', 'BPCL', 'HINDALCO', 'SHREECEM', 'HEROMOTOCO',
            'BAJAJ-AUTO', 'TATACONSUM', 'UPL', 'SBILIFE', 'HDFCLIFE',
            
            # Additional popular stocks
            'VEDL', 'SAIL', 'ZEEL', 'DLF', 'GODREJCP',
            'PIDILITIND', 'MUTHOOTFIN', 'ADANIPOWER', 'TATAPOWER', 'PNB',
            'BANKBARODA', 'CANBK', 'IOC', 'CHOLAFIN', 'RECLTD',
            'PFC', 'IRCTC', 'ADANIGREEN', 'PAGEIND', 'HAVELLS',
            'BOSCHLTD', 'ABB', 'SIEMENS', 'TORNTPHARM', 'LUPIN',
            'AUROPHARMA', 'BIOCON', 'CADILAHC', 'GLENMARK', 'ALKEM',
            'IBULHSGFIN', 'LICHSGFIN', 'M&MFIN', 'BANDHANBNK', 'IDFCFIRSTB',
            'RBLBANK', 'FEDERALBNK', 'IDFC', 'INDUSTOWER', 'BHARATFORG',
            'VOLTAS', 'NMDC', 'AMBUJACEM', 'ACC', 'GAIL',
            'PETRONET', 'INDIGO', 'DABUR', 'MARICO', 'COLPAL',
        ]
    
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
