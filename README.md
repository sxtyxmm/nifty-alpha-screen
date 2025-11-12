# Nifty Alpha Screen

Quant-based Nifty screener identifying top 20 high-momentum, low-risk outperformers using a hybrid momentum-EMA trading strategy.

## 📖 Overview

This repository implements a sophisticated two-stage stock selection strategy for Indian equities:

### Strategy 1: Momentum-Based Selection
- Filters stocks by 52-week high retracement (≤30%)
- Calculates composite score based on:
  - 40% 6-month return
  - 30% volatility-adjusted return
  - 30% relative strength vs Nifty
- Selects top 20 stocks

### Strategy 2: EMA-Based Entry Timing
- Uses 44-day EMA for entry signals
- Enters when:
  - EMA is rising (last 5 days)
  - Price has retraced to touch/cross EMA (±1%)

### Exit Rules
- Stock drops out of top 20 momentum list
- Price closes >2% below 44-day EMA

### Rebalancing
- Monthly momentum recalculation
- Daily EMA entry checks

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sxtyxmm/nifty-alpha-screen.git
cd nifty-alpha-screen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Strategy

Execute the main script:
```bash
python hybrid_momentum_ema.py
```

This will:
- Fetch historical data for Nifty stocks (using free Yahoo Finance API)
- Calculate momentum metrics and composite scores
- Identify top 20 momentum stocks
- Apply EMA entry filters
- Run 5-year backtest
- Generate performance metrics and visualizations

## 📊 Output

The script generates the following files in the `output/` directory:

### CSV Files
- `top_20_momentum_stocks.csv` - Current top 20 stocks by momentum score
- `current_buy_list.csv` - Stocks with active EMA entry signals
- `portfolio_values.csv` - Daily portfolio values during backtest
- `trades_history.csv` - Complete trade log with entry/exit details

### Visualizations
- `momentum_distribution.png` - Distribution of momentum metrics
- `equity_curve.png` - Portfolio performance vs Nifty 50 benchmark
- `drawdown_chart.png` - Portfolio drawdown analysis

## 📈 Performance Metrics

The backtest reports:
- **CAGR** - Compound Annual Growth Rate
- **Sharpe Ratio** - Risk-adjusted returns
- **Maximum Drawdown** - Largest peak-to-trough decline
- **Win Rate** - Percentage of profitable trades
- **Total Return** - Overall return percentage

## 🔧 Configuration

Key parameters can be modified in the script:

```python
BACKTEST_YEARS = 5          # Backtest duration
INITIAL_CAPITAL = 100000    # Starting portfolio value
EMA_PERIOD = 44             # EMA period for entry signals
TOP_N = 20                  # Number of stocks to select
```

## 📚 Data Sources

This implementation uses **only free data sources**:
- **Yahoo Finance** (via yfinance library) - Historical stock data
- **NSE India** - Stock universe (Nifty 200/500)

No paid APIs or data providers required!

## 🛠️ Technical Stack

- **Python 3.8+**
- **pandas** - Data manipulation
- **numpy** - Numerical computations
- **yfinance** - Stock data fetching
- **ta** - Technical indicators
- **matplotlib** - Visualizations

## 📝 Requirements

See `requirements.txt` for complete dependency list.

## ⚠️ Disclaimer

This strategy is for educational and research purposes only. Past performance does not guarantee future results. Always do your own research and consult with a financial advisor before making investment decisions.

## 📄 License

MIT License - Feel free to use and modify for your own research.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
