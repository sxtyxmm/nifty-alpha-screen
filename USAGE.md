# Quick Start Guide

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Internet connection (for fetching real stock data)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sxtyxmm/nifty-alpha-screen.git
   cd nifty-alpha-screen
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the Main Analysis (Requires Internet)

```bash
python nifty_alpha_screen.py
```

This will:
- Fetch Nifty stock symbols
- Download historical stock data from Yahoo Finance
- Calculate metrics for all stocks
- Apply filters and rank stocks
- Display top 20 stocks
- Run a backtest
- Generate performance charts
- Print performance summary

**Expected Output:**
- Console output with top 20 stocks and metrics
- `cumulative_returns.png` - Portfolio vs Nifty 50 comparison
- `volatility_drawdowns.png` - Volatility and drawdown analysis

### Run the Demo (No Internet Required)

```bash
python demo.py
```

This demonstrates the system with synthetic data and generates:
- Console output showing the screening process
- `demo_results.png` - Simulated backtest results

## Understanding the Output

### Top 20 Stocks Table

The table shows:
- **Symbol**: Stock ticker symbol
- **Current_Price**: Latest closing price
- **Retracement_52W**: % decline from 52-week high (lower is better)
- **Return_6M**: 6-month total return (%)
- **Vol_Adj_Return_6M**: Risk-adjusted return (Sharpe-like ratio)
- **Relative_Strength_6M**: Outperformance vs Nifty 50 (%)
- **Composite_Score**: Overall ranking score (0-1, higher is better)

### Performance Summary

Key metrics explained:

- **CAGR** (Compound Annual Growth Rate): Annualized return
- **Max Drawdown**: Largest peak-to-trough decline (risk measure)
- **Sharpe Ratio**: Risk-adjusted return (higher is better, >1 is good)
- **Win Rate**: % of profitable periods
- **Alpha**: Outperformance vs benchmark

### Charts

1. **Cumulative Returns**: Shows portfolio growth vs Nifty 50 over time
2. **Rolling Volatility**: 20-period volatility to assess risk changes
3. **Drawdowns**: Visual representation of portfolio declines from peaks

## Customization

### Analyze More Stocks

Edit `nifty_alpha_screen.py` line ~756:

```python
# Change this:
sample_size = min(100, len(symbols))

# To this (for all stocks):
sample_size = len(symbols)
```

### Change Number of Stocks in Portfolio

Edit line ~779:

```python
# Change from 20 to your preferred number:
top_20 = select_top_stocks(scored_df, top_n=30)
```

### Adjust Scoring Weights

Edit `calculate_composite_score()` function (~350):

```python
def calculate_composite_score(df: pd.DataFrame, 
                              return_weight: float = 0.5,      # Changed from 0.4
                              vol_adj_return_weight: float = 0.3,  # Same
                              rel_strength_weight: float = 0.2) -> pd.DataFrame:  # Changed from 0.3
```

### Change Rebalancing Frequency

Edit `run_backtest()` call line ~795:

```python
# Change 'M' (monthly) to 'W' (weekly) or 'Q' (quarterly):
rebalance_frequency='W',
```

### Adjust Filters

Edit `apply_filters()` function (~292):

```python
# Change retracement threshold (currently 30%):
df_filtered = df[df['Retracement_52W'] <= 20].copy()

# Change return percentile (currently top 50%):
return_threshold = df_filtered['Return_6M'].quantile(0.7)  # Top 30%
```

## Troubleshooting

### Issue: "Could not fetch stock data"

**Cause**: Internet connection issue or Yahoo Finance API temporarily down

**Solution**:
- Check internet connection
- Try again after a few minutes
- Use the demo script to verify functionality

### Issue: "No stocks passed filters"

**Cause**: Filters are too strict for current market conditions

**Solution**:
- Relax the retracement filter (increase from 30% to 40%)
- Lower the return percentile threshold
- Check if data is being fetched correctly

### Issue: Charts not displaying

**Cause**: Running in headless environment or matplotlib backend issue

**Solution**:
- Charts are automatically saved as PNG files
- Check for `cumulative_returns.png` and `volatility_drawdowns.png` in the directory
- Open the PNG files directly

### Issue: Script takes too long

**Cause**: Analyzing too many stocks

**Solution**:
- Reduce `sample_size` variable
- The script includes rate limiting to respect API guidelines
- For production use, consider caching data

## Tips for Best Results

1. **Run during market hours**: Data is most up-to-date during trading hours
2. **Backtest period**: Longer backtests (2+ years) provide more reliable results
3. **Review regularly**: Rerun weekly/monthly to update rankings
4. **Combine with fundamental analysis**: This is a screening tool, not a complete investment system
5. **Paper trade first**: Test the strategy without real money initially

## Example Output

```
======================================================================
TOP 20 STOCKS
======================================================================
Symbol         Current_Price  Retracement_52W  Return_6M  Vol_Adj_Return_6M  ...
RELIANCE.NS           2450.50             5.23      25.40              1.25  ...
TCS.NS                3550.75             8.15      22.10              1.15  ...
...
======================================================================

PERFORMANCE SUMMARY
======================================================================
Portfolio Performance:
  CAGR:              18.50%
  Max Drawdown:      -12.30%
  Sharpe Ratio:      1.45
  Win Rate:          65.00%

Nifty 50 Performance:
  CAGR:              12.20%
  Max Drawdown:      -15.40%
  Sharpe Ratio:      0.95
  Win Rate:          58.33%

Outperformance:
  Alpha:             6.30%
======================================================================
```

## Next Steps

1. Review the top 20 stocks list
2. Conduct fundamental analysis on selected stocks
3. Check company financials and news
4. Create a watchlist for further monitoring
5. Consider position sizing and risk management
6. Implement proper portfolio allocation

## Support

For issues or questions:
- Check the main README.md for detailed documentation
- Review the code comments for implementation details
- Refer to the problem statement for methodology

## Disclaimer

This tool is for educational purposes only. Past performance does not guarantee future results. Always conduct your own research and consult with a financial advisor before making investment decisions.
