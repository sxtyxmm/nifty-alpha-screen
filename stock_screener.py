#!/usr/bin/env python3
"""
Financial Data Automation Assistant
Fetches and filters stock data based on two independent trading strategies
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StockDataFetcher:
    """Handles fetching stock data from NSE"""
    
    def __init__(self, stock_universe='nifty200'):
        """
        Initialize the stock data fetcher
        
        Args:
            stock_universe: 'nifty200' or 'nifty500'
        """
        self.stock_universe = stock_universe
        self.nifty_stocks = []
        
    def get_nifty_stocks(self):
        """
        Get list of Nifty 200 or Nifty 500 stocks
        Returns list of stock symbols with .NS suffix for NSE
        """
        # Nifty 200 stocks (top 200 companies by market cap)
        # This is a representative list of major Nifty 200 stocks
        nifty200_stocks = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR', 'ICICIBANK', 'SBIN',
            'BHARTIARTL', 'KOTAKBANK', 'ITC', 'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI',
            'HCLTECH', 'BAJFINANCE', 'WIPRO', 'ULTRACEMCO', 'TITAN', 'SUNPHARMA',
            'NESTLEIND', 'ONGC', 'NTPC', 'TATASTEEL', 'TECHM', 'POWERGRID', 'M&M',
            'BAJAJFINSV', 'ADANIPORTS', 'COALINDIA', 'JSWSTEEL', 'TATAMOTORS', 'HINDALCO',
            'INDUSINDBK', 'DIVISLAB', 'CIPLA', 'DRREDDY', 'GRASIM', 'EICHERMOT',
            'BRITANNIA', 'APOLLOHOSP', 'BPCL', 'HEROMOTOCO', 'UPL', 'BAJAJ-AUTO',
            'TATACONSUM', 'SBILIFE', 'ADANIENT', 'LTIM', 'HDFCLIFE', 'VEDL',
            'DABUR', 'GODREJCP', 'HAVELLS', 'PIDILITIND', 'BERGEPAINT', 'PAGEIND',
            'SIEMENS', 'AMBUJACEM', 'DLF', 'GAIL', 'ICICIPRULI', 'CHOLAFIN',
            'MARICO', 'BANDHANBNK', 'SHREECEM', 'TORNTPHARM', 'COLPAL', 'MUTHOOTFIN',
            'BAJAJHLDNG', 'ALKEM', 'INDIGO', 'BOSCHLTD', 'MOTHERSON', 'LUPIN',
            'NAUKRI', 'SBICARD', 'PIIND', 'AUROPHARMA', 'MAXHEALTH', 'JINDALSTEL',
            'LICI', 'TATAPOWER', 'PFC', 'RECLTD', 'SAIL', 'NMDC', 'BEL',
            'HINDZINC', 'CANBK', 'BANKBARODA', 'IOC', 'PNB', 'IRCTC', 'ZOMATO',
            'OFSS', 'PERSISTENT', 'MPHASIS', 'COFORGE', 'BIOCON', 'TORNTPOWER',
            'ABB', 'POLYCAB', 'TATAELXSI', 'CHAMBLFERT', 'ACC', 'DMART', 'LAURUSLABS',
            'MCDOWELL-N', 'GODREJPROP', 'ASHOKLEY', 'INDUSTOWER', 'CONCOR', 'TRENT',
            'LICHSGFIN', 'IDFCFIRSTB', 'FEDERALBNK', 'AUBANK', 'ABBOTINDIA', 'METROPOLIS',
            'TIINDIA', 'ASTRAL', 'CUMMINSIND', 'VOLTAS', 'BATAINDIA', 'ATUL',
            'IDEA', 'GMRINFRA', 'PEL', 'TVSMOTOR', 'MRF', 'ESCORTS', 'CROMPTON',
            'OBEROIRLTY', 'PRESTIGE', 'UNITDSPR', 'SUPREMEIND', 'KANSAINER', 'WHIRLPOOL',
            'MANYAVAR', 'JKCEMENT', 'JSWENERGY', 'ADANIGREEN', 'ADANIPOWER', 'ADANITRANS',
            'VEDL', 'RAMCOCEM', 'HONAUT', 'BALKRISIND', 'SRF', 'AARTIIND',
            'STAR', 'ABFRL', 'INDHOTEL', 'NATIONALUM', 'NAVINFLUOR', 'TATACHEM',
            'GRAPHITE', 'JUBLFOOD', 'DEEPAKNTR', 'CLEAN', 'LTTS', 'COROMANDEL',
            'PETRONET', 'HINDPETRO', 'UCOBANK', 'UNIONBANK', 'ZEEL', 'DIXON',
            'SYNGENE', 'LALPATHLAB', 'FLUOROCHEM', 'SONACOMS', 'SKFINDIA', 'GRINDWELL'
        ]
        
        # Add .NS suffix for NSE stocks
        self.nifty_stocks = [f"{stock}.NS" for stock in nifty200_stocks]
        return self.nifty_stocks
    
    def fetch_stock_data(self, symbol, period='1y'):
        """
        Fetch historical data for a stock
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            period: Time period ('1y', '2y', etc.)
        
        Returns:
            DataFrame with historical stock data
        """
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def fetch_nifty_index_data(self, period='1y'):
        """
        Fetch Nifty 50 index data for comparison
        
        Returns:
            DataFrame with Nifty index data
        """
        try:
            nifty = yf.Ticker("^NSEI")
            df = nifty.history(period=period)
            return df
        except Exception as e:
            print(f"Error fetching Nifty index data: {e}")
            return None


class Strategy1:
    """Momentum + Retracement Strategy"""
    
    def __init__(self, fetcher):
        self.fetcher = fetcher
        self.results = []
    
    def calculate_retracement_from_52w_high(self, df):
        """
        Calculate retracement from 52-week high
        
        Returns:
            Retracement percentage (negative value means below high)
        """
        if df is None or len(df) < 252:  # Need at least 1 year of data
            return None
        
        # Get 52-week high
        high_52w = df['High'].tail(252).max()
        current_price = df['Close'].iloc[-1]
        
        # Calculate retracement
        retracement = ((current_price - high_52w) / high_52w) * 100
        return retracement
    
    def calculate_returns(self, df, months):
        """
        Calculate returns over specified months
        
        Args:
            df: Stock price DataFrame
            months: Number of months (3 or 6)
        
        Returns:
            Return percentage
        """
        if df is None or len(df) < months * 21:  # Approximate trading days
            return None
        
        days = months * 21
        past_price = df['Close'].iloc[-days]
        current_price = df['Close'].iloc[-1]
        
        return ((current_price - past_price) / past_price) * 100
    
    def calculate_sharpe_ratio(self, df, risk_free_rate=0.06):
        """
        Calculate Sharpe ratio (annualized)
        
        Args:
            df: Stock price DataFrame
            risk_free_rate: Annual risk-free rate (default 6%)
        
        Returns:
            Sharpe ratio
        """
        if df is None or len(df) < 60:
            return None
        
        # Calculate daily returns
        returns = df['Close'].pct_change().dropna()
        
        # Annualize
        avg_return = returns.mean() * 252
        std_return = returns.std() * np.sqrt(252)
        
        if std_return == 0:
            return None
        
        sharpe = (avg_return - risk_free_rate) / std_return
        return sharpe
    
    def calculate_sortino_ratio(self, df, risk_free_rate=0.06):
        """
        Calculate Sortino ratio (annualized)
        
        Args:
            df: Stock price DataFrame
            risk_free_rate: Annual risk-free rate
        
        Returns:
            Sortino ratio
        """
        if df is None or len(df) < 60:
            return None
        
        # Calculate daily returns
        returns = df['Close'].pct_change().dropna()
        
        # Calculate downside deviation
        negative_returns = returns[returns < 0]
        downside_std = negative_returns.std() * np.sqrt(252)
        
        if downside_std == 0 or pd.isna(downside_std):
            return None
        
        avg_return = returns.mean() * 252
        sortino = (avg_return - risk_free_rate) / downside_std
        return sortino
    
    def calculate_relative_strength(self, stock_df, nifty_df, months=6):
        """
        Calculate relative strength vs Nifty index
        
        Returns:
            Outperformance percentage
        """
        if stock_df is None or nifty_df is None:
            return None
        
        days = months * 21
        
        if len(stock_df) < days or len(nifty_df) < days:
            return None
        
        # Calculate stock return
        stock_return = ((stock_df['Close'].iloc[-1] - stock_df['Close'].iloc[-days]) / 
                       stock_df['Close'].iloc[-days]) * 100
        
        # Calculate Nifty return
        nifty_return = ((nifty_df['Close'].iloc[-1] - nifty_df['Close'].iloc[-days]) / 
                       nifty_df['Close'].iloc[-days]) * 100
        
        # Relative strength = stock return - nifty return
        return stock_return - nifty_return
    
    def run(self):
        """
        Execute Strategy 1: Momentum + Retracement Strategy
        
        Returns:
            DataFrame with top 20 stocks
        """
        print("Running Strategy 1: Momentum + Retracement Strategy")
        print("=" * 60)
        
        stocks = self.fetcher.get_nifty_stocks()
        nifty_data = self.fetcher.fetch_nifty_index_data(period='1y')
        
        if nifty_data is None:
            print("Error: Could not fetch Nifty index data")
            return pd.DataFrame()
        
        results = []
        
        for i, symbol in enumerate(stocks):
            print(f"Processing {i+1}/{len(stocks)}: {symbol}")
            
            # Fetch stock data
            df = self.fetcher.fetch_stock_data(symbol, period='1y')
            
            if df is None or len(df) < 252:
                continue
            
            # 1. Calculate retracement from 52-week high
            retracement = self.calculate_retracement_from_52w_high(df)
            if retracement is None or retracement < -30:  # More than 30% down
                continue
            
            # 2. Calculate 3-month and 6-month returns
            return_3m = self.calculate_returns(df, 3)
            return_6m = self.calculate_returns(df, 6)
            
            # Filter for positive returns
            if return_3m is None or return_6m is None:
                continue
            if return_3m <= 0 or return_6m <= 0:
                continue
            
            # 3. Calculate Sharpe and Sortino ratios
            sharpe = self.calculate_sharpe_ratio(df)
            sortino = self.calculate_sortino_ratio(df)
            
            # 4. Calculate relative strength vs Nifty
            rel_strength = self.calculate_relative_strength(df, nifty_data, months=6)
            
            # Only keep stocks that outperformed Nifty
            if rel_strength is None or rel_strength <= 0:
                continue
            
            # Calculate combined score
            # Weighted score: Sharpe (30%), Sortino (30%), 6m return (20%), 
            # 3m return (10%), relative strength (10%)
            score = 0
            if sharpe is not None:
                score += sharpe * 0.3
            if sortino is not None:
                score += sortino * 0.3
            if return_6m is not None:
                score += (return_6m / 100) * 0.2
            if return_3m is not None:
                score += (return_3m / 100) * 0.1
            if rel_strength is not None:
                score += (rel_strength / 100) * 0.1
            
            results.append({
                'Symbol': symbol.replace('.NS', ''),
                'Retracement_from_52w_high_%': round(retracement, 2),
                'Return_3M_%': round(return_3m, 2),
                'Return_6M_%': round(return_6m, 2),
                'Sharpe_Ratio': round(sharpe, 2) if sharpe else None,
                'Sortino_Ratio': round(sortino, 2) if sortino else None,
                'Relative_Strength_vs_Nifty_%': round(rel_strength, 2),
                'Combined_Score': round(score, 4)
            })
        
        # Convert to DataFrame and rank
        df_results = pd.DataFrame(results)
        
        if len(df_results) == 0:
            print("No stocks met the criteria")
            return df_results
        
        # Sort by combined score and select top 20
        df_results = df_results.sort_values('Combined_Score', ascending=False).head(20)
        df_results['Rank'] = range(1, len(df_results) + 1)
        
        # Reorder columns
        cols = ['Rank', 'Symbol'] + [col for col in df_results.columns if col not in ['Rank', 'Symbol']]
        df_results = df_results[cols]
        
        print(f"\nFound {len(df_results)} stocks for Strategy 1")
        return df_results


class Strategy2:
    """EMA Retracement Strategy"""
    
    def __init__(self, fetcher):
        self.fetcher = fetcher
        self.results = []
    
    def calculate_ema(self, prices, period=44):
        """
        Calculate Exponential Moving Average
        
        Args:
            prices: Series of prices
            period: EMA period (default 44)
        
        Returns:
            Series with EMA values
        """
        return prices.ewm(span=period, adjust=False).mean()
    
    def is_ema_rising(self, ema_series, lookback=5):
        """
        Check if EMA is rising (current > 5 days ago)
        
        Args:
            ema_series: Series of EMA values
            lookback: Number of days to look back (default 5)
        
        Returns:
            Boolean
        """
        if len(ema_series) < lookback + 1:
            return False
        
        current_ema = ema_series.iloc[-1]
        past_ema = ema_series.iloc[-(lookback + 1)]
        
        return current_ema > past_ema
    
    def is_price_near_ema(self, current_price, current_ema, tolerance=0.01):
        """
        Check if price is near EMA (within ±1%)
        
        Args:
            current_price: Current stock price
            current_ema: Current EMA value
            tolerance: Tolerance percentage (default 0.01 for 1%)
        
        Returns:
            Boolean
        """
        lower_bound = current_ema * (1 - tolerance)
        upper_bound = current_ema * (1 + tolerance)
        
        return lower_bound <= current_price <= upper_bound
    
    def run(self):
        """
        Execute Strategy 2: EMA Retracement Strategy
        
        Returns:
            DataFrame with qualifying stocks
        """
        print("\nRunning Strategy 2: EMA Retracement Strategy")
        print("=" * 60)
        
        stocks = self.fetcher.get_nifty_stocks()
        results = []
        
        for i, symbol in enumerate(stocks):
            print(f"Processing {i+1}/{len(stocks)}: {symbol}")
            
            # Fetch stock data (need more data for EMA calculation)
            df = self.fetcher.fetch_stock_data(symbol, period='6mo')
            
            if df is None or len(df) < 50:  # Need enough data for 44-day EMA
                continue
            
            # Calculate 44-day EMA
            df['EMA_44'] = self.calculate_ema(df['Close'], period=44)
            
            # Check if EMA is rising
            if not self.is_ema_rising(df['EMA_44'], lookback=5):
                continue
            
            # Check if current price is near EMA (within ±1%)
            current_price = df['Close'].iloc[-1]
            current_ema = df['EMA_44'].iloc[-1]
            
            if not self.is_price_near_ema(current_price, current_ema, tolerance=0.01):
                continue
            
            # Calculate distance from EMA as percentage
            distance_pct = ((current_price - current_ema) / current_ema) * 100
            
            # Get EMA value from 5 days ago for context
            ema_5d_ago = df['EMA_44'].iloc[-6] if len(df) >= 6 else None
            ema_change = ((current_ema - ema_5d_ago) / ema_5d_ago * 100) if ema_5d_ago else None
            
            results.append({
                'Symbol': symbol.replace('.NS', ''),
                'Current_Price': round(current_price, 2),
                'EMA_44': round(current_ema, 2),
                'Distance_from_EMA_%': round(distance_pct, 2),
                'EMA_Change_5d_%': round(ema_change, 2) if ema_change else None
            })
        
        # Convert to DataFrame
        df_results = pd.DataFrame(results)
        
        print(f"\nFound {len(df_results)} stocks for Strategy 2")
        return df_results


def main():
    """Main function to run both strategies and save results"""
    
    print("Financial Data Automation Assistant")
    print("=" * 60)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Initialize fetcher with Nifty 200
    fetcher = StockDataFetcher(stock_universe='nifty200')
    
    # Run Strategy 1
    strategy1 = Strategy1(fetcher)
    results_s1 = strategy1.run()
    
    # Run Strategy 2
    strategy2 = Strategy2(fetcher)
    results_s2 = strategy2.run()
    
    # Save results to CSV
    print("\n" + "=" * 60)
    print("Saving results to CSV files...")
    
    if len(results_s1) > 0:
        results_s1.to_csv('strategy1_momentum_retracement.csv', index=False)
        print(f"✓ Strategy 1 results saved to 'strategy1_momentum_retracement.csv'")
        print(f"  Top 20 stocks (Momentum + Retracement):")
        print(results_s1[['Rank', 'Symbol', 'Combined_Score', 'Return_6M_%']].to_string(index=False))
    else:
        print("✗ No results for Strategy 1")
    
    print()
    
    if len(results_s2) > 0:
        results_s2.to_csv('strategy2_ema_retracement.csv', index=False)
        print(f"✓ Strategy 2 results saved to 'strategy2_ema_retracement.csv'")
        print(f"  Stocks meeting EMA criteria: {len(results_s2)}")
        print(results_s2[['Symbol', 'Current_Price', 'EMA_44', 'Distance_from_EMA_%']].to_string(index=False))
    else:
        print("✗ No results for Strategy 2")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
