# Strategy Technical Documentation

This document provides detailed technical information about the Hybrid Momentum-EMA Trading Strategy.

## Strategy Architecture

### Two-Stage Selection Process

```
Stage 1: Momentum Selection
    ↓
Filter by 52-week retracement (≤30%)
    ↓
Calculate momentum metrics
    ↓
Compute composite score
    ↓
Rank and select Top 20
    ↓
Stage 2: EMA Entry Timing
    ↓
Calculate 44-day EMA
    ↓
Check EMA rising trend
    ↓
Check price near EMA
    ↓
Generate entry signals
```

## Detailed Methodology

### 1. Momentum Metrics Calculation

#### 52-Week High Retracement
```
retracement_pct = ((52w_high - current_price) / 52w_high) * 100
```

- Measures how far the stock has pulled back from its yearly peak
- Filter: Only consider stocks with retracement ≤ 30%
- Rationale: Stocks near their highs show strength and momentum

#### Returns Calculation
```
returns_3m = ((current_price / price_3m_ago) - 1) * 100
returns_6m = ((current_price / price_6m_ago) - 1) * 100
```

- 3-month and 6-month percentage returns
- Used for ranking and composite score
- Higher returns indicate stronger momentum

#### Volatility-Adjusted Return
```
daily_returns = price.pct_change()
volatility = std_dev(daily_returns, 60-day) * sqrt(252)
vol_adj_return = returns_6m / volatility
```

- Measures return per unit of risk
- Higher values indicate better risk-adjusted performance
- Penalizes stocks with high volatility

#### Relative Strength
```
relative_strength = stock_return_6m / nifty_return_6m
```

- Compares stock performance to benchmark (Nifty 50)
- Values > 1.0 indicate outperformance
- Values < 1.0 indicate underperformance

### 2. Composite Score

```
composite_score = 0.40 × returns_6m + 
                  0.30 × vol_adj_return + 
                  0.30 × relative_strength × 100
```

**Weight Rationale:**
- **40% Returns**: Primary driver, rewards absolute performance
- **30% Vol-Adjusted**: Ensures we're not taking excessive risk
- **30% Relative Strength**: Ensures outperformance vs market

### 3. EMA-Based Entry Timing

#### 44-Day EMA Calculation
```
EMA[t] = (Price[t] × k) + (EMA[t-1] × (1 - k))
where k = 2 / (period + 1) = 2 / 45 ≈ 0.044
```

- Exponential Moving Average gives more weight to recent prices
- 44 days chosen to smooth out noise while remaining responsive
- Acts as dynamic support/resistance level

#### Rising EMA Trend
```
EMA is rising if: EMA[t-i] > EMA[t-i-1] for i = 1 to 5
```

- Confirms the uptrend is intact
- Reduces false signals during sideways or downtrending markets
- 5-day lookback ensures consistency

#### Price Near EMA
```
price_to_ema_pct = ((current_price - EMA) / EMA) × 100
price_near_ema = |price_to_ema_pct| ≤ 1.0
```

- Identifies pullback opportunities
- ±1% threshold allows for minor deviations
- Entry when strong stocks temporarily dip to support

### 4. Entry Signal
```
entry_signal = EMA_rising AND price_near_EMA
```

**Logic:**
1. Stock is in uptrend (rising EMA)
2. Price has pulled back to EMA (buying opportunity)
3. This combines momentum with mean reversion

### 5. Exit Rules

#### Exit Condition 1: Out of Top 20
- Stock no longer meets momentum criteria
- Drops out of top 20 during monthly rebalancing
- Action: Sell position immediately

#### Exit Condition 2: Price Below EMA
```
exit_signal = (current_price - EMA) / EMA × 100 < -2.0
```

- Price closes more than 2% below EMA
- Indicates potential trend reversal
- Action: Sell position to protect capital

### 6. Portfolio Management

#### Position Sizing
```
allocation_per_stock = available_cash / num_buy_signals
shares = allocation_per_stock / current_price
```

- Equal-weight allocation across all buy signals
- Automatic rebalancing on position changes
- No leverage (cash-only strategy)

#### Rebalancing Schedule
- **Monthly**: Full momentum recalculation
- **Daily**: EMA signal checks for new entries
- **Immediate**: Exit signals processed immediately

## Performance Metrics

### 1. CAGR (Compound Annual Growth Rate)
```
CAGR = ((final_value / initial_value)^(1/years) - 1) × 100
```

- Annualized return accounting for compounding
- Comparable across different time periods
- Industry standard for long-term performance

### 2. Sharpe Ratio
```
Sharpe = (avg_return / std_dev_return) × sqrt(12)
```

- Risk-adjusted return metric
- Assumes 0% risk-free rate (conservative)
- Annualized for year-over-year comparison
- **Interpretation:**
  - < 1.0: Poor risk-adjusted returns
  - 1.0-2.0: Good risk-adjusted returns
  - > 2.0: Excellent risk-adjusted returns

