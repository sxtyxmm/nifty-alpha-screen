#!/usr/bin/env python3
"""
Nifty Alpha Screen - A quantitative stock screening and backtesting system
for identifying high-momentum, low-risk outperformers in the Indian stock market.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import warnings
import requests
from bs4 import BeautifulSoup
import time

warnings.filterwarnings('ignore')


# ============================================================================
# DATA FETCHING MODULE
# ============================================================================

def get_nifty_500_symbols() -> List[str]:
    """
    Fetch Nifty 500 stock symbols from NSE India website or Wikipedia.
    Returns a list of Yahoo Finance compatible symbols (with .NS suffix).
    """
    print("Fetching Nifty 500 stock symbols...")
    
    # Try to fetch from Wikipedia as a reliable public source
    try:
        url = "https://en.wikipedia.org/wiki/NIFTY_500"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table with stock symbols
        tables = soup.find_all('table', {'class': 'wikitable'})
        
        symbols = []
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    # Try to extract symbol from the row
                    symbol = cols[0].get_text().strip()
                    if symbol and symbol.isalnum():
                        symbols.append(f"{symbol}.NS")
        
        if symbols:
            print(f"Successfully fetched {len(symbols)} symbols from Wikipedia")
            return symbols[:500]  # Limit to 500 symbols
    except Exception as e:
        print(f"Wikipedia fetch failed: {e}")
    
    # Fallback: Use a curated list of popular Nifty stocks
    print("Using fallback list of Nifty stocks...")
    fallback_symbols = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
        "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
        "TITAN.NS", "BAJFINANCE.NS", "WIPRO.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
        "HCLTECH.NS", "POWERGRID.NS", "NTPC.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
        "BAJAJFINSV.NS", "ONGC.NS", "ADANIPORTS.NS", "COALINDIA.NS", "M&M.NS",
        "TECHM.NS", "DIVISLAB.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS",
        "EICHERMOT.NS", "BRITANNIA.NS", "GRASIM.NS", "HEROMOTOCO.NS", "BPCL.NS",
        "INDUSINDBK.NS", "HINDALCO.NS", "JSWSTEEL.NS", "ADANIENT.NS", "TATACONSUM.NS",
        "SHREECEM.NS", "PIDILITIND.NS", "SIEMENS.NS", "DABUR.NS", "GODREJCP.NS",
        "LTIM.NS", "HDFCLIFE.NS", "SBILIFE.NS", "BAJAJ-AUTO.NS", "VEDL.NS",
        "DLF.NS", "AMBUJACEM.NS", "BANKBARODA.NS", "GAIL.NS", "IOC.NS",
        "TORNTPHARM.NS", "CHOLAFIN.NS", "INDIGO.NS", "PNB.NS", "IDEA.NS",
        "ADANIGREEN.NS", "ADANITRANS.NS", "BANDHANBNK.NS", "BERGEPAINT.NS", "BEL.NS",
        "BIOCON.NS", "BOSCHLTD.NS", "CANBK.NS", "COLPAL.NS", "CONCOR.NS",
        "CUMMINSIND.NS", "DALBHARAT.NS", "ESCORTS.NS", "GLAND.NS", "GODREJPROP.NS",
        "GUJGASLTD.NS", "HAL.NS", "HAVELLS.NS", "ICICIPRULI.NS", "IDFCFIRSTB.NS",
        "INDUSTOWER.NS", "IRCTC.NS", "JINDALSTEL.NS", "JUBLFOOD.NS", "LAURUSLABS.NS",
        "LICHSGFIN.NS", "LUPIN.NS", "MARICO.NS", "MCDOWELL-N.NS", "MFSL.NS",
        "MOTHERSON.NS", "MRF.NS", "MUTHOOTFIN.NS", "NAUKRI.NS", "NMDC.NS",
        "OFSS.NS", "PAGEIND.NS", "PEL.NS", "PERSISTENT.NS", "PETRONET.NS",
        "PGHH.NS", "PFC.NS", "PIIND.NS", "PVR.NS", "RECLTD.NS",
        "SAIL.NS", "SRF.NS", "TATAPOWER.NS", "TATACOMM.NS", "TVSMOTOR.NS",
        "UBL.NS", "MPHASIS.NS", "UPL.NS", "VOLTAS.NS", "ZEEL.NS",
        "ZYDUSLIFE.NS", "AARTIIND.NS", "ABB.NS", "ACC.NS", "ALKEM.NS",
        "AMBUJACEM.NS", "APOLLOTYRE.NS", "ASHOKLEY.NS", "ASTRAL.NS", "AUROPHARMA.NS",
        "BALRAMCHIN.NS", "BATAINDIA.NS", "BHEL.NS", "BSOFT.NS", "CANFINHOME.NS",
        "CHAMBLFERT.NS", "COFORGE.NS", "CROMPTON.NS", "CUB.NS", "DEEPAKNTR.NS",
        "DIXON.NS", "FEDERALBNK.NS", "GODREJIND.NS", "GRANULES.NS", "HDFCAMC.NS",
        "HINDPETRO.NS", "HONAUT.NS", "IBREALEST.NS", "IBULHSGFIN.NS", "ICICIGI.NS",
        "IPCALAB.NS", "IRFC.NS", "IGL.NS", "INDHOTEL.NS", "JKCEMENT.NS",
        "JSWENERGY.NS", "LALPATHLAB.NS", "LTTS.NS", "L&TFH.NS", "MANAPPURAM.NS",
        "MINDTREE.NS", "NATIONALUM.NS", "NAM-INDIA.NS", "NAVINFLUOR.NS", "OBEROIRLTY.NS",
        "ORACLE.NS", "PAYTM.NS", "POLYCAB.NS", "RBLBANK.NS", "SBICARD.NS",
        "SHRIRAMFIN.NS", "SRTRANSFIN.NS", "SUNPHARMA.NS", "SUNTV.NS", "SUPREMEIND.NS",
        "TRENT.NS", "TIINDIA.NS", "TORNTPOWER.NS", "TTML.NS", "UJJIVAN.NS",
        "UNIONBANK.NS", "VGUARD.NS", "WHIRLPOOL.NS", "YESBANK.NS", "ZOMATO.NS"
    ]
    
    return fallback_symbols


def fetch_stock_data(symbol: str, period: str = "2y") -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS')
        period: Time period for data (default: 2 years)
    
    Returns:
        DataFrame with stock price data
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def fetch_nifty_50_data(period: str = "2y") -> pd.DataFrame:
    """
    Fetch Nifty 50 index data for comparison.
    
    Args:
        period: Time period for data (default: 2 years)
    
    Returns:
        DataFrame with Nifty 50 index data
    """
    try:
        nifty = yf.Ticker("^NSEI")
        df = nifty.history(period=period)
        return df
    except Exception as e:
        print(f"Error fetching Nifty 50 data: {e}")
        return None


# ============================================================================
# METRICS CALCULATION MODULE
# ============================================================================

def calculate_retracement_from_52w_high(df: pd.DataFrame) -> float:
    """
    Calculate retracement from 52-week high.
    
    Args:
        df: DataFrame with stock price data
    
    Returns:
        Retracement percentage (0-100)
    """
    if df is None or df.empty:
        return np.nan
    
    # Get last 252 trading days (approximately 1 year)
    lookback_data = df.tail(252)
    if lookback_data.empty:
        return np.nan
    
    high_52w = lookback_data['High'].max()
    current_price = df['Close'].iloc[-1]
    
    retracement = ((high_52w - current_price) / high_52w) * 100
    return retracement


def calculate_returns(df: pd.DataFrame, months: int) -> float:
    """
    Calculate total return over specified months.
    
    Args:
        df: DataFrame with stock price data
        months: Number of months for return calculation
    
    Returns:
        Total return as percentage
    """
    if df is None or df.empty:
        return np.nan
    
    # Approximate trading days for the period
    days = months * 21
    
    if len(df) < days:
        return np.nan
    
    start_price = df['Close'].iloc[-days]
    end_price = df['Close'].iloc[-1]
    
    total_return = ((end_price - start_price) / start_price) * 100
    return total_return


def calculate_volatility(df: pd.DataFrame, months: int) -> float:
    """
    Calculate annualized volatility (standard deviation of returns).
    
    Args:
        df: DataFrame with stock price data
        months: Number of months for volatility calculation
    
    Returns:
        Annualized volatility as percentage
    """
    if df is None or df.empty:
        return np.nan
    
    days = months * 21
    
    if len(df) < days:
        return np.nan
    
    returns = df['Close'].pct_change().tail(days)
    volatility = returns.std() * np.sqrt(252) * 100  # Annualized
    
    return volatility


def calculate_volatility_adjusted_return(df: pd.DataFrame, months: int) -> float:
    """
    Calculate volatility-adjusted return (Sharpe-like ratio).
    
    Args:
        df: DataFrame with stock price data
        months: Number of months for calculation
    
    Returns:
        Volatility-adjusted return
    """
    ret = calculate_returns(df, months)
    vol = calculate_volatility(df, months)
    
    if np.isnan(ret) or np.isnan(vol) or vol == 0:
        return np.nan
    
    return ret / vol


def calculate_relative_strength(stock_df: pd.DataFrame, index_df: pd.DataFrame, months: int) -> float:
    """
    Calculate relative strength vs Nifty 50 index.
    
    Args:
        stock_df: DataFrame with stock price data
        index_df: DataFrame with index price data
        months: Number of months for calculation
    
    Returns:
        Relative strength (stock return - index return)
    """
    stock_return = calculate_returns(stock_df, months)
    index_return = calculate_returns(index_df, months)
    
    if np.isnan(stock_return) or np.isnan(index_return):
        return np.nan
    
    return stock_return - index_return


def calculate_all_metrics(symbol: str, stock_df: pd.DataFrame, index_df: pd.DataFrame) -> Dict:
    """
    Calculate all metrics for a stock.
    
    Args:
        symbol: Stock symbol
        stock_df: DataFrame with stock price data
        index_df: DataFrame with index price data
    
    Returns:
        Dictionary with all calculated metrics
    """
    metrics = {
        'Symbol': symbol,
        'Current_Price': stock_df['Close'].iloc[-1] if stock_df is not None else np.nan,
        'Retracement_52W': calculate_retracement_from_52w_high(stock_df),
        'Return_3M': calculate_returns(stock_df, 3),
        'Return_6M': calculate_returns(stock_df, 6),
        'Volatility_6M': calculate_volatility(stock_df, 6),
        'Vol_Adj_Return_6M': calculate_volatility_adjusted_return(stock_df, 6),
        'Relative_Strength_6M': calculate_relative_strength(stock_df, index_df, 6)
    }
    
    return metrics


# ============================================================================
# FILTERING AND RANKING MODULE
# ============================================================================

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply screening filters to stock data.
    
    Filters:
    1. Retracement ≤ 30% from 52-week high
    2. Strong positive returns (top percentile)
    3. Positive relative strength vs Nifty
    
    Args:
        df: DataFrame with stock metrics
    
    Returns:
        Filtered DataFrame
    """
    print("\nApplying filters...")
    print(f"Initial stocks: {len(df)}")
    
    # Filter 1: Retracement ≤ 30%
    df_filtered = df[df['Retracement_52W'] <= 30].copy()
    print(f"After retracement filter (≤30%): {len(df_filtered)}")
    
    # Filter 2: Top percentile of 6-month returns (top 50%)
    if len(df_filtered) > 0:
        return_threshold = df_filtered['Return_6M'].quantile(0.5)
        df_filtered = df_filtered[df_filtered['Return_6M'] >= return_threshold]
        print(f"After return filter (top 50%): {len(df_filtered)}")
    
    # Filter 3: Positive relative strength
    if len(df_filtered) > 0:
        df_filtered = df_filtered[df_filtered['Relative_Strength_6M'] > 0]
        print(f"After relative strength filter (>0): {len(df_filtered)}")
    
    return df_filtered


