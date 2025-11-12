#!/usr/bin/env python3
"""
Hybrid Momentum-EMA Trading Strategy for Nifty Stocks

This script implements a two-stage stock selection strategy:
1. Momentum-based selection: Filters and ranks stocks based on returns, volatility, and relative strength
2. EMA-based entry timing: Uses 44-day EMA to identify optimal entry points

Author: Automated Strategy Builder
Date: 2025-11-12
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
import requests
from ta.trend import EMAIndicator
import os

warnings.filterwarnings('ignore')


# ============================================================================
# DATA FETCHING FUNCTIONS
# ============================================================================

def get_nifty_500_symbols():
    """
    Fetch Nifty 500 stock symbols.
    
    For this implementation, we use a representative subset of Nifty stocks.
    In production, you would fetch the complete list from NSE or a CSV file.
    
    Returns:
        list: List of stock symbols in NSE format (with .NS suffix for yfinance)
    """
    # Sample Nifty 200 stocks (subset for faster execution)
    # In production, fetch the complete list from NSE website or use a CSV
    nifty_stocks = [
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC',
        'SBIN', 'BHARTIARTL', 'KOTAKBANK', 'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI',
        'TITAN', 'BAJFINANCE', 'SUNPHARMA', 'ULTRACEMCO', 'NESTLEIND', 'WIPRO',
        'HCLTECH', 'ADANIPORTS', 'NTPC', 'POWERGRID', 'M&M', 'TECHM', 'TATAMOTORS',
        'BAJAJFINSV', 'ONGC', 'TATASTEEL', 'INDUSINDBK', 'COALINDIA', 'DIVISLAB',
        'DRREDDY', 'CIPLA', 'GRASIM', 'HINDALCO', 'SHREECEM', 'BRITANNIA', 'BPCL',
        'EICHERMOT', 'HEROMOTOCO', 'TATACONSUM', 'JSWSTEEL', 'SBILIFE', 'HDFCLIFE',
        'APOLLOHOSP', 'BAJAJ-AUTO', 'ADANIENT', 'VEDL', 'GODREJCP', 'DABUR',
        'PIDILITIND', 'TORNTPHARM', 'BERGEPAINT', 'COLPAL', 'MARICO', 'AMBUJACEM',
        'SIEMENS', 'DLF', 'GAIL', 'ADANIGREEN', 'HAVELLS', 'BOSCHLTD', 'BANDHANBNK',
        'BIOCON', 'SRF', 'INDIGO', 'MOTHERSON', 'JINDALSTEL', 'LUPIN', 'ZEEL',
        'AUROPHARMA', 'MCDOWELL-N', 'SAIL', 'NMDC', 'PETRONET', 'CONCOR', 'GODREJPROP',
        'SRTRANSFIN', 'PAGEIND', 'ICICIPRULI', 'BANKBARODA', 'PNB', 'CANBK', 'IOC',
        'RECLTD', 'OFSS', 'MUTHOOTFIN', 'CHOLAFIN', 'L&TFH', 'TATAPOWER', 'ACC',
        'ALKEM', 'LALPATHLAB', 'DMART', 'TVSMOTOR', 'MPHASIS', 'INDUSTOWER', 'CADILAHC'
    ]
    
    # Add .NS suffix for NSE stocks (required by yfinance)
    return [f"{symbol}.NS" for symbol in nifty_stocks]


def get_stock_data(symbol, start_date, end_date, max_retries=3):
    """
    Fetch OHLCV data for a single stock using yfinance.
    
    Args:
        symbol (str): Stock symbol (e.g., 'RELIANCE.NS')
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        pd.DataFrame: OHLCV data with date index
    """
    for attempt in range(max_retries):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, auto_adjust=True)
            
            if df.empty:
                print(f"Warning: No data retrieved for {symbol}")
                return None
            
            # Keep only necessary columns
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            return df
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Retry {attempt + 1}/{max_retries} for {symbol}: {str(e)}")
                continue
            else:
                print(f"Error fetching data for {symbol}: {str(e)}")
                return None
    
    return None


def fetch_all_stock_data(symbols, start_date, end_date):
    """
    Fetch data for all symbols in the list.
    
    Args:
        symbols (list): List of stock symbols
        start_date (str): Start date
        end_date (str): End date
    
    Returns:
        dict: Dictionary with symbol as key and DataFrame as value
    """
    stock_data = {}
    total = len(symbols)
    
    print(f"\nFetching data for {total} stocks...")
    for i, symbol in enumerate(symbols, 1):
        print(f"  [{i}/{total}] Fetching {symbol}...", end='\r')
        df = get_stock_data(symbol, start_date, end_date)
        if df is not None and len(df) > 250:  # At least ~1 year of data
            stock_data[symbol] = df
    
    print(f"\n✓ Successfully fetched data for {len(stock_data)} stocks")
    return stock_data


# ============================================================================
# MOMENTUM METRICS CALCULATION
# ============================================================================

def calculate_momentum_metrics(df, nifty_returns=None):
    """
    Calculate momentum metrics for a stock.
    
    Args:
        df (pd.DataFrame): Stock OHLCV data
        nifty_returns (pd.Series): Nifty returns for relative strength calculation
    
    Returns:
        dict: Dictionary containing all momentum metrics
    """
    try:
        close_prices = df['Close']
        
        # Current price
        current_price = close_prices.iloc[-1]
        
        # 52-week high and retracement
        week_52_high = close_prices.rolling(window=252).max().iloc[-1]
        retracement_pct = ((week_52_high - current_price) / week_52_high) * 100
        
        # Returns calculation
        returns_3m = ((current_price / close_prices.iloc[-63]) - 1) * 100 if len(close_prices) > 63 else 0
        returns_6m = ((current_price / close_prices.iloc[-126]) - 1) * 100 if len(close_prices) > 126 else 0
        
        # Volatility (rolling 60-day standard deviation of returns)
        daily_returns = close_prices.pct_change()
        volatility = daily_returns.rolling(window=60).std().iloc[-1] * np.sqrt(252) * 100
        
        # Volatility-adjusted return
        vol_adj_return = returns_6m / volatility if volatility > 0 else 0
        
        # Relative strength vs Nifty
        relative_strength = 1.0  # Default
        if nifty_returns is not None:
            stock_return_6m = returns_6m / 100
            nifty_return_6m = nifty_returns
            if nifty_return_6m != 0:
                relative_strength = stock_return_6m / nifty_return_6m
        
        return {
            'current_price': current_price,
            '52w_high': week_52_high,
            'retracement_pct': retracement_pct,
            'returns_3m': returns_3m,
            'returns_6m': returns_6m,
            'volatility': volatility,
            'vol_adj_return': vol_adj_return,
            'relative_strength': relative_strength
        }
    
    except Exception as e:
        print(f"Error calculating momentum metrics: {str(e)}")
        return None


def calculate_composite_score(metrics):
    """
    Calculate composite score based on momentum metrics.
    
    Weights:
    - 40% on 6-month return
    - 30% on volatility-adjusted return
    - 30% on relative strength
    
    Args:
        metrics (dict): Dictionary of momentum metrics
    
    Returns:
        float: Composite score
    """
    score = (
        0.40 * metrics['returns_6m'] +
        0.30 * metrics['vol_adj_return'] +
        0.30 * metrics['relative_strength'] * 100
    )
    return score


# ============================================================================
# EMA SIGNALS CALCULATION
# ============================================================================

def calculate_ema_signals(df, ema_period=44):
    """
    Calculate EMA-based entry signals.
    
    Args:
        df (pd.DataFrame): Stock OHLCV data
        ema_period (int): EMA period (default: 44 days)
    
    Returns:
        dict: Dictionary containing EMA signals
    """
    try:
        close_prices = df['Close'].copy()
        
        # Calculate 44-day EMA
        ema_indicator = EMAIndicator(close=close_prices, window=ema_period)
        ema = ema_indicator.ema_indicator()
        
        # Check if EMA is rising (EMA[t] > EMA[t-1] for last 5 days)
        ema_rising = True
        for i in range(1, 6):
            if len(ema) > i and ema.iloc[-i] <= ema.iloc[-i-1]:
                ema_rising = False
                break
        
        # Check if price has touched/crossed EMA (within ±1%)
        current_price = close_prices.iloc[-1]
        current_ema = ema.iloc[-1]
        price_to_ema_ratio = (current_price - current_ema) / current_ema * 100
        price_near_ema = abs(price_to_ema_ratio) <= 1.0
        
        # Entry signal: EMA rising AND price near EMA
        entry_signal = ema_rising and price_near_ema
        
        # Exit signal: Price closes below EMA by >2%
        exit_signal = price_to_ema_ratio < -2.0
        
        return {
            'ema': current_ema,
            'ema_rising': ema_rising,
            'price_near_ema': price_near_ema,
            'price_to_ema_pct': price_to_ema_ratio,
            'entry_signal': entry_signal,
            'exit_signal': exit_signal,
            'ema_series': ema
        }
    
    except Exception as e:
        print(f"Error calculating EMA signals: {str(e)}")
        return None


# ============================================================================
# STOCK SELECTION FUNCTIONS
# ============================================================================

def select_top_stocks(stock_data, nifty_data, top_n=20):
    """
    Select top N stocks based on momentum metrics.
    
    Args:
        stock_data (dict): Dictionary of stock DataFrames
        nifty_data (pd.DataFrame): Nifty index data
        top_n (int): Number of top stocks to select
    
    Returns:
        pd.DataFrame: DataFrame with top stocks and their metrics
    """
    results = []
    
    # Calculate Nifty 6-month return
    nifty_6m_return = 0
    if nifty_data is not None and len(nifty_data) > 126:
        nifty_current = nifty_data['Close'].iloc[-1]
        nifty_6m_ago = nifty_data['Close'].iloc[-126]
        nifty_6m_return = (nifty_current / nifty_6m_ago) - 1
    
    print("\nCalculating momentum metrics for all stocks...")
    for symbol, df in stock_data.items():
        metrics = calculate_momentum_metrics(df, nifty_6m_return)
        if metrics is None:
            continue
        
        # Filter: Retracement <= 30%
        if metrics['retracement_pct'] > 30:
            continue
        
        # Calculate composite score
        composite_score = calculate_composite_score(metrics)
        
        results.append({
            'symbol': symbol,
            'current_price': metrics['current_price'],
            '52w_high': metrics['52w_high'],
            'retracement_pct': metrics['retracement_pct'],
            'returns_3m': metrics['returns_3m'],
            'returns_6m': metrics['returns_6m'],
            'volatility': metrics['volatility'],
            'vol_adj_return': metrics['vol_adj_return'],
            'relative_strength': metrics['relative_strength'],
            'composite_score': composite_score
        })
    
    # Create DataFrame and sort by composite score
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('composite_score', ascending=False)
    
    # Select top N
    top_stocks = df_results.head(top_n).copy()
    top_stocks['rank'] = range(1, len(top_stocks) + 1)
    
    print(f"✓ Selected top {len(top_stocks)} stocks based on momentum")
    return top_stocks


def apply_ema_filter(top_stocks, stock_data):
    """
    Apply EMA-based entry filter to top momentum stocks.
    
    Args:
        top_stocks (pd.DataFrame): Top stocks from momentum selection
        stock_data (dict): Dictionary of stock DataFrames
    
    Returns:
        pd.DataFrame: Stocks with EMA entry signals
    """
    buy_list = []
    
    print("\nApplying EMA entry filter...")
    for _, row in top_stocks.iterrows():
        symbol = row['symbol']
        df = stock_data[symbol]
        
        ema_signals = calculate_ema_signals(df)
        if ema_signals is None:
            continue
        
        if ema_signals['entry_signal']:
            buy_list.append({
                'symbol': symbol,
                'rank': row['rank'],
                'current_price': row['current_price'],
                'composite_score': row['composite_score'],
                'ema': ema_signals['ema'],
                'ema_rising': ema_signals['ema_rising'],
                'price_to_ema_pct': ema_signals['price_to_ema_pct']
            })
    
    df_buy_list = pd.DataFrame(buy_list)
    print(f"✓ {len(df_buy_list)} stocks pass EMA entry criteria")
    return df_buy_list


# ============================================================================
# BACKTESTING ENGINE
# ============================================================================

def backtest_strategy(stock_data, nifty_data, start_date, end_date, initial_capital=100000):
    """
    Backtest the hybrid momentum-EMA strategy.
    
    Args:
        stock_data (dict): Dictionary of stock DataFrames
        nifty_data (pd.DataFrame): Nifty index data
        start_date (str): Backtest start date
        end_date (str): Backtest end date
        initial_capital (float): Initial portfolio capital
    
    Returns:
        dict: Backtest results including portfolio values, trades, and metrics
    """
    print("\n" + "="*70)
    print("BACKTESTING STRATEGY")
    print("="*70)
    
    # Generate monthly rebalance dates
    date_range = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    # Portfolio tracking
    portfolio = {}  # {symbol: {'shares': N, 'entry_price': P, 'entry_date': D}}
    cash = initial_capital
    portfolio_values = []
    trades = []
    
    for rebalance_date in date_range:
        rebalance_date_str = rebalance_date.strftime('%Y-%m-%d')
        print(f"\n--- Rebalancing on {rebalance_date_str} ---")
        
        # Get stock data up to rebalance date
        current_stock_data = {}
        for symbol, df in stock_data.items():
            df_slice = df[df.index <= rebalance_date]
            if len(df_slice) > 250:  # Need sufficient history
                current_stock_data[symbol] = df_slice
        
        if len(current_stock_data) < 20:
            continue
        
        # Get Nifty data up to rebalance date
        nifty_slice = nifty_data[nifty_data.index <= rebalance_date] if nifty_data is not None else None
        
        # Select top 20 stocks
        top_stocks = select_top_stocks(current_stock_data, nifty_slice, top_n=20)
        
        if len(top_stocks) == 0:
            continue
        
        top_symbols = set(top_stocks['symbol'].values)
        
        # Exit positions not in top 20
        symbols_to_exit = []
        for symbol in portfolio.keys():
            if symbol not in top_symbols:
                symbols_to_exit.append(symbol)
        
        for symbol in symbols_to_exit:
            # Get current price
            if symbol in current_stock_data:
                current_price = current_stock_data[symbol]['Close'].iloc[-1]
                shares = portfolio[symbol]['shares']
                entry_price = portfolio[symbol]['entry_price']
                
                # Sell
                cash += shares * current_price
                pnl = (current_price - entry_price) * shares
                pnl_pct = ((current_price / entry_price) - 1) * 100
                
                trades.append({
                    'date': rebalance_date,
                    'symbol': symbol,
                    'action': 'SELL',
                    'price': current_price,
                    'shares': shares,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'reason': 'Out of Top 20'
                })
                
                del portfolio[symbol]
        
        # Apply EMA filter for new entries
        buy_candidates = apply_ema_filter(top_stocks, current_stock_data)
        
        # Buy new positions
        if len(buy_candidates) > 0 and cash > 0:
            # Equal weight allocation
            allocation_per_stock = cash / len(buy_candidates)
            
            for _, row in buy_candidates.iterrows():
                symbol = row['symbol']
                
                # Skip if already holding
                if symbol in portfolio:
                    continue
                
                current_price = row['current_price']
                shares = int(allocation_per_stock / current_price)
                
                if shares > 0:
                    cost = shares * current_price
                    cash -= cost
                    
                    portfolio[symbol] = {
                        'shares': shares,
                        'entry_price': current_price,
                        'entry_date': rebalance_date
                    }
                    
                    trades.append({
                        'date': rebalance_date,
                        'symbol': symbol,
                        'action': 'BUY',
                        'price': current_price,
                        'shares': shares,
                        'pnl': 0,
                        'pnl_pct': 0,
                        'reason': 'EMA Entry Signal'
                    })
        
        # Calculate portfolio value
        portfolio_value = cash
        for symbol, position in portfolio.items():
            if symbol in current_stock_data:
                current_price = current_stock_data[symbol]['Close'].iloc[-1]
                portfolio_value += position['shares'] * current_price
        
        portfolio_values.append({
            'date': rebalance_date,
            'portfolio_value': portfolio_value,
            'cash': cash,
            'positions': len(portfolio)
        })
    
    # Convert to DataFrames
    df_portfolio = pd.DataFrame(portfolio_values)
    df_trades = pd.DataFrame(trades)
    
    # Calculate performance metrics
    metrics = calculate_performance_metrics(df_portfolio, df_trades, initial_capital)
    
    return {
        'portfolio_values': df_portfolio,
        'trades': df_trades,
        'metrics': metrics,
        'final_portfolio': portfolio
    }


def calculate_performance_metrics(df_portfolio, df_trades, initial_capital):
    """
    Calculate performance metrics for the strategy.
    
    Args:
        df_portfolio (pd.DataFrame): Portfolio values over time
        df_trades (pd.DataFrame): All trades executed
        initial_capital (float): Initial capital
    
    Returns:
        dict: Performance metrics
    """
    if len(df_portfolio) == 0:
        return {}
    
    # CAGR calculation
    final_value = df_portfolio['portfolio_value'].iloc[-1]
    start_date = df_portfolio['date'].iloc[0]
    end_date = df_portfolio['date'].iloc[-1]
    years = (end_date - start_date).days / 365.25
    
    cagr = 0
    if years > 0:
        cagr = ((final_value / initial_capital) ** (1 / years) - 1) * 100
    
    # Calculate daily returns
    df_portfolio = df_portfolio.set_index('date')
    df_portfolio['returns'] = df_portfolio['portfolio_value'].pct_change()
    
    # Sharpe Ratio (assuming 0% risk-free rate)
    avg_return = df_portfolio['returns'].mean()
    std_return = df_portfolio['returns'].std()
    sharpe_ratio = 0
    if std_return > 0:
        sharpe_ratio = (avg_return / std_return) * np.sqrt(12)  # Annualized
    
    # Maximum Drawdown
    df_portfolio['cummax'] = df_portfolio['portfolio_value'].cummax()
    df_portfolio['drawdown'] = (df_portfolio['portfolio_value'] - df_portfolio['cummax']) / df_portfolio['cummax'] * 100
    max_drawdown = df_portfolio['drawdown'].min()
    
    # Win Rate
    win_rate = 0
    if len(df_trades) > 0:
        sell_trades = df_trades[df_trades['action'] == 'SELL']
        if len(sell_trades) > 0:
            winning_trades = len(sell_trades[sell_trades['pnl'] > 0])
            win_rate = (winning_trades / len(sell_trades)) * 100
    
    # Total Return
    total_return = ((final_value / initial_capital) - 1) * 100
    
    return {
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return_pct': total_return,
        'cagr_pct': cagr,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown_pct': max_drawdown,
        'win_rate_pct': win_rate,
        'total_trades': len(df_trades),
        'years': years
    }


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_momentum_distribution(top_stocks, output_dir='output'):
    """
    Plot momentum score distribution.
    
    Args:
        top_stocks (pd.DataFrame): Top stocks DataFrame
        output_dir (str): Output directory for saving plots
    """
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Momentum Metrics Distribution', fontsize=16, fontweight='bold')
    
    # Composite Score
    axes[0, 0].barh(top_stocks['symbol'], top_stocks['composite_score'], color='steelblue')
    axes[0, 0].set_xlabel('Composite Score')
    axes[0, 0].set_title('Top Stocks by Composite Score')
    axes[0, 0].invert_yaxis()
    
    # 6-Month Returns
    axes[0, 1].barh(top_stocks['symbol'], top_stocks['returns_6m'], color='green')
    axes[0, 1].set_xlabel('6-Month Return (%)')
    axes[0, 1].set_title('6-Month Returns')
    axes[0, 1].invert_yaxis()
    
    # Volatility-Adjusted Return
    axes[1, 0].barh(top_stocks['symbol'], top_stocks['vol_adj_return'], color='orange')
    axes[1, 0].set_xlabel('Volatility-Adjusted Return')
    axes[1, 0].set_title('Risk-Adjusted Performance')
    axes[1, 0].invert_yaxis()
    
    # Relative Strength
    axes[1, 1].barh(top_stocks['symbol'], top_stocks['relative_strength'], color='purple')
    axes[1, 1].set_xlabel('Relative Strength vs Nifty')
    axes[1, 1].set_title('Relative Strength')
    axes[1, 1].invert_yaxis()
    axes[1, 1].axvline(x=1, color='red', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    filepath = os.path.join(output_dir, 'momentum_distribution.png')
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    print(f"✓ Saved momentum distribution chart: {filepath}")
    plt.close()


def plot_equity_curve(df_portfolio, nifty_data, initial_capital, output_dir='output'):
    """
    Plot equity curve vs Nifty benchmark.
    
    Args:
        df_portfolio (pd.DataFrame): Portfolio values over time
        nifty_data (pd.DataFrame): Nifty index data
        initial_capital (float): Initial capital
        output_dir (str): Output directory for saving plots
    """
    os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot portfolio equity curve
    df_plot = df_portfolio.set_index('date')
    ax.plot(df_plot.index, df_plot['portfolio_value'], label='Strategy Portfolio', 
            color='blue', linewidth=2)
    
    # Plot Nifty benchmark (normalized to initial capital)
    if nifty_data is not None and len(nifty_data) > 0:
        nifty_slice = nifty_data[nifty_data.index.isin(df_plot.index)]
        if len(nifty_slice) > 0:
            nifty_normalized = (nifty_slice['Close'] / nifty_slice['Close'].iloc[0]) * initial_capital
            ax.plot(nifty_slice.index, nifty_normalized, label='Nifty 50 Benchmark', 
                   color='red', linewidth=2, alpha=0.7)
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Portfolio Value (₹)', fontsize=12)
    ax.set_title('Portfolio Equity Curve vs Nifty 50', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    filepath = os.path.join(output_dir, 'equity_curve.png')
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    print(f"✓ Saved equity curve chart: {filepath}")
    plt.close()


def plot_drawdown(df_portfolio, output_dir='output'):
    """
    Plot drawdown chart.
    
    Args:
        df_portfolio (pd.DataFrame): Portfolio values over time
        output_dir (str): Output directory for saving plots
    """
    os.makedirs(output_dir, exist_ok=True)
    
    df_plot = df_portfolio.set_index('date')
    df_plot['cummax'] = df_plot['portfolio_value'].cummax()
    df_plot['drawdown'] = (df_plot['portfolio_value'] - df_plot['cummax']) / df_plot['cummax'] * 100
    
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.fill_between(df_plot.index, df_plot['drawdown'], 0, alpha=0.3, color='red')
    ax.plot(df_plot.index, df_plot['drawdown'], color='darkred', linewidth=1.5)
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.set_title('Portfolio Drawdown Over Time', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    filepath = os.path.join(output_dir, 'drawdown_chart.png')
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    print(f"✓ Saved drawdown chart: {filepath}")
    plt.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function for the hybrid momentum-EMA strategy.
    """
    print("\n" + "="*70)
    print("HYBRID MOMENTUM-EMA TRADING STRATEGY")
    print("="*70)
    print("\nStrategy Overview:")
    print("  1. Momentum Selection: Filters stocks by 52w retracement, ranks by")
    print("     composite score (returns, volatility-adjusted returns, relative strength)")
    print("  2. EMA Entry: Uses 44-day EMA to identify optimal entry points")
    print("  3. Exit: Remove stocks that drop out of top 20 or close >2% below EMA")
    print("="*70)
    
    # Configuration
    BACKTEST_YEARS = 5
    end_date = datetime.now()
    start_date = end_date - timedelta(days=BACKTEST_YEARS*365 + 180)  # Extra buffer for calculations
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"\nBacktest Period: {start_date_str} to {end_date_str}")
    print(f"Duration: ~{BACKTEST_YEARS} years")
    
    # Fetch Nifty 500 symbols
    symbols = get_nifty_500_symbols()
    print(f"\nStock Universe: {len(symbols)} Nifty stocks")
    
    # Fetch Nifty 50 data for benchmark
    print("\nFetching Nifty 50 benchmark data...")
    nifty_data = get_stock_data('^NSEI', start_date_str, end_date_str)
    
    # Fetch all stock data
    stock_data = fetch_all_stock_data(symbols, start_date_str, end_date_str)
    
    if len(stock_data) < 20:
        print("\nError: Insufficient stock data. Need at least 20 stocks.")
        return
    
    # Current stock selection (for latest signals)
    print("\n" + "="*70)
    print("CURRENT STOCK SELECTION")
    print("="*70)
    
    top_stocks = select_top_stocks(stock_data, nifty_data, top_n=20)
    
    print("\n📊 Top 20 Momentum Stocks:")
    print(top_stocks[['rank', 'symbol', 'composite_score', 'returns_6m', 
                      'vol_adj_return', 'relative_strength']].to_string(index=False))
    
    # Apply EMA filter
    buy_list = apply_ema_filter(top_stocks, stock_data)
    
    if len(buy_list) > 0:
        print("\n✅ BUY LIST (EMA Entry Signals):")
        print(buy_list[['symbol', 'rank', 'current_price', 'ema', 
                       'price_to_ema_pct']].to_string(index=False))
    else:
        print("\n⚠️  No stocks currently showing EMA entry signals")
    
    # Save current results
    os.makedirs('output', exist_ok=True)
    top_stocks.to_csv('output/top_20_momentum_stocks.csv', index=False)
    if len(buy_list) > 0:
        buy_list.to_csv('output/current_buy_list.csv', index=False)
    print("\n✓ Saved current stock selections to output/ directory")
    
    # Backtest
    backtest_results = backtest_strategy(
        stock_data, 
        nifty_data, 
        start_date_str, 
        end_date_str,
        initial_capital=100000
    )
    
    # Display performance metrics
    metrics = backtest_results['metrics']
    print("\n" + "="*70)
    print("BACKTEST PERFORMANCE METRICS")
    print("="*70)
    print(f"Initial Capital:       ₹{metrics['initial_capital']:,.2f}")
    print(f"Final Value:           ₹{metrics['final_value']:,.2f}")
    print(f"Total Return:          {metrics['total_return_pct']:.2f}%")
    print(f"CAGR:                  {metrics['cagr_pct']:.2f}%")
    print(f"Sharpe Ratio:          {metrics['sharpe_ratio']:.2f}")
    print(f"Maximum Drawdown:      {metrics['max_drawdown_pct']:.2f}%")
    print(f"Win Rate:              {metrics['win_rate_pct']:.2f}%")
    print(f"Total Trades:          {metrics['total_trades']}")
    print("="*70)
    
    # Save backtest results
    backtest_results['portfolio_values'].to_csv('output/portfolio_values.csv', index=False)
    backtest_results['trades'].to_csv('output/trades_history.csv', index=False)
    print("\n✓ Saved backtest results to output/ directory")
    
    # Generate visualizations
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70)
    
    plot_momentum_distribution(top_stocks)
    plot_equity_curve(backtest_results['portfolio_values'], nifty_data, metrics['initial_capital'])
    plot_drawdown(backtest_results['portfolio_values'])
    
    print("\n" + "="*70)
    print("STRATEGY EXECUTION COMPLETE")
    print("="*70)
    print("\n📁 Output files saved in 'output/' directory:")
    print("   • top_20_momentum_stocks.csv - Current top momentum stocks")
    print("   • current_buy_list.csv - Stocks with EMA entry signals")
    print("   • portfolio_values.csv - Portfolio value over time")
    print("   • trades_history.csv - All trades executed")
    print("   • momentum_distribution.png - Momentum metrics visualization")
    print("   • equity_curve.png - Portfolio vs Nifty performance")
    print("   • drawdown_chart.png - Drawdown analysis")
    print("\n✨ Strategy analysis complete!\n")


if __name__ == "__main__":
    main()
