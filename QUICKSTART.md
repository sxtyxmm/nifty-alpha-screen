# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Installation

```bash
# Clone and setup
git clone https://github.com/sxtyxmm/nifty-alpha-screen.git
cd nifty-alpha-screen
pip install -r requirements.txt
```

### Step 2: Choose Your Interface

#### Option A: Streamlit Dashboard (Recommended)

```bash
streamlit run dashboard.py
```

**What you'll see:**
- Beautiful web interface at `http://localhost:8501`
- Interactive charts and tables
- Real-time filtering and sorting
- Export to CSV/Excel

#### Option B: Command Line

```bash
# Analyze one stock
python cli.py --symbol RELIANCE

# Get top 20 BUY signals
python cli.py --scan --top 20

# Quick mode (skip delivery data)
python cli.py --symbol TCS --no-delivery
```

### Step 3: Understand the Output

#### Score Breakdown (-5 to +5)

```
Components:
✓ EMA Position: Price > EMA-44 (+1 to +2)
✓ EMA Slope: Rising trend (+1)
✓ Fundamentals: PE, ROE, Debt (-2 to +2)
✓ Delivery %: High accumulation (+1 to +2)
✓ Delivery Trend: Rising (+1)
```

#### Signals

- **BUY** (Score ≥ 3): Strong buy opportunity
- **HOLD** (Score 1-2): Monitor closely
- **AVOID** (Score ≤ 0): Stay away

### Step 4: Customize

Edit settings in the Streamlit sidebar:
- Number of stocks (10-500)
- Include/exclude delivery data
- Filter by sector, signal, score
- Sort by any metric

### Step 5: Export and Use

Download your analysis:
- 📥 CSV for spreadsheets
- 📊 Excel for detailed analysis
- Share insights with your team

## 📊 Example: Analyzing RELIANCE

### Input
```bash
python cli.py --symbol RELIANCE
```

### Output
```
📊 FUNDAMENTALS
+------------------+------------+
| Metric           | Value      |
+==================+============+
| Current Price    | ₹2,461.00  |
| Market Cap       | ₹16.65 Cr  |
| P/E (Trailing)   | 23.45      |
| ROE              | 9.87%      |
| Debt to Equity   | 0.45       |
+------------------+------------+

📈 TECHNICAL ANALYSIS
+------------+--------+
| Metric     | Value  |
+============+========+
| EMA-44     | 2,389  |
| Position   | ABOVE  |
| Deviation  | +3.02% |
| EMA Slope  | +2.15% |
+------------+--------+

📦 DELIVERY DATA
+--------------+--------+
| Metric       | Value  |
+==============+========+
| Delivery %   | 42.0%  |
| Trend        | rising |
+--------------+--------+

🎯 FINAL VERDICT
🚀 Signal: BUY
Score: 4.5 / 5.0
```

## 🎓 Understanding the Analysis

### What Makes a BUY Signal?

1. **Price Above EMA-44**: Shows bullish momentum
2. **Rising EMA**: Confirms uptrend
3. **High Delivery %**: Institutional accumulation
4. **Good Fundamentals**: Sustainable business

### What to Watch For

⚠️ **Avoid if:**
- Price well below EMA-44
- Falling EMA slope
- High P/E (>40) with low ROE
- Low delivery % (<20%)

✅ **Strong BUY if:**
- Score ≥ 4
- Price >5% above EMA-44
- Delivery % >50%
- ROE >15%, PE <20

## 🔧 Common Tasks

### Scan All NSE Stocks
```bash
python cli.py --scan
```

### Find Top 50 Opportunities
```bash
python cli.py --scan --top 50
```

### Analyze Your Watchlist
```bash
python cli.py --symbols RELIANCE TCS INFY HDFCBANK ICICIBANK
```

### Fast Analysis (No Delivery)
```bash
python cli.py --symbol SBIN --no-delivery
```

## 📱 Dashboard Features

### Sidebar Controls
- **Stock Selection**: Dropdown with search
- **Filters**: Signal type, sector, score range
- **Options**: Charts, fundamentals display
- **Export**: CSV and Excel downloads

### Main Tabs

1. **Overview**: Market summary and top BUY signals
2. **Stock Details**: Deep dive into specific stocks
3. **Rankings**: Sortable table of all stocks

### Interactive Charts
- Price vs EMA-44 with crossover markers
- Delivery % trend with threshold lines
- Color-coded signals (Green/Yellow/Red)

## 🎯 Pro Tips

1. **Start Small**: Test with 50 stocks first
2. **Use Caching**: Data refreshes every hour
3. **Watch Crossovers**: EMA crossovers signal trend changes
4. **Combine Signals**: Don't rely on score alone
5. **Monitor Regularly**: Markets change daily

## ⚠️ Important Notes

- **Not Financial Advice**: Do your own research
- **Data Freshness**: Yahoo Finance provides real-time data
- **NSE Delivery**: May not be available for all dates
- **Fallback Mode**: Uses 100 popular stocks if NSE fails

## 🆘 Troubleshooting

### "No data available"
- Check internet connection
- Try `--no-delivery` flag
- Reduce number of stocks

### Slow Performance
- Limit to 50-100 stocks
- Disable delivery data
- Use CLI instead of dashboard

### Missing Delivery Data
- Normal for some dates/stocks
- Analysis works without it (reduced score)

## 📚 Next Steps

1. ✅ Run the quick start commands above
2. 📊 Explore the dashboard features
3. 📈 Build your watchlist
4. 🔄 Set up daily analysis routine
5. 📱 Deploy to cloud for 24/7 access

## 🌟 Advanced Usage

See [README.md](README.md) for:
- Python API usage
- Cloud deployment options
- Custom scoring logic
- Backtesting strategies

---

**Ready to start? Run:** `streamlit run dashboard.py` 🚀