def calculate_composite_score(df: pd.DataFrame, 
                              return_weight: float = 0.4,
                              vol_adj_return_weight: float = 0.3,
                              rel_strength_weight: float = 0.3) -> pd.DataFrame:
    """
    Calculate composite score for ranking stocks.
    
    Args:
        df: DataFrame with stock metrics
        return_weight: Weight for 6-month return
        vol_adj_return_weight: Weight for volatility-adjusted return
        rel_strength_weight: Weight for relative strength
    
    Returns:
        DataFrame with composite scores
    """
    # Normalize metrics to 0-1 scale
    df['Return_6M_Norm'] = (df['Return_6M'] - df['Return_6M'].min()) / (df['Return_6M'].max() - df['Return_6M'].min() + 1e-10)
    df['Vol_Adj_Return_Norm'] = (df['Vol_Adj_Return_6M'] - df['Vol_Adj_Return_6M'].min()) / (df['Vol_Adj_Return_6M'].max() - df['Vol_Adj_Return_6M'].min() + 1e-10)
    df['Rel_Strength_Norm'] = (df['Relative_Strength_6M'] - df['Relative_Strength_6M'].min()) / (df['Relative_Strength_6M'].max() - df['Relative_Strength_6M'].min() + 1e-10)
    
    # Calculate composite score
    df['Composite_Score'] = (
        return_weight * df['Return_6M_Norm'] +
        vol_adj_return_weight * df['Vol_Adj_Return_Norm'] +
        rel_strength_weight * df['Rel_Strength_Norm']
    )
    
    return df


