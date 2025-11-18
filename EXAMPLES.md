# Example Usage Scenarios

This document provides real-world usage examples for the NSE Stock Analysis System.

## Scenario 1: Daily Morning Routine

### Objective
Get top 20 BUY opportunities before market opens

### Commands
```bash
# Quick scan (no delivery data for speed)
python cli.py --scan --top 20 --no-delivery

# OR use dashboard for interactive exploration
streamlit run dashboard.py
```

### Expected Time
- CLI: 2-3 minutes
- Dashboard: 5 minutes initial load, then instant filtering

### What to Look For
- Score ≥ 4: Strong conviction plays
- Price >5% above EMA-44: Strong momentum
- Multiple BUY signals in same sector: Sector rotation

## Scenario 2: Deep Dive on Watchlist

### Objective
Analyze your existing watchlist in detail

### Code (Python API)
```python
from data_pipeline import StockDataPipeline

# Your watchlist
watchlist = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
             'HDFC', 'ITC', 'KOTAKBANK', 'LT', 'AXISBANK']

# Analyze with delivery data
pipeline = StockDataPipeline(symbols=watchlist, max_workers=5)
df = pipeline.fetch_all_data(use_delivery=True)

# Filter for BUY signals only
buys = df[df['signal'] == 'BUY'].sort_values('score', ascending=False)

# Print results
print(buys[['symbol', 'current_price', 'score', 'delivery_pct']])

# Export for detailed review
pipeline.export_to_excel('my_watchlist_analysis.xlsx')
```

### Output
Excel file with:
- All stocks analyzed
- Separate sheets for BUY/HOLD/AVOID
- Full metrics for each stock

## Scenario 3: Sector Analysis

### Objective
Find best stocks in Banking sector

### Using Dashboard
1. Run `streamlit run dashboard.py`
2. Go to "Rankings" tab
3. Use "Sector" filter → Select "Financial Services"
4. Sort by "Score" (Descending)
5. Export top results to CSV

### Using Python
```python
from data_pipeline import StockDataPipeline

# Analyze all stocks
pipeline = StockDataPipeline(max_workers=10)
df = pipeline.fetch_all_data(use_delivery=True)

# Filter for banking/financial stocks
banking = df[df['sector'].str.contains('Financial|Banking', case=False, na=False)]

# Get top 10 BUY signals in banking
top_banking = banking[banking['signal'] == 'BUY'].head(10)

print(top_banking[['symbol', 'company_name', 'score', 'signal']])
```

## Scenario 4: Risk Assessment

### Objective
Identify AVOID signals to stay away from

### Commands
```bash
# Scan for weak stocks
python cli.py --scan --top 100
```

### In Python
```python
from data_pipeline import StockDataPipeline

pipeline = StockDataPipeline(max_workers=10)
df = pipeline.fetch_all_data(use_delivery=True)

# Find worst performers
avoid = df[df['signal'] == 'AVOID'].sort_values('score')

# Check why they're weak
for idx, stock in avoid.head(10).iterrows():
    print(f"\n{stock['symbol']}:")
    print(f"  Price vs EMA: {stock['price_vs_ema']}")
    print(f"  EMA Slope: {stock['ema_slope']:.2f}%")
    print(f"  Score: {stock['score']:.1f}")
```

## Scenario 5: Portfolio Rebalancing

### Objective
Check existing holdings and decide on actions

### Code
```python
from data_pipeline import StockDataPipeline
import pandas as pd

# Your current holdings
portfolio = {
    'RELIANCE': 50,   # 50 shares
    'TCS': 30,
    'INFY': 100,
    'HDFCBANK': 75,
}

# Analyze all holdings
pipeline = StockDataPipeline(symbols=list(portfolio.keys()), max_workers=4)
df = pipeline.fetch_all_data(use_delivery=True)

# Add position size
df['shares'] = df['symbol'].map(portfolio)
df['position_value'] = df['current_price'] * df['shares']

# Recommendations
for idx, stock in df.iterrows():
    symbol = stock['symbol']
    signal = stock['signal']
    score = stock['score']
    value = stock['position_value']
    
    print(f"\n{symbol} ({signal}, Score: {score:.1f})")
    print(f"  Position: {portfolio[symbol]} shares = ₹{value:,.0f}")
    
    if signal == 'AVOID' and score < -1:
        print(f"  → Consider SELLING")
    elif signal == 'BUY' and score >= 4:
        print(f"  → Consider ADDING")
    else:
        print(f"  → HOLD current position")
```

## Scenario 6: Weekly Review

### Objective
Weekly comprehensive market analysis

