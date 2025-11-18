"""
Configuration file for Stock Analysis System
Adjust these settings based on your requirements
"""

# Data Fetching Settings
MAX_WORKERS = 10  # Number of parallel threads for fetching data
CACHE_TTL = 3600  # Cache duration in seconds (1 hour)
DEFAULT_PERIOD = '1y'  # Historical price data period

# Scoring Thresholds
SCORE_BUY_THRESHOLD = 3.0
SCORE_HOLD_MIN = 1.0
SCORE_AVOID_MAX = 0.0

# EMA Settings
EMA_PERIOD = 44  # Exponential Moving Average period
EMA_SLOPE_DAYS = 5  # Days to calculate slope

# Fundamental Thresholds
PE_LOW_THRESHOLD = 20  # Good P/E ratio
PE_HIGH_THRESHOLD = 40  # High P/E ratio
ROE_GOOD_THRESHOLD = 0.15  # 15% ROE
DEBT_LOW_THRESHOLD = 0.5  # Low debt to equity
DEBT_HIGH_THRESHOLD = 2.0  # High debt to equity

# Delivery Data Thresholds
DELIVERY_HIGH_THRESHOLD = 50  # High delivery %
DELIVERY_GOOD_THRESHOLD = 35  # Good delivery %
DELIVERY_TREND_THRESHOLD = 0.05  # 5% change for trend

# Dashboard Settings
DEFAULT_STOCKS_LIMIT = 100  # Default number of stocks to analyze
CHART_HEIGHT = 500  # Chart height in pixels

# Export Settings
EXPORT_DATE_FORMAT = '%Y%m%d_%H%M%S'

# Network Settings
REQUEST_TIMEOUT = 15  # Timeout for HTTP requests in seconds
MAX_RETRIES = 3  # Maximum retries for failed requests

# NSE Settings
NSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# Fallback Symbols (used when NSE API is unavailable)
FALLBACK_SYMBOLS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
    'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
    # Add more as needed...
]