def select_top_stocks(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Select top N stocks based on composite score.
    
    Args:
        df: DataFrame with composite scores
        top_n: Number of top stocks to select
    
    Returns:
        DataFrame with top N stocks
    """
    df_sorted = df.sort_values('Composite_Score', ascending=False)
    return df_sorted.head(top_n)


# ============================================================================
# BACKTESTING MODULE
# ============================================================================

def run_backtest(symbols_list: List[str], 
                index_df: pd.DataFrame,
                start_date: str,
                end_date: str,
                rebalance_frequency: str = 'M',
                top_n: int = 20) -> Tuple[pd.Series, pd.Series, List]:
    """
    Run a backtest with monthly rebalancing.
    
    Args:
        symbols_list: List of all available stock symbols
        index_df: DataFrame with index price data
        start_date: Backtest start date
        end_date: Backtest end date
        rebalance_frequency: Rebalancing frequency ('M' for monthly)
        top_n: Number of stocks in portfolio
    
    Returns:
        Tuple of (portfolio returns, index returns, rebalance dates)
    """
    print("\nRunning backtest...")
    
    # Generate rebalance dates
    date_range = pd.date_range(start=start_date, end=end_date, freq=rebalance_frequency)
    
    portfolio_values = []
    index_values = []
    portfolio_value = 100  # Start with 100
    index_value = 100
    
    current_holdings = []
    rebalance_dates = []
    
    for i, rebalance_date in enumerate(date_range):
        print(f"\nRebalancing on {rebalance_date.date()}...")
        
        # Fetch data up to rebalance date
        period_end = rebalance_date
        period_start = period_end - timedelta(days=365)
        
        # Calculate metrics for all stocks at this rebalance date
        metrics_list = []
        
        # Limit to subset for faster backtesting
        sample_symbols = symbols_list[:100] if len(symbols_list) > 100 else symbols_list
        
        for symbol in sample_symbols:
            try:
                stock_df = yf.Ticker(symbol).history(start=period_start, end=period_end)
                if stock_df is not None and len(stock_df) > 126:  # At least 6 months
                    index_subset = index_df[index_df.index <= period_end].tail(252)
                    metrics = calculate_all_metrics(symbol, stock_df, index_subset)
                    metrics_list.append(metrics)
            except:
                continue
        
        if not metrics_list:
            continue
        
        # Create DataFrame and apply filters
        metrics_df = pd.DataFrame(metrics_list)
        metrics_df = metrics_df.dropna()
        
        if len(metrics_df) == 0:
            continue
        
        filtered_df = apply_filters(metrics_df)
        
        if len(filtered_df) == 0:
            continue
        
        # Calculate composite scores and select top stocks
        scored_df = calculate_composite_score(filtered_df)
        top_stocks_df = select_top_stocks(scored_df, top_n)
        
        # Update holdings
        current_holdings = top_stocks_df['Symbol'].tolist()
        rebalance_dates.append(rebalance_date)
        
        print(f"Selected {len(current_holdings)} stocks for portfolio")
        
        # Calculate returns until next rebalance (or end date)
        if i < len(date_range) - 1:
            next_rebalance = date_range[i + 1]
        else:
            next_rebalance = pd.Timestamp(end_date)
        
        # Equal weight portfolio
        weight = 1.0 / len(current_holdings) if len(current_holdings) > 0 else 0
        
        # Get returns for each holding
        period_returns = []
        for symbol in current_holdings:
            try:
                stock_df = yf.Ticker(symbol).history(start=rebalance_date, end=next_rebalance)
                if stock_df is not None and len(stock_df) > 1:
                    stock_return = (stock_df['Close'].iloc[-1] - stock_df['Close'].iloc[0]) / stock_df['Close'].iloc[0]
                    period_returns.append(stock_return)
            except:
                continue
        
        # Calculate portfolio return for period
        if period_returns:
            portfolio_return = np.mean(period_returns)
            portfolio_value *= (1 + portfolio_return)
        
        # Calculate index return for period
        index_subset = index_df[(index_df.index >= rebalance_date) & (index_df.index <= next_rebalance)]
        if len(index_subset) > 1:
            index_return = (index_subset['Close'].iloc[-1] - index_subset['Close'].iloc[0]) / index_subset['Close'].iloc[0]
            index_value *= (1 + index_return)
        
        portfolio_values.append(portfolio_value)
        index_values.append(index_value)
    
    # Create return series
    portfolio_returns = pd.Series(portfolio_values, index=rebalance_dates[:len(portfolio_values)])
    index_returns = pd.Series(index_values, index=rebalance_dates[:len(index_values)])
    
    return portfolio_returns, index_returns, rebalance_dates


# ============================================================================
# VISUALIZATION MODULE
# ============================================================================

def plot_cumulative_returns(portfolio_returns: pd.Series, index_returns: pd.Series, save_path: str = None):
    """
    Plot cumulative returns comparison.
    
    Args:
        portfolio_returns: Portfolio return series
        index_returns: Index return series
        save_path: Path to save the plot
    """
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_returns.index, portfolio_returns.values, label='Portfolio', linewidth=2)
    plt.plot(index_returns.index, index_returns.values, label='Nifty 50', linewidth=2)
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return (Base 100)')
    plt.title('Portfolio vs Nifty 50 - Cumulative Returns')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def calculate_rolling_volatility(returns: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate rolling volatility.
    
    Args:
        returns: Return series
        window: Rolling window size
    
    Returns:
        Rolling volatility series
    """
    pct_returns = returns.pct_change()
    rolling_vol = pct_returns.rolling(window=window).std() * np.sqrt(252)
    return rolling_vol


def calculate_drawdowns(returns: pd.Series) -> pd.Series:
    """
    Calculate drawdowns from peak.
    
    Args:
        returns: Return series
    
    Returns:
        Drawdown series
    """
    cumulative = returns
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max * 100
    return drawdown


def plot_volatility_and_drawdowns(portfolio_returns: pd.Series, index_returns: pd.Series, save_path: str = None):
    """
    Plot rolling volatility and drawdowns.
    
    Args:
        portfolio_returns: Portfolio return series
        index_returns: Index return series
        save_path: Path to save the plot
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Rolling volatility
    portfolio_vol = calculate_rolling_volatility(portfolio_returns)
    index_vol = calculate_rolling_volatility(index_returns)
    
    ax1.plot(portfolio_vol.index, portfolio_vol.values, label='Portfolio Volatility', linewidth=2)
    ax1.plot(index_vol.index, index_vol.values, label='Nifty 50 Volatility', linewidth=2)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Annualized Volatility')
    ax1.set_title('Rolling Volatility (20-period)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Drawdowns
    portfolio_dd = calculate_drawdowns(portfolio_returns)
    index_dd = calculate_drawdowns(index_returns)
    
    ax2.fill_between(portfolio_dd.index, 0, portfolio_dd.values, alpha=0.3, label='Portfolio Drawdown')
    ax2.fill_between(index_dd.index, 0, index_dd.values, alpha=0.3, label='Nifty 50 Drawdown')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Drawdown (%)')
    ax2.set_title('Drawdowns from Peak')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


# ============================================================================
# PERFORMANCE METRICS MODULE
# ============================================================================

def calculate_cagr(returns: pd.Series) -> float:
    """
    Calculate Compound Annual Growth Rate.
    
    Args:
        returns: Return series
    
    Returns:
        CAGR as percentage
    """
    if len(returns) < 2:
        return np.nan
    
    start_value = returns.iloc[0]
    end_value = returns.iloc[-1]
    
    years = (returns.index[-1] - returns.index[0]).days / 365.25
    
    if years == 0 or start_value == 0:
        return np.nan
    
    cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
    return cagr


def calculate_max_drawdown(returns: pd.Series) -> float:
    """
    Calculate maximum drawdown.
    
    Args:
        returns: Return series
    
    Returns:
        Maximum drawdown as percentage
    """
    drawdowns = calculate_drawdowns(returns)
    max_dd = drawdowns.min()
    return max_dd


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.06) -> float:
    """
    Calculate Sharpe Ratio.
    
    Args:
        returns: Return series
        risk_free_rate: Annual risk-free rate (default 6%)
    
    Returns:
        Sharpe ratio
    """
    if len(returns) < 2:
        return np.nan
    
    pct_returns = returns.pct_change().dropna()
    
    if len(pct_returns) == 0:
        return np.nan
    
    excess_returns = pct_returns - (risk_free_rate / 252)  # Daily risk-free rate
    
    if pct_returns.std() == 0:
        return np.nan
    
    sharpe = (excess_returns.mean() / pct_returns.std()) * np.sqrt(252)
    return sharpe


def calculate_win_rate(returns: pd.Series) -> float:
    """
    Calculate win rate (percentage of positive periods).
    
    Args:
        returns: Return series
    
    Returns:
        Win rate as percentage
    """
    if len(returns) < 2:
        return np.nan
    
    pct_returns = returns.pct_change().dropna()
    
    if len(pct_returns) == 0:
        return np.nan
    
    win_rate = (pct_returns > 0).sum() / len(pct_returns) * 100
    return win_rate


def print_performance_summary(portfolio_returns: pd.Series, index_returns: pd.Series):
    """
    Print performance summary with key metrics.
    
    Args:
        portfolio_returns: Portfolio return series
        index_returns: Index return series
    """
    print("\n" + "="*70)
    print("PERFORMANCE SUMMARY")
    print("="*70)
    
    print("\nPortfolio Performance:")
    print(f"  CAGR:              {calculate_cagr(portfolio_returns):.2f}%")
    print(f"  Max Drawdown:      {calculate_max_drawdown(portfolio_returns):.2f}%")
    print(f"  Sharpe Ratio:      {calculate_sharpe_ratio(portfolio_returns):.2f}")
    print(f"  Win Rate:          {calculate_win_rate(portfolio_returns):.2f}%")
    
    print("\nNifty 50 Performance:")
    print(f"  CAGR:              {calculate_cagr(index_returns):.2f}%")
    print(f"  Max Drawdown:      {calculate_max_drawdown(index_returns):.2f}%")
    print(f"  Sharpe Ratio:      {calculate_sharpe_ratio(index_returns):.2f}")
    print(f"  Win Rate:          {calculate_win_rate(index_returns):.2f}%")
    
    print("\nOutperformance:")
    portfolio_cagr = calculate_cagr(portfolio_returns)
    index_cagr = calculate_cagr(index_returns)
    if not np.isnan(portfolio_cagr) and not np.isnan(index_cagr):
        print(f"  Alpha:             {portfolio_cagr - index_cagr:.2f}%")
    
    print("="*70)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function.
    """
    print("="*70)
    print("NIFTY ALPHA SCREEN - Stock Screening & Backtesting System")
    print("="*70)
    
    # Step 1: Fetch stock symbols
    symbols = get_nifty_500_symbols()
    print(f"\nTotal symbols to analyze: {len(symbols)}")
    
    # Step 2: Fetch Nifty 50 data for comparison
    print("\nFetching Nifty 50 index data...")
    nifty_df = fetch_nifty_50_data(period="2y")
    
    if nifty_df is None or nifty_df.empty:
        print("Error: Could not fetch Nifty 50 data. Exiting.")
        return
    
    print(f"Nifty 50 data fetched: {len(nifty_df)} days")
    
    # Step 3: Calculate metrics for all stocks
    print("\nCalculating metrics for all stocks...")
    metrics_list = []
    
    # Limit to first 100 stocks for demonstration (change to len(symbols) for full run)
    sample_size = min(100, len(symbols))
    print(f"Analyzing {sample_size} stocks (use full list for production)...")
    
    for i, symbol in enumerate(symbols[:sample_size]):
        if (i + 1) % 10 == 0:
            print(f"Progress: {i+1}/{sample_size} stocks processed")
        
        stock_df = fetch_stock_data(symbol, period="2y")
        
        if stock_df is not None and len(stock_df) > 126:  # At least 6 months of data
            metrics = calculate_all_metrics(symbol, stock_df, nifty_df)
            metrics_list.append(metrics)
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    # Step 4: Create DataFrame with all metrics
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df = metrics_df.dropna()
    
    print(f"\nStocks with complete data: {len(metrics_df)}")
    
    if len(metrics_df) == 0:
        print("Error: No stocks with complete data. Exiting.")
        return
    
    # Step 5: Apply filters
    filtered_df = apply_filters(metrics_df)
    
    if len(filtered_df) == 0:
        print("Error: No stocks passed filters. Exiting.")
        return
    
    # Step 6: Calculate composite scores and rank
    print("\nCalculating composite scores...")
    scored_df = calculate_composite_score(filtered_df)
    
    # Step 7: Select top 20 stocks
    top_20 = select_top_stocks(scored_df, top_n=20)
    
    # Step 8: Display top 20 stocks
    print("\n" + "="*70)
    print("TOP 20 STOCKS")
    print("="*70)
    
    display_columns = [
        'Symbol', 'Current_Price', 'Retracement_52W', 
        'Return_6M', 'Vol_Adj_Return_6M', 'Relative_Strength_6M',
        'Composite_Score'
    ]
    
    print(top_20[display_columns].to_string(index=False))
    print("="*70)
    
    # Step 9: Run backtest
    print("\n" + "="*70)
    print("BACKTESTING")
    print("="*70)
    
    # Define backtest period (last 1 year)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    portfolio_returns, index_returns, rebalance_dates = run_backtest(
        symbols_list=symbols[:sample_size],
        index_df=nifty_df,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        rebalance_frequency='M',
        top_n=20
    )
    
    # Step 10: Print performance summary
    if len(portfolio_returns) > 0 and len(index_returns) > 0:
        print_performance_summary(portfolio_returns, index_returns)
        
        # Step 11: Generate charts
        print("\nGenerating charts...")
        
        plot_cumulative_returns(portfolio_returns, index_returns, 
                               save_path='cumulative_returns.png')
        
        plot_volatility_and_drawdowns(portfolio_returns, index_returns,
                                      save_path='volatility_drawdowns.png')
        
        print("\nCharts saved:")
        print("  - cumulative_returns.png")
        print("  - volatility_drawdowns.png")
    else:
        print("\nInsufficient backtest data to generate performance metrics and charts.")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