### 3. Maximum Drawdown
```
cummax = running_maximum(portfolio_value)
drawdown = (portfolio_value - cummax) / cummax × 100
max_drawdown = minimum(drawdown)
```

- Largest peak-to-trough decline
- Measures worst-case scenario
- Important for risk management
- Lower (less negative) is better

### 4. Win Rate
```
win_rate = (winning_trades / total_trades) × 100
```

- Percentage of profitable trades
- Simple but important metric
- > 50% indicates edge over random
- Combined with avg win/loss for complete picture

## Data Requirements

### Minimum Data Points

| Metric | Required Days | Reason |
|--------|---------------|--------|
| 52-week high | 252 | Full year of trading days |
| 6-month return | 126 | ~6 months of trading days |
| 3-month return | 63 | ~3 months of trading days |
| Volatility (60-day) | 60 | Rolling window |
| 44-day EMA | 44 | EMA calculation |
| **Total minimum** | **~300** | **~1.2 years with buffer** |

For backtesting: Minimum 5 years (1,260 trading days) recommended

### Data Quality Checks

The script includes built-in data validation:
1. **Completeness**: Skips stocks with insufficient data
2. **Validity**: Handles missing values and data gaps
3. **Recency**: Uses most recent available data
4. **Filtering**: Requires minimum 250 days for inclusion

## Algorithm Complexity

### Time Complexity

- **Data Fetching**: O(N) where N = number of stocks
- **Momentum Calculation**: O(N × M) where M = data points per stock
- **Sorting**: O(N log N) for ranking
- **Backtesting**: O(T × N) where T = rebalance periods
- **Overall**: O(N × M) dominated by data processing

### Space Complexity

- **Data Storage**: O(N × M) for all stock data
- **Results**: O(N) for metrics and rankings
- **Portfolio History**: O(T) for backtest results
- **Overall**: O(N × M) dominated by data storage

### Performance Optimization

1. **Vectorized Operations**: Uses pandas/numpy for speed
2. **Early Filtering**: Removes unsuitable stocks early
3. **Caching**: Could add data caching for repeated runs
4. **Parallel Processing**: Could parallelize data fetching

## Risk Considerations

### Strategy Risks

1. **Momentum Crashes**: Strategy vulnerable during market reversals
2. **Concentration**: Only 20 stocks may lack diversification
3. **Whipsaw**: EMA crossovers can produce false signals
4. **Data Quality**: Reliant on accurate historical data

### Mitigation Measures

1. **Retracement Filter**: Prevents chasing extended rallies
2. **Volatility Adjustment**: Penalizes high-risk stocks
3. **EMA Filter**: Confirms trend before entry
4. **Exit Rules**: Protects against major declines

## Assumptions

1. **Transaction Costs**: Not included in backtest (would reduce returns)
2. **Slippage**: Assumes fills at exact prices
3. **Liquidity**: Assumes sufficient liquidity for all trades
4. **Dividends**: Included via Yahoo Finance adjusted prices
5. **Tax**: Not considered in performance metrics
6. **Market Impact**: Assumes no price impact from trades

## Future Enhancements

### Potential Improvements

1. **Dynamic Position Sizing**
   - Risk parity allocation
   - Volatility-based sizing
   - Kelly criterion

2. **Additional Filters**
   - Fundamental screening (P/E, ROE, etc.)
   - Sector diversification
   - Liquidity requirements

3. **Advanced Entry/Exit**
   - Multi-timeframe analysis
   - Volume confirmation
   - Adaptive thresholds

4. **Risk Management**
   - Portfolio-level stop loss
   - Maximum position size
   - Correlation analysis

5. **Machine Learning**
   - Optimize weights using ML
   - Pattern recognition
   - Regime detection

## References

### Technical Indicators
- EMA: Exponential Moving Average (standard implementation)
- RSI: Relative Strength Index (could be added)
- Volume: Trading volume analysis (could be added)

### Academic Research
- Momentum Investing: Jegadeesh and Titman (1993)
- Volatility-Adjusted Returns: Sharpe (1966)
- Moving Average Strategies: Brock et al. (1992)

### Data Sources
- Yahoo Finance: Historical OHLCV data
- NSE India: Stock universe and corporate actions
- BSE India: Alternative data source

## Version History

- **v1.0** (2025-11-12): Initial implementation
  - Two-stage momentum + EMA strategy
  - 5-year backtesting
  - Performance metrics and visualizations
  - Demo mode for testing

## Contact & Support

For questions, suggestions, or bug reports:
- GitHub Issues: Use the repository's issue tracker
- Documentation: Refer to README.md and USAGE.md
- Code: Well-commented inline documentation

---

**Disclaimer**: This strategy is for educational purposes only. Past performance does not guarantee future results. Always do your own research and consult with a financial advisor before making investment decisions.
