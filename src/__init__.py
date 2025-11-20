"""NSE Stock Analysis System - Main Package"""

__version__ = "3.0.0"
__author__ = "sxtyxmm"
__description__ = "EMA Retracement + Smart Money Screener for Indian Markets"

from .data_fetchers import NSEDataFetcher, DeliveryDataFetcher
from .analyzers import TechnicalAnalyzer, FundamentalAnalyzer
from .scorers import StockScorer
from .async_pipeline import AsyncStockDataPipeline

__all__ = [
    'NSEDataFetcher',
    'DeliveryDataFetcher',
    'TechnicalAnalyzer',
    'FundamentalAnalyzer',
    'StockScorer',
    'AsyncStockDataPipeline'
]
