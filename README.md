# nifty-alpha-screen

Quant-based stock analyzer for Indian markets that provides comprehensive investment recommendations based on fundamentals, technical indicators (EMA-44), and NSE delivery data.

## Features

- **Fundamental Analysis**: Fetches key metrics including Market Cap, P/E ratios, Price to Book, Debt to Equity, ROE, and Beta
- **Technical Analysis**: Calculates EMA-44 and analyzes price position and trend
- **Delivery Data Analysis**: Parses NSE bhavcopy data to assess genuine accumulation
- **Smart Scoring**: Combines all signals into a final INVEST/HOLD/AVOID recommendation
- **Comprehensive Reports**: Presents data in easy-to-read tables with clear explanations

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

### Basic Usage (without delivery data)

```bash
python stock_analyzer.py RELIANCE
```

### With Delivery Data

```bash
python stock_analyzer.py RELIANCE sample_bhavcopy.csv
```

### Examples

Analyze Reliance Industries:
```bash
python stock_analyzer.py RELIANCE.NS
```

Analyze TCS with delivery data:
```bash
python stock_analyzer.py TCS /path/to/bhavcopy.csv
```

## Output Format

The analyzer provides a comprehensive report with:

1. **Key Fundamentals Table**: Market Cap, P/E, P/B, D/E, ROE, Beta
2. **EMA-44 Trend Analysis**: Current position vs EMA, slope, trend direction
3. **NSE Delivery Data**: Deliverable quantity, percentage, and 3-day trend
4. **Fundamental Grade**: A-D rating based on key metrics
5. **Final Verdict**: INVEST/HOLD/AVOID with score (-2 to +3) and confidence level

## Scoring Methodology

The analyzer uses a multi-factor scoring system:

- **Price vs EMA-44**: +1 if above (bullish), -1 if below (bearish)
- **EMA Slope**: +1 if rising >1%, -1 if falling <-1%
- **Delivery %**: +1 if >35% (high accumulation)
- **P/E Ratio**: +0.5 if reasonable (<25), -0.5 if high (>40)
- **ROE**: +0.5 if >15%, -0.5 if negative

**Final Score Range**: -2.0 to +3.0

**Verdict Mapping**:
- Score ≥ 2.0: INVEST (High Confidence)
- Score ≥ 1.0: INVEST (Moderate Confidence)
- Score ≥ 0.0: HOLD (Moderate Confidence)
- Score ≥ -1.0: AVOID (Moderate Confidence)
- Score < -1.0: AVOID (High Confidence)

## NSE Delivery Data

To include delivery data analysis, provide a bhavcopy CSV file with the following columns:
- `SYMBOL`: Stock symbol
- `TTL_TRD_QNTY`: Total traded quantity
- `DELIV_QTY`: Deliverable quantity
- `DELIV_PER`: Delivery percentage (optional, will be calculated)

You can download bhavcopy files from NSE India's website.

### Sample Bhavcopy Format

A sample bhavcopy file (`sample_bhavcopy.csv`) is included in the repository for reference.

## Requirements

- Python 3.8+
- yfinance
- pandas
- numpy
- tabulate

## How It Works

1. **Data Collection**: Fetches real-time fundamentals from Yahoo Finance
2. **EMA Calculation**: Computes 44-day exponential moving average on adjusted close prices
3. **Trend Analysis**: Evaluates EMA slope over 5 days to confirm trend strength
4. **Delivery Analysis**: Parses NSE bhavcopy to assess institutional interest
5. **Smart Scoring**: Combines technical, fundamental, and delivery signals
6. **Recommendation**: Provides actionable INVEST/HOLD/AVOID verdict with reasoning

## Limitations

- Relies on Yahoo Finance data availability
- NSE delivery data requires manual CSV input
- Forward P/E may not be available for all stocks
- Historical data limited to what Yahoo Finance provides

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this tool for your investment research.

## Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.
