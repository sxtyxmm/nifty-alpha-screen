# Example Output

This document shows example outputs from the Nifty Alpha Screen system.

## Console Output

### Top 20 Stocks Table

```
======================================================================
TOP 20 STOCKS
======================================================================
    Symbol  Current_Price  Retracement_52W  Return_6M  Vol_Adj_Return_6M  Relative_Strength_6M  Composite_Score
STOCK27.NS         147.61             1.75      43.48              1.413                 46.11            1.000
STOCK16.NS          93.02             2.59      42.73              1.308                 45.36            0.955
STOCK14.NS          91.76             2.15      35.85              1.243                 38.48            0.793
STOCK17.NS         140.35             3.62      32.93              1.150                 35.56            0.706
STOCK18.NS         214.99             4.91      25.40              0.808                 28.03            0.453
STOCK07.NS         202.99             7.67      24.06              0.879                 26.69            0.445
STOCK10.NS         132.99             8.32      24.44              0.666                 27.07            0.393
STOCK30.NS         176.32             6.20      20.39              0.587                 23.02            0.286
STOCK13.NS         118.17            12.34      17.21              0.554                 19.84            0.211
STOCK28.NS         110.25             5.37      16.89              0.536                 19.52            0.199
STOCK01.NS         138.57            10.62      16.50              0.505                 19.13            0.182
STOCK24.NS         147.07             2.31      14.98              0.544                 17.61            0.162
STOCK05.NS         107.81            15.40      13.38              0.463                 16.01            0.105
STOCK08.NS         117.62            12.35       9.83              0.351                 12.46            0.000
======================================================================
```

### Performance Summary

```
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

## Interpretation Guide

### Understanding the Metrics

#### Stock Metrics

1. **Current_Price**
   - Latest closing price of the stock
   - Used for reference

2. **Retracement_52W** (Lower is Better)
   - How far the stock has fallen from its 52-week high
   - Values shown: 1.75% to 15.40%
   - Interpretation:
     - < 5%: Very strong trend, near all-time high
     - 5-15%: Healthy trend, moderate pullback
     - 15-30%: Acceptable retracement (within filter)
     - > 30%: Filtered out (too weak)

3. **Return_6M** (Higher is Better)
   - Total return over last 6 months
   - Values shown: 9.83% to 43.48%
   - Interpretation:
     - > 30%: Excellent momentum
     - 15-30%: Good performance
     - 5-15%: Moderate performance
     - < 5%: Filtered out

4. **Vol_Adj_Return_6M** (Higher is Better)
   - Risk-adjusted return (like Sharpe ratio)
   - Values shown: 0.351 to 1.413
   - Interpretation:
     - > 1.0: Excellent risk-adjusted return
     - 0.5-1.0: Good risk-adjusted return
     - < 0.5: Lower quality (filtered out)

5. **Relative_Strength_6M** (Higher is Better)
   - Outperformance vs Nifty 50
   - Values shown: 12.46% to 46.11%
   - Interpretation:
     - > 20%: Strong outperformer
     - 10-20%: Good outperformer
     - 0-10%: Marginal outperformer
     - < 0%: Filtered out (underperformer)

6. **Composite_Score** (Higher is Better)
   - Overall ranking score (0-1 scale)
   - Top stock = 1.0, others normalized
   - Values shown: 0.000 to 1.000
   - Interpretation:
     - > 0.8: Top tier stocks
     - 0.5-0.8: Good candidates
     - 0.3-0.5: Moderate candidates
     - < 0.3: Lower tier (but passed filters)

#### Portfolio Performance Metrics

1. **CAGR (Compound Annual Growth Rate)**
   - Annualized return
   - Example: 18.50% (portfolio) vs 12.20% (index)
   - Interpretation:
     - Portfolio outperforms by 6.30% annually
     - On $100k investment, extra $6,300/year

2. **Max Drawdown**
   - Largest peak-to-trough decline
   - Example: -12.30% (portfolio) vs -15.40% (index)
   - Interpretation:
     - Portfolio has less downside risk
     - Better capital preservation
     - Lower is better (less negative)

3. **Sharpe Ratio**
   - Risk-adjusted return measure
   - Example: 1.45 (portfolio) vs 0.95 (index)
   - Interpretation:
     - > 1.5: Excellent
     - 1.0-1.5: Very good
     - 0.5-1.0: Good
     - < 0.5: Poor
     - Portfolio has superior risk-adjusted returns

4. **Win Rate**
   - % of profitable periods
   - Example: 65% (portfolio) vs 58.33% (index)
   - Interpretation:
     - Portfolio profitable in 65% of months
     - More consistent performance
     - Higher reliability

5. **Alpha**
   - Outperformance vs benchmark
   - Example: 6.30%
   - Interpretation:
     - Positive alpha = beating market
     - 6.30% = significant outperformance
     - Value added by strategy

## Example Insights

### From the Sample Data Above

**Best Stocks:**
- STOCK27.NS: Near 52-week high (1.75% retracement), strong returns (43.48%), excellent risk-adjusted performance (1.413)
- STOCK16.NS: Similar profile to STOCK27, second-best composite score
- STOCK14.NS: Good balance of momentum and risk management

**Portfolio Characteristics:**
- Strong momentum bias (all stocks positive returns)
- Good risk management (retracement filter)
- Outperformance focus (relative strength filter)
- Diversified risk-return profile

**Investment Implications:**
- Portfolio suitable for growth-oriented investors
- Moderate risk with 12.30% max drawdown
- Consistent performance (65% win rate)
- Significant alpha generation (6.30%)

## Visual Charts

The system generates two key charts:

### 1. Cumulative Returns Chart
Shows portfolio value growth vs Nifty 50 over time:
- X-axis: Time (dates)
- Y-axis: Cumulative return (base 100)
- Blue line: Portfolio performance
- Orange line: Nifty 50 benchmark
- Gap between lines = outperformance

### 2. Volatility & Drawdowns Chart
Two panels:

**Panel 1: Rolling Volatility**
- Shows risk changes over time
- Higher volatility = more risk
- Portfolio vs index comparison

**Panel 2: Drawdowns**
- Shows decline from peaks
- Shaded areas represent underwater periods
- Depth shows severity of drawdowns
- Duration shows recovery time

## How to Use This Information

### For Stock Selection:
1. Review top 20 list
2. Check individual metrics
3. Verify with fundamental analysis
4. Create watchlist for monitoring

### For Portfolio Construction:
1. Use equal weights (1/20 each)
2. Rebalance monthly
3. Replace stocks that drop out
4. Track performance metrics

### For Risk Management:
1. Monitor max drawdown
2. Watch volatility trends
3. Set stop-loss levels
4. Maintain diversification

### For Performance Evaluation:
1. Compare to benchmark (Nifty 50)
2. Track CAGR and alpha
3. Monitor Sharpe ratio
4. Review win rate consistency

## Disclaimer

These are example outputs for illustration purposes. Actual results will vary based on:
- Market conditions
- Time period analyzed
- Data quality
- Execution timing
- Transaction costs

Always conduct thorough research before making investment decisions.
