# 📈 NSE Stock Analysis System

**Complete Automated Stock Analysis System for Indian Markets**

A comprehensive, production-ready platform that automatically analyzes ALL NSE stocks using fundamentals, technical indicators (EMA-44), and delivery data to provide actionable BUY/HOLD/AVOID signals.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

## 🚀 Features

### Automated Data Pipeline
- **Auto-fetch ALL NSE stocks** from official sources
- **Parallel processing** for fast data retrieval
- **Comprehensive fundamentals**: Market Cap, P/E, ROE, D/E, Beta, and more
- **Technical analysis**: EMA-44, slope calculation, trend detection
- **NSE delivery data**: Auto-download daily bhavcopy with 3-day trend analysis

### Advanced Scoring System
Score range: **-5 to +5** based on:
- ✅ EMA trend and position (0 to +2)
- ✅ EMA slope momentum (-1 to +1)
- ✅ Fundamental strength (-2 to +2)
- ✅ Delivery percentage (0 to +2)
- ✅ Delivery trend (0 or +1)

### Decision Signals
- **BUY**: Score ≥ 3 (High conviction opportunities)
- **HOLD**: Score 1-2 (Monitor positions)
- **AVOID**: Score ≤ 0 (Stay away)

### Interactive Streamlit Dashboard
- 📊 **Real-time stock rankings** with sortable tables
- 📈 **Interactive charts** (Price vs EMA-44, Delivery trends)
- 🔍 **Stock search** and filtering
- 📥 **Export to CSV/Excel**
- ⚙️ **Customizable filters** (sector, signal type, score range)
- 🎨 **Professional UI** with color-coded signals

### Command Line Interface
- Fast single-stock analysis
- Batch analysis of multiple stocks
- Full NSE scan with top opportunities
- Export capabilities

## 📦 Installation

### Quick Start

```bash
# Clone repository
git clone https://github.com/sxtyxmm/nifty-alpha-screen.git
cd nifty-alpha-screen

# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.10+
- Internet connection (for data fetching)
- 2GB+ RAM recommended

## 🎯 Usage

### Streamlit Dashboard (Recommended)

```bash
streamlit run dashboard.py
```

Then open your browser to `http://localhost:8501`

**Dashboard Features:**
- View all stocks with comprehensive rankings
- Filter by signal type (BUY/HOLD/AVOID)
- Analyze individual stocks in detail
- Interactive charts and visualizations
- Export results to CSV/Excel
- Real-time data refresh

### Command Line Interface

#### Analyze Single Stock
```bash
python cli.py --symbol RELIANCE
```

#### Scan All NSE Stocks
```bash
python cli.py --scan --top 30
```

#### Analyze Multiple Stocks
```bash
python cli.py --symbols RELIANCE TCS INFY HDFCBANK
```

#### Fast Mode (Skip Delivery Data)
```bash
python cli.py --symbol RELIANCE --no-delivery
```

### Python API

```python
from data_pipeline import StockDataPipeline

# Create pipeline
pipeline = StockDataPipeline()

# Fetch all data
df = pipeline.fetch_all_data(use_delivery=True)

# Get top BUY signals
top_buys = pipeline.get_top_buys(n=20)

# Export results
pipeline.export_to_excel('analysis.xlsx')
```

## 📊 Data Sources

### Stock Symbols
- NSE official API
- NSE equity list
- Fallback to curated Nifty 50 + popular stocks

### Fundamentals
- **Source**: Yahoo Finance (`yfinance`)
- **Metrics**: Market Cap, P/E, P/B, ROE, D/E, Beta
- **Frequency**: Real-time

### Price Data
- **Source**: Yahoo Finance
- **Period**: Last 1 year
- **Indicators**: EMA-44, slope analysis

### Delivery Data
- **Source**: NSE Bhavcopy (archives.nseindia.com)
- **Format**: Daily CSV files
- **Metrics**: Delivery quantity, percentage, trends

## 🎓 Scoring Methodology

### Component Breakdown

1. **EMA Trend (0 to +2)**
   - Price >5% above EMA-44: +2
   - Price above EMA-44: +1
   - Price below EMA-44: 0

2. **EMA Slope (-1 to +1)**
   - Rising >2% (5-day): +1
   - Flat: 0
   - Falling <-2%: -1

3. **Fundamentals (-2 to +2)**
   - P/E: <20 (+1), >40 (-1)
   - ROE: >15% (+1), <0% (-1)
   - Debt: <0.5 (+0.5), >2 (-0.5)

4. **Delivery % (0 to +2)**
   - >50%: +2
   - >35%: +1
   - Otherwise: 0

