#!/usr/bin/env python3
"""
Demo script for Nifty Alpha Screen with synthetic data.
This demonstrates the system's functionality without requiring internet access.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)


def generate_synthetic_stock_data(symbol: str, days: int = 500) -> pd.DataFrame:
    """
    Generate synthetic stock price data.
    
    Args:
        symbol: Stock symbol
        days: Number of days of data
    
    Returns:
        DataFrame with synthetic stock data
    """
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate random walk with drift
    returns = np.random.normal(0.0005, 0.02, days)
    prices = 100 * np.exp(np.cumsum(returns))
    
    # Add some volatility
    high = prices * (1 + np.random.uniform(0, 0.02, days))
    low = prices * (1 - np.random.uniform(0, 0.02, days))
    
    df = pd.DataFrame({
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
        'High': high,
        'Low': low,
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, days)
    }, index=dates)
    
    return df


def demo_screening():
    """
    Demonstrate the screening process with synthetic data.
    """
    print("="*70)
    print("NIFTY ALPHA SCREEN - DEMO WITH SYNTHETIC DATA")
    print("="*70)
    
    # Generate synthetic data for 30 stocks
    num_stocks = 30
    stock_symbols = [f"STOCK{i:02d}.NS" for i in range(1, num_stocks + 1)]
    
    print(f"\nGenerating synthetic data for {num_stocks} stocks...")
    
    # Generate Nifty 50 index data
    nifty_df = generate_synthetic_stock_data("NIFTY50", days=500)
    
    # Calculate metrics for all stocks
    metrics_list = []
    
    for symbol in stock_symbols:
        # Generate stock data with varying characteristics
        stock_df = generate_synthetic_stock_data(symbol, days=500)
        
        # Calculate metrics
        # 52-week high retracement
        high_52w = stock_df['High'].tail(252).max()
        current_price = stock_df['Close'].iloc[-1]
        retracement = ((high_52w - current_price) / high_52w) * 100
        
        # 6-month return
        start_price = stock_df['Close'].iloc[-126]
        return_6m = ((current_price - start_price) / start_price) * 100
        
        # Volatility
        returns = stock_df['Close'].pct_change().tail(126)
        volatility_6m = returns.std() * np.sqrt(252) * 100
        
        # Volatility-adjusted return
        vol_adj_return = return_6m / volatility_6m if volatility_6m > 0 else 0
        
        # Relative strength (vs Nifty)
        nifty_start = nifty_df['Close'].iloc[-126]
        nifty_end = nifty_df['Close'].iloc[-1]
        nifty_return = ((nifty_end - nifty_start) / nifty_start) * 100
        rel_strength = return_6m - nifty_return
        
        metrics_list.append({
            'Symbol': symbol,
            'Current_Price': current_price,
            'Retracement_52W': retracement,
            'Return_3M': return_6m * 0.7,  # Approximate
            'Return_6M': return_6m,
            'Volatility_6M': volatility_6m,
            'Vol_Adj_Return_6M': vol_adj_return,
            'Relative_Strength_6M': rel_strength
        })
    
    # Create DataFrame
    metrics_df = pd.DataFrame(metrics_list)
    
    print(f"\nInitial stocks: {len(metrics_df)}")
    
    # Apply filters
    print("\nApplying filters...")
    
    # Filter 1: Retracement ≤ 30%
    filtered_df = metrics_df[metrics_df['Retracement_52W'] <= 30].copy()
    print(f"After retracement filter (≤30%): {len(filtered_df)}")
    
    # Filter 2: Top 50% by returns
    if len(filtered_df) > 0:
        return_threshold = filtered_df['Return_6M'].quantile(0.5)
        filtered_df = filtered_df[filtered_df['Return_6M'] >= return_threshold]
        print(f"After return filter (top 50%): {len(filtered_df)}")
    
    # Filter 3: Positive relative strength
    if len(filtered_df) > 0:
        filtered_df = filtered_df[filtered_df['Relative_Strength_6M'] > 0]
        print(f"After relative strength filter (>0): {len(filtered_df)}")
    
    # Calculate composite scores
    if len(filtered_df) > 0:
        print("\nCalculating composite scores...")
        
        # Normalize metrics
        filtered_df['Return_Norm'] = (filtered_df['Return_6M'] - filtered_df['Return_6M'].min()) / (filtered_df['Return_6M'].max() - filtered_df['Return_6M'].min())
        filtered_df['VolAdj_Norm'] = (filtered_df['Vol_Adj_Return_6M'] - filtered_df['Vol_Adj_Return_6M'].min()) / (filtered_df['Vol_Adj_Return_6M'].max() - filtered_df['Vol_Adj_Return_6M'].min())
        filtered_df['RelStr_Norm'] = (filtered_df['Relative_Strength_6M'] - filtered_df['Relative_Strength_6M'].min()) / (filtered_df['Relative_Strength_6M'].max() - filtered_df['Relative_Strength_6M'].min())
        
        # Composite score
        filtered_df['Composite_Score'] = (
            0.4 * filtered_df['Return_Norm'] +
            0.3 * filtered_df['VolAdj_Norm'] +
            0.3 * filtered_df['RelStr_Norm']
        )
        
        # Select top 20
        top_20 = filtered_df.sort_values('Composite_Score', ascending=False).head(20)
        
        # Display results
        print("\n" + "="*70)
        print("TOP 20 STOCKS (SYNTHETIC DATA DEMO)")
        print("="*70)
        
        display_columns = [
            'Symbol', 'Current_Price', 'Retracement_52W',
            'Return_6M', 'Vol_Adj_Return_6M', 'Relative_Strength_6M',
            'Composite_Score'
        ]
        
        # Format the output
        display_df = top_20[display_columns].copy()
        display_df['Current_Price'] = display_df['Current_Price'].round(2)
        display_df['Retracement_52W'] = display_df['Retracement_52W'].round(2)
        display_df['Return_6M'] = display_df['Return_6M'].round(2)
        display_df['Vol_Adj_Return_6M'] = display_df['Vol_Adj_Return_6M'].round(3)
        display_df['Relative_Strength_6M'] = display_df['Relative_Strength_6M'].round(2)
        display_df['Composite_Score'] = display_df['Composite_Score'].round(3)
        
        print(display_df.to_string(index=False))
        print("="*70)
        
        # Generate simple backtest
        print("\n" + "="*70)
        print("SIMULATED BACKTEST")
        print("="*70)
        
        # Simulate 12 months of returns
        months = 12
        dates = pd.date_range(end=datetime.now(), periods=months, freq='ME')
        
        portfolio_returns = [100]
        nifty_returns = [100]
        
        for i in range(1, months):
            # Simulate portfolio return (slightly better than index)
            port_ret = np.random.normal(0.015, 0.04)
            nifty_ret = np.random.normal(0.01, 0.035)
            
            portfolio_returns.append(portfolio_returns[-1] * (1 + port_ret))
            nifty_returns.append(nifty_returns[-1] * (1 + nifty_ret))
        
        portfolio_series = pd.Series(portfolio_returns, index=dates)
        nifty_series = pd.Series(nifty_returns, index=dates)
        
        # Calculate performance metrics
        years = 1.0
        
        # CAGR
        port_cagr = ((portfolio_series.iloc[-1] / portfolio_series.iloc[0]) ** (1/years) - 1) * 100
        nifty_cagr = ((nifty_series.iloc[-1] / nifty_series.iloc[0]) ** (1/years) - 1) * 100
        
        # Max Drawdown
        port_cummax = portfolio_series.expanding().max()
        port_dd = ((portfolio_series - port_cummax) / port_cummax * 100).min()
        
        nifty_cummax = nifty_series.expanding().max()
        nifty_dd = ((nifty_series - nifty_cummax) / nifty_cummax * 100).min()
        
        # Sharpe Ratio
        port_returns_pct = portfolio_series.pct_change().dropna()
        nifty_returns_pct = nifty_series.pct_change().dropna()
        
        port_sharpe = (port_returns_pct.mean() / port_returns_pct.std()) * np.sqrt(12) if port_returns_pct.std() > 0 else 0
        nifty_sharpe = (nifty_returns_pct.mean() / nifty_returns_pct.std()) * np.sqrt(12) if nifty_returns_pct.std() > 0 else 0
        
        # Win Rate
        port_win_rate = (port_returns_pct > 0).sum() / len(port_returns_pct) * 100
        nifty_win_rate = (nifty_returns_pct > 0).sum() / len(nifty_returns_pct) * 100
        
        # Print summary
        print("\nPortfolio Performance (Simulated):")
        print(f"  CAGR:              {port_cagr:.2f}%")
        print(f"  Max Drawdown:      {port_dd:.2f}%")
        print(f"  Sharpe Ratio:      {port_sharpe:.2f}")
        print(f"  Win Rate:          {port_win_rate:.2f}%")
        
        print("\nNifty 50 Performance (Simulated):")
        print(f"  CAGR:              {nifty_cagr:.2f}%")
        print(f"  Max Drawdown:      {nifty_dd:.2f}%")
        print(f"  Sharpe Ratio:      {nifty_sharpe:.2f}")
        print(f"  Win Rate:          {nifty_win_rate:.2f}%")
        
        print(f"\nOutperformance:")
        print(f"  Alpha:             {port_cagr - nifty_cagr:.2f}%")
        print("="*70)
        
        # Generate charts
        print("\nGenerating charts...")
        
        # Cumulative returns chart
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        ax1.plot(portfolio_series.index, portfolio_series.values, label='Portfolio', linewidth=2)
        ax1.plot(nifty_series.index, nifty_series.values, label='Nifty 50', linewidth=2)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Cumulative Return (Base 100)')
        ax1.set_title('Portfolio vs Nifty 50 - Cumulative Returns (Simulated)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Drawdowns
        port_dd_series = (portfolio_series - port_cummax) / port_cummax * 100
        nifty_dd_series = (nifty_series - nifty_cummax) / nifty_cummax * 100
        
        ax2.fill_between(port_dd_series.index, 0, port_dd_series.values, alpha=0.3, label='Portfolio Drawdown')
        ax2.fill_between(nifty_dd_series.index, 0, nifty_dd_series.values, alpha=0.3, label='Nifty 50 Drawdown')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Drawdown (%)')
        ax2.set_title('Drawdowns from Peak (Simulated)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('demo_results.png', dpi=300, bbox_inches='tight')
        print("Chart saved: demo_results.png")
        
        plt.show()
        
    else:
        print("\nNo stocks passed all filters.")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nNote: This demo uses synthetic data for illustration purposes.")
    print("Run 'python nifty_alpha_screen.py' with internet access for real data.")


if __name__ == "__main__":
    demo_screening()
