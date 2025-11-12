# Quick Reference Card

## Installation
```bash
pip install -r requirements.txt
```

## Basic Usage
```bash
# With internet (real data)
python hybrid_momentum_ema.py

# Demo mode (simulated data)
python demo_strategy.py

# Run tests
python test_strategy.py
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| BACKTEST_YEARS | 5 | Years of historical data |
| INITIAL_CAPITAL | 100000 | Starting portfolio (₹) |
| EMA_PERIOD | 44 | EMA period for signals |
| TOP_N | 20 | Number of stocks to select |
| RETRACEMENT_MAX | 30% | Max pullback from 52w high |
| EMA_TOUCH_TOLERANCE | ±1% | Price-to-EMA distance |
| EXIT_THRESHOLD | -2% | Price below EMA for exit |

## Composite Score Weights
- **40%** - 6-month return
- **30%** - Volatility-adjusted return
- **30%** - Relative strength vs Nifty

## Entry Criteria
1. ✓ Top 20 by momentum score
2. ✓ Retracement ≤ 30% from 52w high
3. ✓ 44-day EMA rising (last 5 days)
4. ✓ Price within ±1% of EMA

## Exit Criteria
1. ✗ Drops out of top 20 momentum list
2. ✗ Price closes >2% below 44-day EMA

## Output Files

### CSV Files (output/)
- `top_20_momentum_stocks.csv` - Top stocks by score
- `current_buy_list.csv` - Stocks with entry signals
- `portfolio_values.csv` - Daily portfolio tracking
- `trades_history.csv` - All buy/sell trades

### Charts (output/)
- `momentum_distribution.png` - Score breakdown
- `equity_curve.png` - Strategy vs Nifty
- `drawdown_chart.png` - Risk analysis

## Performance Metrics

| Metric | Formula | Good Value |
|--------|---------|------------|
| CAGR | Annualized return | > 15% |
| Sharpe Ratio | Return/Risk | > 1.0 |
| Max Drawdown | Worst decline | > -20% |
| Win Rate | % profitable trades | > 55% |

## Common Commands

```python
# Load results
import pandas as pd
df = pd.read_csv('output/top_20_momentum_stocks.csv')
buy_list = pd.read_csv('output/current_buy_list.csv')
trades = pd.read_csv('output/trades_history.csv')

# Get buy signals
print(buy_list[['symbol', 'current_price', 'ema']])

# Analyze trades
profitable = trades[trades['pnl'] > 0]
print(f"Win rate: {len(profitable)/len(trades)*100:.2f}%")
```

## Customization

### Change stock universe
Edit `get_nifty_500_symbols()` in `hybrid_momentum_ema.py`

### Adjust composite weights
Edit `calculate_composite_score()` function

### Modify EMA period
Change `ema_period=44` in function calls

### Add filters
Add conditions in `select_top_stocks()` or `apply_ema_filter()`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No internet | Use `demo_strategy.py` |
| Too slow | Reduce stock universe or backtest period |
| No buy signals | Normal - wait for pullbacks to EMA |
| Import errors | Run `pip install -r requirements.txt` |

## Example Workflow

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run strategy
python hybrid_momentum_ema.py

# 3. Review top stocks
cat output/top_20_momentum_stocks.csv

# 4. Check buy signals
cat output/current_buy_list.csv

# 5. View performance
# Open output/*.png files
```

## Strategy Logic Flow

```
1. Fetch Nifty stock data (5 years)
   ↓
2. Calculate momentum metrics
   - 52w high retracement
   - 6M/3M returns
   - Volatility-adjusted return
   - Relative strength vs Nifty
   ↓
3. Filter: retracement ≤ 30%
   ↓
4. Rank by composite score
   ↓
5. Select top 20 stocks
   ↓
6. Apply EMA filter (44-day)
   - Check rising trend
   - Check price near EMA
   ↓
7. Generate buy/sell signals
   ↓
8. Backtest strategy (5 years)
   ↓
9. Calculate metrics & visualize
   ↓
10. Output results to CSV/PNG
```

## Important Notes

⚠️ **For Educational Use Only**
- Not financial advice
- Past performance ≠ future results
- Consult a financial advisor

💡 **Best Practices**
- Review buy list daily
- Rebalance monthly
- Track all trades
- Monitor drawdowns
- Adjust for your risk tolerance

🔒 **Data Privacy**
- No data sent to external servers
- All processing done locally
- Uses only public market data

## Resources

- **README.md** - Overview and quick start
- **USAGE.md** - Detailed usage guide
- **TECHNICAL.md** - Technical documentation
- **requirements.txt** - Dependencies

## Version

Current: v1.0 (2025-11-12)

## License

MIT License - Free to use and modify
