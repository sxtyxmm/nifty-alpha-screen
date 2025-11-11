# Nifty Alpha Screen

A quantitative stock screening and backtesting system for identifying high-momentum, low-risk outperformers in the Indian stock market (Nifty 200/500 universe).

## Features

- **Automated Data Fetching**: Fetches historical stock data from Yahoo Finance for Nifty stocks
- **Comprehensive Metrics**: Calculates retracement from 52-week high, returns (3M/6M), volatility, volatility-adjusted returns, and relative strength vs Nifty 50
- **Multi-Stage Filtering**: 
  - Retracement ≤ 30% from 52-week high
  - Top percentile of recent returns
  - Positive relative strength vs Nifty 50
- **Composite Scoring**: Weighted ranking system combining return, risk-adjusted return, and relative strength
- **Backtesting Engine**: Monthly rebalancing with performance tracking
- **Visualization**: Charts for cumulative returns, rolling volatility, and drawdowns
- **Performance Metrics**: CAGR, Max Drawdown, Sharpe Ratio, and Win Rate

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sxtyxmm/nifty-alpha-screen.git
cd nifty-alpha-screen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
python nifty_alpha_screen.py
```

The script will:
1. Fetch Nifty stock symbols and historical data
2. Calculate metrics for all stocks
3. Apply filters to identify quality stocks
4. Rank stocks using composite scoring
5. Display top 20 stocks with detailed metrics
6. Run a backtest with monthly rebalancing
7. Generate performance charts and metrics

## Output

The script generates:
- **Console Output**: Top 20 stocks table and performance summary
- **Charts**:
  - `cumulative_returns.png`: Portfolio vs Nifty 50 comparison
  - `volatility_drawdowns.png`: Rolling volatility and drawdown analysis

## Performance Metrics

The system calculates and displays:
- **CAGR**: Compound Annual Growth Rate
- **Max Drawdown**: Maximum peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure
- **Win Rate**: Percentage of positive return periods
- **Alpha**: Outperformance vs Nifty 50

## Methodology

### Stock Selection Process

1. **Data Collection**: Fetch 2 years of historical data for Nifty stocks
2. **Metric Calculation**:
   - 52-week high retracement
   - 3-month and 6-month total returns
   - Annualized volatility
   - Volatility-adjusted return (Sharpe-like ratio)
   - Relative strength vs Nifty 50

3. **Filtering**:
   - Keep stocks within 30% of 52-week high (strong trend)
   - Keep top 50% of stocks by 6-month return (momentum)
   - Keep stocks outperforming Nifty 50 (relative strength)

4. **Scoring & Ranking**:
   - Composite score = 0.4 × Return + 0.3 × Vol-Adj Return + 0.3 × Rel Strength
   - Select top 20 stocks

### Backtesting

- **Frequency**: Monthly rebalancing
- **Portfolio Construction**: Equal-weight top 20 stocks
- **Benchmark**: Nifty 50 index
- **Period**: Last 1 year (configurable)

## Customization

You can modify key parameters in the script:

```python
# In main() function:
sample_size = min(100, len(symbols))  # Number of stocks to analyze
top_n = 20  # Number of stocks in portfolio

# In calculate_composite_score():
return_weight = 0.4
vol_adj_return_weight = 0.3
rel_strength_weight = 0.3

# In run_backtest():
rebalance_frequency = 'M'  # 'M' for monthly, 'W' for weekly
```

## Requirements

- Python 3.7+
- pandas >= 2.0.0
- numpy >= 1.24.0
- yfinance >= 0.2.28
- matplotlib >= 3.7.0
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0

## Notes

- The script uses free data from Yahoo Finance (no paid APIs required)
- By default, analyzes 100 stocks for faster execution (modify `sample_size` for full analysis)
- Includes rate limiting to respect API guidelines
- Uses fallback stock list if web scraping fails

## Disclaimer

This tool is for educational and research purposes only. It does not constitute financial advice. Past performance does not guarantee future results. Always conduct your own research and consult with a financial advisor before making investment decisions.

## License

MIT License - see LICENSE file for details
