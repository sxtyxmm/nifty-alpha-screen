#!/usr/bin/env python3
"""
Test script for Financial Data Automation Assistant
Demonstrates the strategies using sample data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def generate_sample_stock_data(symbol, days=252):
    """Generate sample stock data for testing"""
    np.random.seed(hash(symbol) % 2**32)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate realistic stock prices
    base_price = np.random.uniform(100, 2000)
    trend = np.random.uniform(-0.002, 0.003)
    volatility = np.random.uniform(0.015, 0.03)
    
    prices = [base_price]
    for i in range(1, days):
        change = np.random.normal(trend, volatility)
        prices.append(prices[-1] * (1 + change))
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': prices,
        'High': [p * (1 + np.random.uniform(0, 0.02)) for p in prices],
        'Low': [p * (1 - np.random.uniform(0, 0.02)) for p in prices],
        'Close': prices,
        'Volume': [np.random.randint(1000000, 10000000) for _ in range(days)]
    })
    df.set_index('Date', inplace=True)
    
    return df

def test_strategy1():
    """Test Strategy 1 with sample data"""
    print("Testing Strategy 1: Momentum + Retracement Strategy")
    print("=" * 60)
    
    # Sample stocks
    stocks = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 
              'HINDUNILVR', 'SBIN', 'BHARTIARTL', 'KOTAKBANK', 'ITC',
              'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'HCLTECH']
    
    results = []
    
    for symbol in stocks:
        # Generate sample data
        df = generate_sample_stock_data(symbol, days=252)
        
        # Calculate metrics
        high_52w = df['High'].max()
        current_price = df['Close'].iloc[-1]
        retracement = ((current_price - high_52w) / high_52w) * 100
        
        # 3-month and 6-month returns
        return_3m = ((df['Close'].iloc[-1] - df['Close'].iloc[-63]) / df['Close'].iloc[-63]) * 100
        return_6m = ((df['Close'].iloc[-1] - df['Close'].iloc[-126]) / df['Close'].iloc[-126]) * 100
        
        # Sharpe ratio
        returns = df['Close'].pct_change().dropna()
        sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
        
        # Sortino ratio
        negative_returns = returns[returns < 0]
        sortino = (returns.mean() * 252) / (negative_returns.std() * np.sqrt(252))
        
        # Relative strength (simulated)
        rel_strength = np.random.uniform(-5, 15)
        
        # Combined score
        score = sharpe * 0.3 + sortino * 0.3 + (return_6m / 100) * 0.2 + \
                (return_3m / 100) * 0.1 + (rel_strength / 100) * 0.1
        
        results.append({
            'Symbol': symbol,
            'Retracement_from_52w_high_%': round(retracement, 2),
            'Return_3M_%': round(return_3m, 2),
            'Return_6M_%': round(return_6m, 2),
            'Sharpe_Ratio': round(sharpe, 2),
            'Sortino_Ratio': round(sortino, 2),
            'Relative_Strength_vs_Nifty_%': round(rel_strength, 2),
            'Combined_Score': round(score, 4)
        })
    
    # Sort and rank
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('Combined_Score', ascending=False)
    df_results['Rank'] = range(1, len(df_results) + 1)
    
    cols = ['Rank', 'Symbol', 'Retracement_from_52w_high_%', 'Return_3M_%', 
            'Return_6M_%', 'Sharpe_Ratio', 'Sortino_Ratio', 
            'Relative_Strength_vs_Nifty_%', 'Combined_Score']
    df_results = df_results[cols]
    
    print(df_results.to_string(index=False))
    print(f"\n✓ Generated {len(df_results)} stocks for Strategy 1")
    
    return df_results

def test_strategy2():
    """Test Strategy 2 with sample data"""
    print("\n\nTesting Strategy 2: EMA Retracement Strategy")
    print("=" * 60)
    
    stocks = ['RELIANCE', 'TCS', 'HDFCBANK', 'WIPRO', 'TITAN', 'MARUTI']
    
    results = []
    
    for symbol in stocks:
        # Generate sample data
        df = generate_sample_stock_data(symbol, days=100)
        
        # Calculate 44-day EMA
        df['EMA_44'] = df['Close'].ewm(span=44, adjust=False).mean()
        
        current_price = df['Close'].iloc[-1]
        current_ema = df['EMA_44'].iloc[-1]
        ema_5d_ago = df['EMA_44'].iloc[-6]
        
        # Check if EMA is rising
        if current_ema <= ema_5d_ago:
            continue
        
        # Check if price is near EMA
        distance_pct = ((current_price - current_ema) / current_ema) * 100
        if abs(distance_pct) > 1.0:
            continue
        
        ema_change = ((current_ema - ema_5d_ago) / ema_5d_ago) * 100
        
        results.append({
            'Symbol': symbol,
            'Current_Price': round(current_price, 2),
            'EMA_44': round(current_ema, 2),
            'Distance_from_EMA_%': round(distance_pct, 2),
            'EMA_Change_5d_%': round(ema_change, 2)
        })
    
    df_results = pd.DataFrame(results)
    
    if len(df_results) > 0:
        print(df_results.to_string(index=False))
        print(f"\n✓ Generated {len(df_results)} stocks for Strategy 2")
    else:
        print("No stocks met the criteria (this is expected with random data)")
    
    return df_results

def main():
    """Main test function"""
    print("Financial Data Automation Assistant - Test Mode")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Note: Using sample data for demonstration")
    print("=" * 60)
    print()
    
    # Test both strategies
    results_s1 = test_strategy1()
    results_s2 = test_strategy2()
    
    # Save to CSV
    print("\n" + "=" * 60)
    print("Saving test results to CSV files...")
    
    results_s1.to_csv('test_strategy1_results.csv', index=False)
    print("✓ Strategy 1 test results saved to 'test_strategy1_results.csv'")
    
    if len(results_s2) > 0:
        results_s2.to_csv('test_strategy2_results.csv', index=False)
        print("✓ Strategy 2 test results saved to 'test_strategy2_results.csv'")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
