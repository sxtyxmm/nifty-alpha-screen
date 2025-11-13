# Nifty Alpha Screen - Financial Data Automation Assistant

A Python-based stock screening tool that implements two independent trading strategies to identify high-potential stocks from the NSE (National Stock Exchange of India).

## Overview

This tool fetches live market data from NSE/BSE and applies quantitative filters to identify stocks based on:
- **Strategy 1**: Momentum + Retracement Strategy (Top 20 stocks)
- **Strategy 2**: EMA Retracement Strategy (All qualifying stocks)

## Features

- ✅ Automated fetching of Nifty 200 stock data
- ✅ Real-time market data from Yahoo Finance (NSE)
- ✅ Two independent trading strategies
- ✅ CSV output for easy analysis
- ✅ Comprehensive risk metrics (Sharpe ratio, Sortino ratio)
- ✅ Relative strength analysis vs Nifty index

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sxtyxmm/nifty-alpha-screen.git
cd nifty-alpha-screen
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the stock screener with live market data:
```bash
python stock_screener.py
```

The script will:
1. Fetch live data for all Nifty 200 stocks
2. Apply both strategies independently
3. Generate two CSV files with results:
   - `strategy1_momentum_retracement.csv` - Top 20 momentum stocks
   - `strategy2_ema_retracement.csv` - EMA retracement opportunities

### Test Mode (Demo with Sample Data)

If you want to test the tool without fetching live data:
```bash
python test_screener.py
```

This will generate sample data and demonstrate the strategies.

### Programmatic Usage

Use the screener in your own Python code:
```bash
python example_usage.py
```

Or import the modules directly:
```python
from stock_screener import StockDataFetcher, Strategy1, Strategy2

fetcher = StockDataFetcher(stock_universe='nifty200')
strategy1 = Strategy1(fetcher)
results = strategy1.run()
```

See `example_usage.py` for more detailed examples.

## Strategy Details

### Strategy 1: Momentum + Retracement Strategy

Identifies top 20 stocks based on:
1. **Retracement Filter**: Stocks within 30% of 52-week high
2. **Return Filter**: Positive returns over 3-6 months
3. **Risk-Adjusted Returns**: Sharpe and Sortino ratios
4. **Relative Strength**: Outperformance vs Nifty index
5. **Ranking**: Combined score from all metrics

**Output**: Top 20 ranked stocks with detailed metrics

### Strategy 2: EMA Retracement Strategy

Identifies stocks where:
1. **Rising EMA**: 44-day EMA is trending upward
2. **Price Retracement**: Current price is near EMA (±1%)

**Output**: All stocks meeting the criteria

## Output Format

Both strategies output CSV files with the following information:

**Strategy 1 Columns**:
- Rank
- Symbol
- Retracement from 52-week high (%)
- 3-month return (%)
- 6-month return (%)
- Sharpe Ratio
- Sortino Ratio
- Relative Strength vs Nifty (%)
- Combined Score

**Strategy 2 Columns**:
- Symbol
- Current Price
- 44-day EMA
- Distance from EMA (%)
- EMA Change over 5 days (%)

## Requirements

- Python 3.7+
- yfinance
- pandas
- numpy
- nselib

## Notes

- The tool uses Yahoo Finance API for NSE data
- Data is fetched in real-time during market hours
- Processing time depends on network speed and market data availability
- Stocks with insufficient data are automatically filtered out
- CSV files are automatically ignored by git (see `.gitignore`)

## Limitations & Future Enhancements

**Current Limitations:**
- Relies on Yahoo Finance API which may have rate limits or access restrictions
- Stock list is hardcoded (top Nifty 200 stocks)
- No automatic rebalancing or tracking over time
- Single-threaded data fetching (can be slow for large universes)

**Potential Enhancements:**
- Add support for fetching official Nifty 200/500 lists from NSE
- Implement parallel data fetching for faster processing
- Add backtesting capabilities to validate strategy performance
- Create a web dashboard for visualization
- Add email/notification alerts for strategy triggers
- Support for custom stock universes and sectors
- Historical tracking and performance monitoring

## Contributing

Feel free to submit issues or pull requests to improve the tool!

## License

MIT License