5. **Delivery Trend (0 or +1)**
   - Rising 3-day trend: +1
   - Otherwise: 0

### Example Score Calculation

**RELIANCE**:
- Price 3% above EMA-44: +1
- EMA slope +3% (rising): +1
- P/E 18 (good): +1, ROE 12% (ok): 0, D/E 0.3 (low): +0.5
- Delivery 42%: +1
- Delivery rising: +1
- **Total: 5.5 → Capped at 5.0 → BUY**

## 📁 Project Structure

```
nifty-alpha-screen/
├── dashboard.py              # Streamlit dashboard
├── cli.py                    # Command-line interface
├── data_pipeline.py          # Main data processing pipeline
├── nse_data_fetcher.py       # NSE data fetching utilities
├── stock_analyzer.py         # Original single-stock analyzer
├── requirements.txt          # Python dependencies
├── sample_bhavcopy.csv       # Sample delivery data
├── README.md                 # This file
├── DEPLOYMENT.md             # Deployment guide
└── .gitignore               # Git ignore rules
```

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:

- **Streamlit Cloud** (Free, recommended)
- **Railway.app** ($5/month free credit)
- **Render.com** (Free tier with limitations)
- **Docker** (Self-hosted)
- **Heroku** ($7/month minimum)

### Quick Deploy to Streamlit Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy with main file: `dashboard.py`
4. Done! ✅

## ⚙️ Configuration

### Performance Tuning

Edit `data_pipeline.py` to adjust:

```python
# Number of parallel workers
max_workers = 10  # Reduce for slower connections

# Cache duration (seconds)
CACHE_TTL = 3600  # 1 hour
```

### Data Limits

In the dashboard, use sidebar controls to:
- Limit number of stocks analyzed (10-500)
- Enable/disable delivery data fetching
- Adjust cache settings

## 🔧 Advanced Features

### Caching
- All data fetching is cached for 1 hour
- Reduces API calls and improves performance
- Configurable cache TTL

### Error Handling
- Graceful fallback if NSE APIs fail
- Continues processing even if individual stocks fail
- Comprehensive logging

### Export Capabilities
- CSV export with all metrics
- Excel export with multiple sheets
- Timestamped filenames

## 📈 Example Output

### Dashboard View
```
Symbol  | Company         | Price  | EMA     | Slope  | Deliv% | Score | Signal
--------|-----------------|--------|---------|--------|--------|-------|-------
RELIANCE| Reliance Ind.   | 2461.0 | ABOVE   | +2.3%  | 42.0%  | 5.0   | BUY
TCS     | TCS Ltd         | 3510.5 | ABOVE   | +1.8%  | 42.5%  | 4.5   | BUY
INFY    | Infosys Ltd     | 1460.0 | ABOVE   | +0.9%  | 40.0%  | 3.0   | BUY
```

### CLI Output
```
🎯 FINAL VERDICT
================================================================================
🚀 Signal: BUY
Score: 5.0 / 5.0
================================================================================
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⚠️ Disclaimer

**This tool is for educational and informational purposes only.**

- NOT financial advice
- Do your own research (DYOR)
- Consult a qualified financial advisor
- Past performance doesn't guarantee future results
- Markets are inherently risky

## 📄 License

MIT License - Free to use, modify, and distribute.

## 🔗 Links

- **Repository**: [github.com/sxtyxmm/nifty-alpha-screen](https://github.com/sxtyxmm/nifty-alpha-screen)
- **Issues**: [Report bugs or request features](https://github.com/sxtyxmm/nifty-alpha-screen/issues)
- **Discussions**: [Ask questions](https://github.com/sxtyxmm/nifty-alpha-screen/discussions)

## 🙏 Acknowledgments

- **Yahoo Finance** for fundamental and price data
- **NSE India** for delivery data
- **Streamlit** for the amazing dashboard framework
- **yfinance** library maintainers

## 📞 Support

Having issues? Try:

1. Check the [Deployment Guide](DEPLOYMENT.md)
2. Review [GitHub Issues](https://github.com/sxtyxmm/nifty-alpha-screen/issues)
3. Run with `--no-delivery` flag for faster/simpler analysis
4. Reduce number of stocks analyzed

## 🎉 Features Coming Soon

- [ ] Real-time alerts for BUY signals
- [ ] Backtesting capabilities
- [ ] Portfolio tracking
- [ ] WhatsApp/Telegram notifications
- [ ] Mobile app
- [ ] Options data integration
- [ ] Sector rotation analysis

---

**Made with ❤️ for the Indian trading community**

**Star ⭐ this repo if you find it useful!**
