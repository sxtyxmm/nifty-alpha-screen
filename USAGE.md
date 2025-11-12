# Usage Examples

This document provides quick usage examples for the Nifty Alpha Screen strategy.

## Basic Usage

### Running with Real Market Data

If you have internet access:

```bash
python hybrid_momentum_ema.py
```

This will:
1. Fetch 5 years of historical data for Nifty stocks from Yahoo Finance
2. Calculate momentum metrics and select top 20 stocks
3. Apply EMA entry filters
4. Run backtest simulation
5. Generate performance reports and visualizations

Expected runtime: 5-15 minutes depending on internet speed.

### Running Demo Mode

To test the strategy logic without internet access:

```bash
python demo_strategy.py
```

This uses simulated stock data to demonstrate the strategy functionality.

Expected runtime: ~10 seconds.

## Output Files

All outputs are saved in the `output/` directory:

### CSV Files

- **top_20_momentum_stocks.csv** - Current top 20 stocks ranked by momentum
  - Columns: rank, symbol, composite_score, returns_6m, vol_adj_return, relative_strength, etc.

- **current_buy_list.csv** - Stocks with active EMA entry signals
  - Columns: symbol, rank, current_price, ema, price_to_ema_pct

- **portfolio_values.csv** - Daily portfolio values during backtest
  - Columns: date, portfolio_value, cash, positions

- **trades_history.csv** - Complete trade log
  - Columns: date, symbol, action (BUY/SELL), price, shares, pnl, pnl_pct, reason

### Visualizations

- **momentum_distribution.png** - Charts showing:
  - Composite score ranking
  - 6-month returns
  - Volatility-adjusted returns
  - Relative strength vs Nifty

- **equity_curve.png** - Portfolio performance vs Nifty 50 benchmark

- **drawdown_chart.png** - Portfolio drawdown analysis

## Customization

### Adjusting Parameters

Edit the configuration section in `hybrid_momentum_ema.py`:

```python
# In the main() function:
BACKTEST_YEARS = 5          # Change backtest duration
INITIAL_CAPITAL = 100000    # Change starting capital

# In select_top_stocks() function:
top_n = 20                  # Change number of stocks to select

# In calculate_ema_signals() function:
ema_period = 44             # Change EMA period
```

### Modifying Stock Universe

To use a different stock list, edit the `get_nifty_500_symbols()` function:

```python
def get_nifty_500_symbols():
    # Option 1: Load from CSV
    df = pd.read_csv('nifty_stocks.csv')
    return [f"{symbol}.NS" for symbol in df['Symbol'].values]
    
    # Option 2: Hardcode your list
    my_stocks = ['RELIANCE', 'TCS', 'INFY', ...]
    return [f"{symbol}.NS" for symbol in my_stocks]
```

### Changing Composite Score Weights

In the `calculate_composite_score()` function:

```python
def calculate_composite_score(metrics):
    # Adjust these weights (must sum to 1.0 after dividing by 100)
    score = (
        0.40 * metrics['returns_6m'] +           # 6-month return
        0.30 * metrics['vol_adj_return'] +       # Volatility-adjusted return
        0.30 * metrics['relative_strength'] * 100 # Relative strength
    )
    return score
```

## Interpreting Results

### Momentum Metrics

- **Retracement %**: How far the stock is from its 52-week high (filter: ≤30%)
- **Returns 6M**: Percentage return over past 6 months
- **Vol Adj Return**: Return divided by volatility (risk-adjusted performance)
- **Relative Strength**: Stock return relative to Nifty 50 (>1.0 means outperforming)

### EMA Signals

- **EMA Rising**: EMA[t] > EMA[t-1] for last 5 days (confirms uptrend)
- **Price Near EMA**: Current price within ±1% of EMA (pullback opportunity)
- **Entry Signal**: Both conditions met (buy opportunity)
- **Exit Signal**: Price closes >2% below EMA (exit position)

### Performance Metrics

- **CAGR**: Compound Annual Growth Rate (annualized return)
- **Sharpe Ratio**: Risk-adjusted returns (>1.0 is good, >2.0 is excellent)
- **Max Drawdown**: Largest peak-to-trough decline (lower is better)
- **Win Rate**: Percentage of profitable trades (>50% is good)

## Troubleshooting

### No Data Retrieved

If you get "Failed to get ticker" errors:
- Check internet connection
- Verify stock symbols are correct (should end with .NS for NSE)
- Yahoo Finance may be temporarily unavailable - try again later
- Some stocks may be delisted - the script will skip them

### Insufficient Stock Data

Error: "Insufficient stock data. Need at least 20 stocks."

Solution:
- Increase the stock universe in `get_nifty_500_symbols()`
- Reduce the backtest period
- Check if Yahoo Finance is accessible

### Memory Issues

If running on a machine with limited RAM:
- Reduce `BACKTEST_YEARS`
- Reduce the number of stocks in the universe
- Run the demo version instead

## Advanced Usage

### Scheduled Daily Execution

To get daily signals, set up a cron job (Linux/Mac):

```bash
# Edit crontab
crontab -e

# Add line to run daily at 6 PM IST
0 18 * * * cd /path/to/nifty-alpha-screen && python hybrid_momentum_ema.py > logs/daily_$(date +\%Y\%m\%d).log 2>&1
```

### Integration with Trading Systems

The strategy outputs can be integrated with automated trading:

```python
# Read the buy list
import pandas as pd
buy_list = pd.read_csv('output/current_buy_list.csv')

# Send orders to your broker API
for _, row in buy_list.iterrows():
    symbol = row['symbol'].replace('.NS', '')  # Remove .NS suffix
    price = row['current_price']
    # place_order(symbol, 'BUY', quantity, price)
```

## Example Output

When you run the script successfully, you should see output like:

```
======================================================================
HYBRID MOMENTUM-EMA TRADING STRATEGY
======================================================================

Backtest Period: 2020-05-17 to 2025-11-12
Stock Universe: 100 Nifty stocks

Fetching data for 100 stocks...
✓ Successfully fetched data for 87 stocks

Calculating momentum metrics for all stocks...
✓ Selected top 20 stocks based on momentum

📊 Top 20 Momentum Stocks:
 rank      symbol  composite_score  returns_6m  vol_adj_return
    1  RELIANCE.NS        15.23        22.5           1.85
    2      TCS.NS        14.87        19.3           1.92
...

✅ BUY LIST (EMA Entry Signals):
     symbol  rank  current_price     ema
RELIANCE.NS     1        2450.50  2440.20
    INFY.NS     5        1580.75  1575.30

======================================================================
BACKTEST PERFORMANCE METRICS
======================================================================
CAGR:                  18.45%
Sharpe Ratio:          1.32
Maximum Drawdown:      -15.23%
Win Rate:              62.50%
Total Trades:          145
======================================================================
```
