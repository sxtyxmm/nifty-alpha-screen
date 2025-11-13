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

Run the stock screener:
```bash
python stock_screener.py
```

The script will:
1. Fetch live data for all Nifty 200 stocks
2. Apply both strategies independently
3. Generate two CSV files with results:
   - `strategy1_momentum_retracement.csv` - Top 20 momentum stocks
   - `strategy2_ema_retracement.csv` - EMA retracement opportunities

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

## License

MIT License
