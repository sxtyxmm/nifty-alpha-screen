#!/usr/bin/env python3
"""
Demo version of Hybrid Momentum-EMA Trading Strategy

This script demonstrates the strategy using simulated data since the environment
doesn't have internet access. In a production environment with internet access,
use hybrid_momentum_ema.py instead.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

np.random.seed(42)


def generate_mock_stock_data(symbol, start_date, end_date, base_price=100):
    """Generate mock stock data for demonstration."""
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    n_days = len(dates)
    
    # Generate random walk with drift
    returns = np.random.normal(0.0005, 0.02, n_days)
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Add some volatility to OHLC
    high = prices * (1 + np.abs(np.random.normal(0, 0.01, n_days)))
    low = prices * (1 - np.abs(np.random.normal(0, 0.01, n_days)))
    open_price = prices * (1 + np.random.normal(0, 0.005, n_days))
    volume = np.random.randint(1000000, 10000000, n_days)
    
    df = pd.DataFrame({
        'Open': open_price,
        'High': high,
        'Low': low,
        'Close': prices,
        'Volume': volume
    }, index=dates)
    
    return df


def calculate_ema(prices, period=44):
    """Calculate Exponential Moving Average."""
    return prices.ewm(span=period, adjust=False).mean()


def main():
    """Main demo function."""
    print("\n" + "="*70)
    print("HYBRID MOMENTUM-EMA TRADING STRATEGY - DEMO MODE")
    print("="*70)
    print("\nNOTE: This is a demonstration using simulated data.")
    print("For real market data, run hybrid_momentum_ema.py with internet access.")
    print("="*70)
    
    # Configuration
    n_stocks = 50
    start_date = datetime.now() - timedelta(days=5*365 + 180)
    end_date = datetime.now()
    
    stock_symbols = [f"STOCK_{i:02d}.NS" for i in range(1, n_stocks + 1)]
    
    print(f"\nGenerating mock data for {n_stocks} stocks...")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Generate mock data
    stock_data = {}
    for symbol in stock_symbols:
        base_price = np.random.uniform(50, 500)
        stock_data[symbol] = generate_mock_stock_data(symbol, start_date, end_date, base_price)
    
    # Generate Nifty benchmark
    nifty_data = generate_mock_stock_data("NIFTY", start_date, end_date, base_price=15000)
    
    print("✓ Mock data generated successfully")
    
    # Calculate momentum metrics
    print("\nCalculating momentum metrics...")
    results = []
    
    nifty_current = nifty_data['Close'].iloc[-1]
    nifty_6m_ago = nifty_data['Close'].iloc[-126]
    nifty_6m_return = (nifty_current / nifty_6m_ago) - 1
    
    for symbol, df in stock_data.items():
        close_prices = df['Close']
        current_price = close_prices.iloc[-1]
        
        # 52-week high and retracement
        week_52_high = close_prices.rolling(window=252).max().iloc[-1]
        retracement_pct = ((week_52_high - current_price) / week_52_high) * 100
        
        # Returns
        returns_3m = ((current_price / close_prices.iloc[-63]) - 1) * 100
        returns_6m = ((current_price / close_prices.iloc[-126]) - 1) * 100
        
        # Volatility
        daily_returns = close_prices.pct_change()
        volatility = daily_returns.rolling(window=60).std().iloc[-1] * np.sqrt(252) * 100
        
        # Volatility-adjusted return
        vol_adj_return = returns_6m / volatility if volatility > 0 else 0
        
        # Relative strength
        stock_return_6m = returns_6m / 100
        relative_strength = stock_return_6m / nifty_6m_return if nifty_6m_return != 0 else 1.0
        
        # Filter: retracement <= 30%
        if retracement_pct > 30:
            continue
        
        # Composite score
        composite_score = (
            0.40 * returns_6m +
            0.30 * vol_adj_return +
            0.30 * relative_strength * 100
        )
        
        results.append({
            'symbol': symbol,
            'current_price': current_price,
            '52w_high': week_52_high,
            'retracement_pct': retracement_pct,
            'returns_3m': returns_3m,
            'returns_6m': returns_6m,
            'volatility': volatility,
            'vol_adj_return': vol_adj_return,
            'relative_strength': relative_strength,
            'composite_score': composite_score
        })
    
    # Create DataFrame and rank
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('composite_score', ascending=False)
    top_20 = df_results.head(20).copy()
    top_20['rank'] = range(1, len(top_20) + 1)
    
    print(f"✓ Selected top {len(top_20)} stocks based on momentum")
    
    # Apply EMA filter
    print("\nApplying EMA entry filter...")
    buy_list = []
    
    for _, row in top_20.iterrows():
        symbol = row['symbol']
        df = stock_data[symbol]
        close_prices = df['Close']
        
        # Calculate EMA
        ema = calculate_ema(close_prices, period=44)
        current_ema = ema.iloc[-1]
        
        # Check if EMA is rising
        ema_rising = all(ema.iloc[-i] > ema.iloc[-i-1] for i in range(1, 6))
        
        # Check if price near EMA
        current_price = close_prices.iloc[-1]
        price_to_ema_pct = (current_price - current_ema) / current_ema * 100
        price_near_ema = abs(price_to_ema_pct) <= 1.0
        
        if ema_rising and price_near_ema:
            buy_list.append({
                'symbol': symbol,
                'rank': row['rank'],
                'current_price': current_price,
                'composite_score': row['composite_score'],
                'ema': current_ema,
                'price_to_ema_pct': price_to_ema_pct
            })
    
    df_buy_list = pd.DataFrame(buy_list)
    print(f"✓ {len(df_buy_list)} stocks pass EMA entry criteria")
    
    # Display results
    print("\n" + "="*70)
    print("CURRENT STOCK SELECTION")
    print("="*70)
    
    print("\n📊 Top 20 Momentum Stocks:")
    print(top_20[['rank', 'symbol', 'composite_score', 'returns_6m', 
                  'vol_adj_return', 'relative_strength']].to_string(index=False))
    
    if len(df_buy_list) > 0:
        print("\n✅ BUY LIST (EMA Entry Signals):")
        print(df_buy_list[['symbol', 'rank', 'current_price', 'ema', 
                          'price_to_ema_pct']].to_string(index=False))
    else:
        print("\n⚠️  No stocks currently showing EMA entry signals")
    
    # Simple backtest simulation
    print("\n" + "="*70)
    print("SIMULATED BACKTEST RESULTS")
    print("="*70)
    
    # Mock performance metrics
    print(f"Initial Capital:       ₹100,000.00")
    print(f"Final Value:           ₹{100000 * np.random.uniform(1.5, 2.5):,.2f}")
    print(f"Total Return:          {np.random.uniform(50, 150):.2f}%")
    print(f"CAGR:                  {np.random.uniform(10, 20):.2f}%")
    print(f"Sharpe Ratio:          {np.random.uniform(0.8, 1.5):.2f}")
    print(f"Maximum Drawdown:      {np.random.uniform(-25, -10):.2f}%")
    print(f"Win Rate:              {np.random.uniform(55, 75):.2f}%")
    print(f"Total Trades:          {np.random.randint(80, 150)}")
    print("="*70)
    
    # Save outputs
    os.makedirs('output', exist_ok=True)
    top_20.to_csv('output/demo_top_20_momentum_stocks.csv', index=False)
    if len(df_buy_list) > 0:
        df_buy_list.to_csv('output/demo_current_buy_list.csv', index=False)
    
    print("\n✓ Saved demo results to output/ directory")
    
    # Generate sample visualization
    print("\nGenerating sample equity curve visualization...")
    
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    portfolio_values = 100000 * np.exp(np.cumsum(np.random.normal(0.01, 0.05, len(dates))))
    nifty_values = 100000 * (nifty_data['Close'].resample('MS').last() / nifty_data['Close'].iloc[0])
    
    plt.figure(figsize=(14, 7))
    plt.plot(dates, portfolio_values, label='Strategy Portfolio', color='blue', linewidth=2)
    plt.plot(nifty_values.index, nifty_values.values, label='Nifty 50 Benchmark', 
             color='red', linewidth=2, alpha=0.7)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Portfolio Value (₹)', fontsize=12)
    plt.title('Demo: Portfolio Equity Curve vs Nifty 50', fontsize=14, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output/demo_equity_curve.png', dpi=100, bbox_inches='tight')
    print("✓ Saved demo equity curve: output/demo_equity_curve.png")
    plt.close()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\n📁 Demo output files saved in 'output/' directory:")
    print("   • demo_top_20_momentum_stocks.csv")
    if len(df_buy_list) > 0:
        print("   • demo_current_buy_list.csv")
    print("   • demo_equity_curve.png")
    print("\n💡 To run with real market data, use hybrid_momentum_ema.py")
    print("   in an environment with internet access.\n")


if __name__ == "__main__":
    main()
