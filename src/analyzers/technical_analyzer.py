"""Technical Analyzer Module - EMA, trends, and technical indicators"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import logging

from ..utils.validators import validate_price

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Multi-timeframe technical analysis (Daily 1yr EMA + Weekly 5yr EMA)"""
    
    def __init__(
        self,
        daily_ema_period: int = 252,  # 1 year daily (252 trading days)
        weekly_ema_period: int = 260  # 5 years weekly (~260 weeks)
    ):
        """
        Initialize technical analyzer with multi-timeframe analysis
        
        Args:
            daily_ema_period: EMA period for daily chart (252 = 1 year)
            weekly_ema_period: EMA period for weekly chart (260 = 5 years)
        """
        self.daily_ema_period = daily_ema_period
        self.weekly_ema_period = weekly_ema_period
    
    def analyze(self, price_data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Multi-timeframe EMA analysis (Daily 1yr + Weekly 5yr)
        Identifies stocks in sustained uptrends with both timeframes aligned
        
        Args:
            price_data: DataFrame with price history (must have 'close' column)
        
        Returns:
            Dictionary with multi-timeframe analysis results or None if failed
        """
        if price_data is None or price_data.empty:
            logger.warning("Empty price data provided")
            return None
        
        try:
            current_price = price_data['close'].iloc[-1]
            
            # 1. Daily Chart - 1 Year EMA (252 trading days)
            daily_ema = self._calculate_ema_value(price_data, self.daily_ema_period)
            daily_above = current_price > daily_ema if daily_ema else False
            daily_diff_pct = ((current_price - daily_ema) / daily_ema * 100) if daily_ema else 0
            
            # 2. Weekly Chart - 5 Year EMA (convert daily to weekly)
            weekly_data = self._resample_to_weekly(price_data)
            weekly_ema = self._calculate_ema_value(weekly_data, self.weekly_ema_period)
            weekly_above = current_price > weekly_ema if weekly_ema else False
            weekly_diff_pct = ((current_price - weekly_ema) / weekly_ema * 100) if weekly_ema else 0
            
            # 3. Timeframe Alignment Score
            alignment_score = 0
            if daily_above:
                alignment_score += 1
            if weekly_above:
                alignment_score += 1
            
            # 4. Trend Strength
            if daily_above and weekly_above:
                if daily_diff_pct > 5 and weekly_diff_pct > 5:
                    trend_strength = 'VERY_STRONG'  # Both EMAs well above
                else:
                    trend_strength = 'STRONG'  # Both EMAs above
            elif daily_above or weekly_above:
                trend_strength = 'WEAK'  # Mixed signals
            else:
                trend_strength = 'DOWNTREND'  # Both EMAs below
            
            # 5. Calculate slopes for momentum
            daily_slope = self._calculate_ema_slope(price_data, self.daily_ema_period, days=20)
            weekly_slope = self._calculate_ema_slope(weekly_data, self.weekly_ema_period, weeks=4)
            
            # 6. Overall trend verdict
            if daily_above and weekly_above and daily_slope > 0 and weekly_slope > 0:
                overall_trend = 'STRONG_UPTREND'  # Perfect alignment
            elif daily_above and weekly_above:
                overall_trend = 'UPTREND'  # Good alignment
            elif daily_above:
                overall_trend = 'WEAK_UPTREND'  # Short-term only
            else:
                overall_trend = 'DOWNTREND'
            
            return {
                'current_price': round(current_price, 2),
                
                # Daily timeframe (1 year)
                'daily_ema_252': round(daily_ema, 2) if daily_ema else 0,
                'daily_vs_ema': 'ABOVE' if daily_above else 'BELOW',
                'daily_diff_pct': round(daily_diff_pct, 2),
                'daily_slope_pct': round(daily_slope, 2),
                
                # Weekly timeframe (5 years)
                'weekly_ema_260': round(weekly_ema, 2) if weekly_ema else 0,
                'weekly_vs_ema': 'ABOVE' if weekly_above else 'BELOW',
                'weekly_diff_pct': round(weekly_diff_pct, 2),
                'weekly_slope_pct': round(weekly_slope, 2),
                
                # Multi-timeframe verdict
                'timeframe_alignment': alignment_score,  # 0, 1, or 2
                'trend_strength': trend_strength,
                'overall_trend': overall_trend,
                
                # Legacy compatibility
                'ema': round(daily_ema, 2) if daily_ema else 0,
                'price_vs_ema': 'ABOVE' if daily_above else 'BELOW',
                'price_diff_pct': round(daily_diff_pct, 2),
                'slope_pct': round(daily_slope, 2),
                'slope_trend': 'RISING' if daily_slope > 2 else 'FALLING' if daily_slope < -2 else 'FLAT',
                
                'data_points': len(price_data),
                'multi_timeframe': True
            }
        
        except Exception as e:
            logger.error(f"Error in technical analysis: {str(e)}")
            return None
    
    def get_support_resistance(
        self, 
        price_data: pd.DataFrame,
        window: int = 20
    ) -> Dict[str, float]:
        """
        Calculate support and resistance levels
        
        Args:
            price_data: DataFrame with price history
            window: Window for calculating levels
        
        Returns:
            Dictionary with support and resistance levels
        """
        if price_data is None or len(price_data) < window:
            return {'support': 0, 'resistance': 0}
        
        try:
            recent = price_data.tail(window)
            
            return {
                'support': round(recent['low'].min(), 2),
                'resistance': round(recent['high'].max(), 2),
                'current': round(price_data['close'].iloc[-1], 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {str(e)}")
            return {'support': 0, 'resistance': 0}
    
    def _calculate_ema_value(self, data: pd.DataFrame, period: int) -> Optional[float]:
        """Calculate single EMA value for given period"""
        if data is None or len(data) < period:
            return None
        
        try:
            ema_series = data['close'].ewm(span=period, adjust=False).mean()
            return ema_series.iloc[-1]
        except Exception as e:
            logger.error(f"Error calculating EMA: {str(e)}")
            return None
    
    def _resample_to_weekly(self, daily_data: pd.DataFrame) -> pd.DataFrame:
        """Convert daily data to weekly for long-term analysis"""
        try:
            # Ensure index is datetime
            if 'date' in daily_data.columns:
                weekly = daily_data.set_index('date')
            else:
                weekly = daily_data.copy()
            
            if not isinstance(weekly.index, pd.DatetimeIndex):
                return daily_data  # Can't resample, return original
            
            # Resample to weekly (use last close of week)
            weekly_resampled = pd.DataFrame({
                'close': weekly['close'].resample('W').last()
            }).dropna()
            
            return weekly_resampled
        except Exception as e:
            logger.debug(f"Could not resample to weekly: {str(e)}")
            return daily_data
    
    def _calculate_ema_slope(self, data: pd.DataFrame, ema_period: int, days: int = None, weeks: int = None) -> float:
        """Calculate EMA slope over specified period"""
        try:
            ema_series = data['close'].ewm(span=ema_period, adjust=False).mean()
            
            if len(ema_series) < 2:
                return 0.0
            
            # Use specified lookback period
            lookback = weeks if weeks else days if days else 5
            if len(ema_series) < lookback:
                lookback = len(ema_series)
            
            ema_start = ema_series.iloc[-lookback]
            ema_end = ema_series.iloc[-1]
            
            slope_pct = ((ema_end - ema_start) / ema_start * 100) if ema_start > 0 else 0
            return slope_pct
        except Exception as e:
            logger.error(f"Error calculating EMA slope: {str(e)}")
            return 0.0

