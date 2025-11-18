#!/usr/bin/env python3
"""
Stock Data Pipeline
Comprehensive data fetching and analysis for all NSE stocks
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from nse_data_fetcher import NSEDataFetcher


class StockDataPipeline:
    """Complete data pipeline for NSE stock analysis."""
    
    def __init__(self, symbols: Optional[List[str]] = None, max_workers: int = 10):
        """
        Initialize the pipeline.
        
        Args:
            symbols: List of stock symbols (if None, will auto-fetch)
            max_workers: Number of parallel workers for data fetching
        """
        self.nse_fetcher = NSEDataFetcher()
        
        if symbols is None:
            print("Auto-fetching NSE symbols...")
            symbols = self.nse_fetcher.fetch_all_nse_symbols()
        
        self.symbols = symbols
        self.max_workers = max_workers
        self.stock_data = pd.DataFrame()
        self.bhavcopy_data = {}
        
    def fetch_all_data(self, use_delivery: bool = True) -> pd.DataFrame:
        """
        Fetch all data for all symbols.
        
        Args:
            use_delivery: Whether to fetch delivery data
            
        Returns:
            DataFrame with all stock data and scores
        """
        print(f"\n{'='*80}")
        print(f"Starting data pipeline for {len(self.symbols)} stocks...")
        print(f"{'='*80}\n")
        
        # Fetch bhavcopy data if needed
        if use_delivery:
            print("Step 1: Fetching NSE delivery data (bhavcopy)...")
            self.bhavcopy_data = self.nse_fetcher.fetch_multiple_bhavcopy(days=3)
            print(f"✓ Fetched bhavcopy for {len(self.bhavcopy_data)} days\n")
        
        # Fetch stock data in parallel
        print("Step 2: Fetching fundamentals and price data...")
        all_stock_data = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self._fetch_stock_data, symbol): symbol 
                for symbol in self.symbols
            }
            
            completed = 0
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    stock_data = future.result()
                    if stock_data is not None:
                        all_stock_data.append(stock_data)
                    
                    completed += 1
                    if completed % 10 == 0:
                        print(f"   Progress: {completed}/{len(self.symbols)} stocks processed...")
                        
                except Exception as e:
                    print(f"   Error processing {symbol}: {e}")
        
        print(f"✓ Completed: {len(all_stock_data)} stocks successfully processed\n")
        
        # Create DataFrame
        if all_stock_data:
            self.stock_data = pd.DataFrame(all_stock_data)
            
            # Calculate scores
            print("Step 3: Calculating scores and signals...")
            self.stock_data = self._calculate_scores(self.stock_data)
            print(f"✓ Scores calculated\n")
            
            # Sort by score
            self.stock_data = self.stock_data.sort_values('score', ascending=False)
            
            return self.stock_data
        else:
            return pd.DataFrame()
    
    def _fetch_stock_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch all data for a single stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with all stock data
        """
        try:
            # Add .NS suffix for NSE
            ticker_symbol = f"{symbol}.NS"
            ticker = yf.Ticker(ticker_symbol)
            
            # Fetch info
            info = ticker.info
            
            # Fetch price history
            hist = ticker.history(period='1y')
            
            if hist.empty:
                return None
            
            # Calculate EMA-44
            hist['EMA_44'] = hist['Close'].ewm(span=44, adjust=False).mean()
            
            current_price = hist['Close'].iloc[-1]
            ema_44 = hist['EMA_44'].iloc[-1]
            
            # Calculate EMA slope (5-day change)
            if len(hist) >= 6:
                ema_5_days_ago = hist['EMA_44'].iloc[-6]
                ema_slope = (ema_44 - ema_5_days_ago) / ema_5_days_ago * 100
            else:
                ema_slope = 0
            
            # Get delivery data
            delivery_pct = None
            delivery_trend = None
            
            if self.bhavcopy_data:
                # Get latest bhavcopy
                latest_date = sorted(self.bhavcopy_data.keys())[-1]
                bhavcopy_df = self.bhavcopy_data[latest_date]
                
                delivery_data = self.nse_fetcher.get_delivery_data(symbol, bhavcopy_df)
                if delivery_data:
                    delivery_pct = delivery_data['delivery_pct']
                
                # Calculate 3-day trend if we have multiple days
                if len(self.bhavcopy_data) >= 2:
                    delivery_trend = self._calculate_delivery_trend(symbol)
            
            # Compile stock data
            stock_data = {
                'symbol': symbol,
                'company_name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'current_price': current_price,
                'market_cap': info.get('marketCap'),
                'pe_trailing': info.get('trailingPE'),
                'pe_forward': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'debt_to_equity': info.get('debtToEquity'),
                'roe': info.get('returnOnEquity'),
                'beta': info.get('beta'),
                'ema_44': ema_44,
                'ema_slope': ema_slope,
                'price_vs_ema': 'ABOVE' if current_price > ema_44 else 'BELOW',
                'price_ema_pct': ((current_price - ema_44) / ema_44) * 100,
                'delivery_pct': delivery_pct,
                'delivery_trend': delivery_trend,
            }
            
            return stock_data
            
        except Exception as e:
            # Silently skip errors for individual stocks
            return None
    
    def _calculate_delivery_trend(self, symbol: str) -> str:
        """Calculate 3-day delivery trend."""
        try:
            delivery_pcts = []
            
            for date in sorted(self.bhavcopy_data.keys()):
                df = self.bhavcopy_data[date]
                delivery_data = self.nse_fetcher.get_delivery_data(symbol, df)
                if delivery_data:
                    delivery_pcts.append(delivery_data['delivery_pct'])
            
            if len(delivery_pcts) >= 2:
                if delivery_pcts[-1] > delivery_pcts[0] * 1.05:
                    return 'rising'
                elif delivery_pcts[-1] < delivery_pcts[0] * 0.95:
                    return 'falling'
                else:
                    return 'flat'
            
            return 'insufficient_data'
        except:
            return 'insufficient_data'
    
    def _calculate_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate comprehensive scores for all stocks.
        Score range: -5 to +5
        
        Components:
        - EMA trend (0 to +2)
        - EMA slope (-1 to +1)
        - Fundamentals (-2 to +2)
        - Delivery % (0 to +2)
        - Delivery trend (0 or +1)
        """
        scores = []
        signals = []
        
        for idx, row in df.iterrows():
            score = 0
            breakdown = []
            
            # 1. EMA Trend Score (0 to +2)
            if pd.notna(row['current_price']) and pd.notna(row['ema_44']):
                if row['price_vs_ema'] == 'ABOVE':
                    pct_above = row['price_ema_pct']
                    if pct_above > 5:
                        score += 2
                        breakdown.append('EMA:+2(>5%)')
                    else:
                        score += 1
                        breakdown.append('EMA:+1')
                else:
                    breakdown.append('EMA:0(below)')
            
            # 2. EMA Slope Score (-1 to +1)
            if pd.notna(row['ema_slope']):
                if row['ema_slope'] > 2:
                    score += 1
                    breakdown.append('Slope:+1')
                elif row['ema_slope'] < -2:
                    score -= 1
                    breakdown.append('Slope:-1')
                else:
                    breakdown.append('Slope:0')
            
            # 3. Fundamentals Score (-2 to +2)
            fund_score = 0
            
            # PE ratio check
            if pd.notna(row['pe_trailing']):
                if 0 < row['pe_trailing'] < 20:
                    fund_score += 1
                elif row['pe_trailing'] > 40:
                    fund_score -= 1
            
            # ROE check
            if pd.notna(row['roe']):
                roe_pct = row['roe'] * 100
                if roe_pct > 15:
                    fund_score += 1
                elif roe_pct < 0:
                    fund_score -= 1
            
            # Debt check
            if pd.notna(row['debt_to_equity']):
                if row['debt_to_equity'] < 0.5:
                    fund_score += 0.5
                elif row['debt_to_equity'] > 2:
                    fund_score -= 0.5
            
            score += fund_score
            breakdown.append(f'Fund:{fund_score:+.1f}')
            
            # 4. Delivery % Score (0 to +2)
            if pd.notna(row['delivery_pct']):
                if row['delivery_pct'] > 50:
                    score += 2
                    breakdown.append('Deliv:+2')
                elif row['delivery_pct'] > 35:
                    score += 1
                    breakdown.append('Deliv:+1')
                else:
                    breakdown.append('Deliv:0')
            else:
                breakdown.append('Deliv:N/A')
            
            # 5. Delivery Trend Score (0 or +1)
            if row['delivery_trend'] == 'rising':
                score += 1
                breakdown.append('Trend:+1')
            else:
                breakdown.append(f"Trend:0({row['delivery_trend']})")
            
            # Cap score between -5 and +5
            score = max(-5, min(5, score))
            
            # Determine signal
            if score >= 3:
                signal = 'BUY'
            elif score >= 1:
                signal = 'HOLD'
            else:
                signal = 'AVOID'
            
            scores.append(score)
            signals.append(signal)
        
        df['score'] = scores
        df['signal'] = signals
        
        return df
    
    def get_top_buys(self, n: int = 20) -> pd.DataFrame:
        """Get top N BUY signals."""
        if self.stock_data.empty:
            return pd.DataFrame()
        
        buy_stocks = self.stock_data[self.stock_data['signal'] == 'BUY']
        return buy_stocks.head(n)
    
    def export_to_csv(self, filename: str = 'stock_analysis.csv'):
        """Export analysis to CSV."""
        if not self.stock_data.empty:
            self.stock_data.to_csv(filename, index=False)
            print(f"✓ Data exported to {filename}")
    
    def export_to_excel(self, filename: str = 'stock_analysis.xlsx'):
        """Export analysis to Excel with formatting."""
        if not self.stock_data.empty:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # All stocks sheet
                self.stock_data.to_excel(writer, sheet_name='All Stocks', index=False)
                
                # BUY signals sheet
                buy_stocks = self.stock_data[self.stock_data['signal'] == 'BUY']
                buy_stocks.to_excel(writer, sheet_name='BUY Signals', index=False)
                
                # HOLD signals sheet
                hold_stocks = self.stock_data[self.stock_data['signal'] == 'HOLD']
                hold_stocks.to_excel(writer, sheet_name='HOLD Signals', index=False)
            
            print(f"✓ Data exported to {filename}")


if __name__ == "__main__":
    # Test the pipeline
    print("Testing Stock Data Pipeline")
    print("=" * 80)
    
    # Use a small subset for testing
    test_symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
    
    pipeline = StockDataPipeline(symbols=test_symbols, max_workers=5)
    
    # Fetch all data
    df = pipeline.fetch_all_data(use_delivery=True)
    
    if not df.empty:
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(df[['symbol', 'current_price', 'price_vs_ema', 'ema_slope', 
                  'delivery_pct', 'score', 'signal']].to_string(index=False))
        
        print(f"\nTop BUY signals:")
        top_buys = pipeline.get_top_buys(5)
        if not top_buys.empty:
            print(top_buys[['symbol', 'current_price', 'score', 'signal']].to_string(index=False))