### Process
1. **Monday Morning**: Scan all stocks
   ```bash
   streamlit run dashboard.py
   # In sidebar: Set "Number of Stocks" to 200
   # Include delivery data
   ```

2. **Review Top BUY Signals**
   - Check fundamentals (P/E, ROE)
   - Verify delivery % trend
   - Look at price charts

3. **Export for Record**
   - Download CSV with timestamp
   - Track top signals week over week

4. **Compare with Previous Week**
   ```python
   import pandas as pd
   
   # Load this week and last week
   this_week = pd.read_csv('stock_analysis_20231120.csv')
   last_week = pd.read_csv('stock_analysis_20231113.csv')
   
   # Find new BUY signals
   this_buys = set(this_week[this_week['signal'] == 'BUY']['symbol'])
   last_buys = set(last_week[last_week['signal'] == 'BUY']['symbol'])
   
   new_buys = this_buys - last_buys
   print(f"New BUY signals this week: {new_buys}")
   ```

## Scenario 7: Automated Daily Report

### Objective
Email yourself top opportunities every day

### Code (save as `daily_report.py`)
```python
from data_pipeline import StockDataPipeline
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_daily_report():
    # Analyze top 100 stocks
    pipeline = StockDataPipeline(max_workers=10)
    df = pipeline.fetch_all_data(use_delivery=True)
    
    # Get top 10 BUY signals
    top_buys = df[df['signal'] == 'BUY'].head(10)
    
    # Create HTML report
    html = f"""
    <h2>Daily Stock Report - {datetime.now().strftime('%Y-%m-%d')}</h2>
    <h3>Top 10 BUY Opportunities</h3>
    {top_buys[['symbol', 'current_price', 'score', 'delivery_pct']].to_html()}
    
    <h3>Market Summary</h3>
    <ul>
        <li>Total BUY signals: {len(df[df['signal'] == 'BUY'])}</li>
        <li>Total HOLD signals: {len(df[df['signal'] == 'HOLD'])}</li>
        <li>Total AVOID signals: {len(df[df['signal'] == 'AVOID'])}</li>
    </ul>
    """
    
    # Send email (configure your SMTP settings)
    # msg = MIMEMultipart()
    # msg['Subject'] = f"Daily Stock Report - {datetime.now().strftime('%Y-%m-%d')}"
    # msg.attach(MIMEText(html, 'html'))
    # ... email sending code ...
    
    # OR just save to file
    with open(f"daily_report_{datetime.now().strftime('%Y%m%d')}.html", 'w') as f:
        f.write(html)
    
    print("Report generated successfully!")

if __name__ == "__main__":
    generate_daily_report()
```

### Run with Cron
```bash
# Add to crontab (runs every day at 8 AM)
0 8 * * * cd /path/to/nifty-alpha-screen && python daily_report.py
```

## Scenario 8: Backtesting (Manual)

### Objective
Check how past signals performed

### Process
1. Save weekly reports with timestamps
2. After 1-2 weeks, check performance
3. Compare actual price movement vs prediction

### Code
```python
import pandas as pd
import yfinance as yf

# Load old report
old_report = pd.read_csv('stock_analysis_20231106.csv')
old_buys = old_report[old_report['signal'] == 'BUY']['symbol'].tolist()

# Check performance after 2 weeks
for symbol in old_buys[:10]:
    ticker = yf.Ticker(f"{symbol}.NS")
    hist = ticker.history(period='1mo')
    
    # Price 2 weeks ago vs today
    old_price = hist['Close'].iloc[0]
    new_price = hist['Close'].iloc[-1]
    change = ((new_price - old_price) / old_price) * 100
    
    print(f"{symbol}: {change:+.2f}%")
```

## Tips for Success

1. **Consistency**: Run analysis daily or weekly
2. **Record Keeping**: Export and save results
3. **Patience**: Don't act on every signal
4. **Diversification**: Don't put all in top scorer
5. **Risk Management**: Always use stop losses
6. **Due Diligence**: Verify with fundamental analysis
7. **Market Context**: Consider overall market sentiment

## Performance Optimization

For faster analysis:

```python
# Use fewer stocks
pipeline = StockDataPipeline(max_workers=10)
symbols = fetcher.fetch_all_nse_symbols()[:50]  # Top 50 only
pipeline.symbols = symbols

# Skip delivery data
df = pipeline.fetch_all_data(use_delivery=False)

# Increase workers (if you have good internet)
pipeline = StockDataPipeline(max_workers=20)
```

---

**Remember**: This is a tool to assist your research, not a guarantee of profits. Always:
- Do your own analysis
- Check company news
- Understand the business
- Manage risk appropriately
- Consult a financial advisor
