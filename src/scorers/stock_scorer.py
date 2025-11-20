"""Stock Scorer Module - Calculate final scores and signals"""

from typing import Dict, Any, Optional
import logging

from ..utils.validators import validate_score

logger = logging.getLogger(__name__)


class StockScorer:
    """Calculate stock scores and generate BUY/HOLD/AVOID signals"""
    
    def __init__(
        self,
        buy_threshold: float = 3.0,
        hold_min: float = 1.0,
        hold_max: float = 2.9,
        min_score: float = -5.0,
        max_score: float = 5.0
    ):
        """
        Initialize stock scorer
        
        Args:
            buy_threshold: Minimum score for BUY signal
            hold_min: Minimum score for HOLD signal
            hold_max: Maximum score for HOLD signal
            min_score: Minimum possible score
            max_score: Maximum possible score
        """
        self.buy_threshold = buy_threshold
        self.hold_min = hold_min
        self.hold_max = hold_max
        self.min_score = min_score
        self.max_score = max_score
    
    def calculate_score(
        self,
        technical_analysis: Optional[Dict[str, Any]] = None,
        fundamental_analysis: Optional[Dict[str, Any]] = None,
        delivery_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall stock score based on all analyses
        
        Args:
            technical_analysis: Technical analysis results
            fundamental_analysis: Fundamental analysis results
            delivery_data: Delivery data analysis results
        
        Returns:
            Dictionary with score breakdown and signal
        """
        try:
            # Calculate component scores
            technical_score = self._calculate_technical_score(technical_analysis)
            fundamental_score = self._calculate_fundamental_score(fundamental_analysis)
            delivery_score = self._calculate_delivery_score(delivery_data)
            
            # Total score (capped at min/max)
            total_score = technical_score + fundamental_score + delivery_score
            total_score = max(self.min_score, min(total_score, self.max_score))
            
            # Generate signal
            signal = self._generate_signal(total_score)
            
            # Create score breakdown
            return {
                'total_score': round(total_score, 2),
                'signal': signal,
                'breakdown': {
                    'technical': round(technical_score, 2),
                    'fundamental': round(fundamental_score, 2),
                    'delivery': round(delivery_score, 2)
                },
                'components': {
                    'daily_ema': technical_analysis.get('daily_vs_ema', 'N/A') if technical_analysis else 'N/A',
                    'weekly_ema': technical_analysis.get('weekly_vs_ema', 'N/A') if technical_analysis else 'N/A',
                    'timeframe_alignment': technical_analysis.get('timeframe_alignment', 0) if technical_analysis else 0,
                    'fundamentals': fundamental_score,
                    'delivery_qty_spike': delivery_data.get('has_qty_spike', False) if delivery_data else False,
                    'delivery_qty_ratio': delivery_data.get('qty_spike_ratio', 0) if delivery_data else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating score: {str(e)}")
            return {
                'total_score': 0.0,
                'signal': 'AVOID',
                'breakdown': {'technical': 0, 'fundamental': 0, 'delivery': 0},
                'error': str(e)
            }
    
    def _calculate_technical_score(self, analysis: Optional[Dict[str, Any]]) -> float:
        """
        Calculate technical score for EMA RETRACEMENT strategy (buy-the-dip)
        
        Score range: 0 to +4
        
        Strategy: Look for stocks that pulled back to TOUCH the EMA in an uptrend
        This is the entry point, not stocks far above the EMA
        
        Components:
        - Daily EMA touchpoint (0-5% above): 0 to +2 (perfect entry)
        - Weekly EMA touchpoint (0-5% above): 0 to +2 (long-term support)
        - Far above EMA (>10%): LOWER score (already ran, missed entry)
        
        Args:
            analysis: Technical analysis results with multi-timeframe data
        
        Returns:
            Technical score (0 to 4)
        """
        if not analysis:
            return 0.0
        
        score = 0.0
        
        # Daily timeframe - RETRACEMENT scoring (near EMA = best)
        daily_above = analysis.get('daily_vs_ema') == 'ABOVE'
        daily_diff = analysis.get('daily_diff_pct', 0)
        
        if daily_above:
            if 0 <= daily_diff <= 3:  # PERFECT touchpoint (0-3% above)
                score += 2.0
            elif 3 < daily_diff <= 5:  # Good touchpoint (3-5% above)
                score += 1.5
            elif 5 < daily_diff <= 8:  # Slightly extended
                score += 1.0
            elif 8 < daily_diff <= 15:  # Extended (not ideal entry)
                score += 0.5
            else:  # Far above (missed the entry)
                score += 0.25
        # Below EMA = downtrend, score 0
        
        # Weekly timeframe - RETRACEMENT scoring (long-term support)
        weekly_above = analysis.get('weekly_vs_ema') == 'ABOVE'
        weekly_diff = analysis.get('weekly_diff_pct', 0)
        
        if weekly_above:
            if 0 <= weekly_diff <= 5:  # PERFECT long-term touchpoint
                score += 2.0
            elif 5 < weekly_diff <= 10:  # Good position
                score += 1.5
            elif 10 < weekly_diff <= 20:  # Slightly extended
                score += 1.0
            elif 20 < weekly_diff <= 30:  # Extended
                score += 0.5
            else:  # Very far (overbought)
                score += 0.25
        
        return score
    
    def _calculate_fundamental_score(self, analysis: Optional[Dict[str, Any]]) -> float:
        """
        Calculate fundamental analysis score (-2 to +2)
        
        Based on quality score from fundamental analysis
        """
        if not analysis:
            return 0.0
        
        quality_score = analysis.get('quality_score', 0)
        
        # Scale quality score (-1 to +1) to (-2 to +2)
        return quality_score * 2
    
    def _calculate_delivery_score(self, data: Optional[Dict[str, Any]]) -> float:
        """
        Calculate delivery score based on QUANTITY spike (smart money detection)
        
        Score range: 0 to +3
        
        Components:
        - Delivery quantity spike: 0 to +2 (unusual accumulation)
        - High delivery percentage: 0 to +1 (confirmation)
        
        Args:
            data: Delivery data with quantity metrics
        
        Returns:
            Delivery score (0 to 3)
        """
        if not data:
            return 0.0
        
        score = 0.0
        
        # QUANTITY SPIKE (This is the smart money indicator)
        has_spike = data.get('has_qty_spike', False)
        spike_ratio = data.get('qty_spike_ratio', 1.0)
        
        if has_spike:
            if spike_ratio >= 3.0:  # 3x normal quantity = STRONG accumulation
                score += 2.0
            elif spike_ratio >= 2.0:  # 2x normal quantity = accumulation
                score += 1.5
            else:
                score += 1.0
        
        # PERCENTAGE confirmation (high delivery % = real accumulation, not just trading)
        delivery_pct = data.get('latest_delivery_pct', 0)
        
        if delivery_pct > 50:  # Very high delivery
            score += 1.0
        elif delivery_pct > 35:  # Moderate delivery
            score += 0.5
        
        return score
    
    def _generate_signal(self, score: float) -> str:
        """
        Generate BUY/HOLD/AVOID signal based on score
        
        Args:
            score: Total score
        
        Returns:
            Signal string (BUY/HOLD/AVOID)
        """
        if score >= self.buy_threshold:
            return 'BUY'
        elif score >= self.hold_min:
            return 'HOLD'
        else:
            return 'AVOID'
    
    def get_signal_emoji(self, signal: str) -> str:
        """Get emoji for signal"""
        emoji_map = {
            'BUY': '🚀',
            'HOLD': '⏸️',
            'AVOID': '❌'
        }
        return emoji_map.get(signal, '❓')
    
    def get_signal_color(self, signal: str) -> str:
        """Get color for signal (for dashboard)"""
        color_map = {
            'BUY': 'green',
            'HOLD': 'orange',
            'AVOID': 'red'
        }
        return color_map.get(signal, 'gray')
