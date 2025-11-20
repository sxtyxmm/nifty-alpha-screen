"""Fundamental Analyzer Module - Analyze fundamental metrics"""

from typing import Optional, Dict, Any
import logging

from ..utils.validators import validate_score

logger = logging.getLogger(__name__)


class FundamentalAnalyzer:
    """Analyze fundamental metrics for stocks"""
    
    def __init__(
        self,
        pe_low: float = 20,
        pe_high: float = 40,
        roe_good: float = 15,
        roe_poor: float = 0,
        debt_low: float = 0.5,
        debt_high: float = 2.0,
        pb_low: float = 1.5,
        pb_high: float = 5.0
    ):
        """
        Initialize fundamental analyzer
        
        Args:
            pe_low: Low P/E ratio threshold (good)
            pe_high: High P/E ratio threshold (expensive)
            roe_good: Good ROE percentage threshold
            roe_poor: Poor ROE percentage threshold
            debt_low: Low debt-to-equity ratio (good)
            debt_high: High debt-to-equity ratio (risky)
            pb_low: Low price-to-book ratio
            pb_high: High price-to-book ratio
        """
        self.pe_low = pe_low
        self.pe_high = pe_high
        self.roe_good = roe_good
        self.roe_poor = roe_poor
        self.debt_low = debt_low
        self.debt_high = debt_high
        self.pb_low = pb_low
        self.pb_high = pb_high
    
    def analyze(self, fundamentals: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Perform complete fundamental analysis
        
        Args:
            fundamentals: Dictionary with fundamental metrics
        
        Returns:
            Dictionary with fundamental analysis results or None if failed
        """
        if not fundamentals:
            logger.warning("No fundamental data provided")
            return None
        
        try:
            # Analyze each metric
            pe_analysis = self._analyze_pe_ratio(fundamentals.get('pe_ratio', 0))
            roe_analysis = self._analyze_roe(fundamentals.get('roe', 0))
            debt_analysis = self._analyze_debt(fundamentals.get('debt_to_equity', 0))
            pb_analysis = self._analyze_pb_ratio(fundamentals.get('pb_ratio', 0))
            
            # Calculate overall quality score
            quality_score = (
                pe_analysis['score'] +
                roe_analysis['score'] +
                debt_analysis['score'] +
                pb_analysis['score']
            ) / 4
            
            # Determine quality rating
            quality_rating = self._get_quality_rating(quality_score)
            
            return {
                'pe_analysis': pe_analysis,
                'roe_analysis': roe_analysis,
                'debt_analysis': debt_analysis,
                'pb_analysis': pb_analysis,
                'quality_score': round(quality_score, 2),
                'quality_rating': quality_rating,
                'market_cap': fundamentals.get('market_cap', 0),
                'sector': fundamentals.get('sector', 'N/A'),
                'industry': fundamentals.get('industry', 'N/A')
            }
            
        except Exception as e:
            logger.error(f"Error in fundamental analysis: {str(e)}")
            return None
    
    def _analyze_pe_ratio(self, pe_ratio: float) -> Dict[str, Any]:
        """
        Analyze P/E ratio
        
        Returns:
            Dictionary with P/E analysis and score (-1 to +1)
        """
        if pe_ratio <= 0:
            return {
                'value': pe_ratio,
                'rating': 'N/A',
                'score': 0,
                'message': 'No P/E ratio available'
            }
        
        if pe_ratio < self.pe_low:
            return {
                'value': pe_ratio,
                'rating': 'GOOD',
                'score': 1.0,
                'message': f'Low P/E ratio (< {self.pe_low})'
            }
        elif pe_ratio < self.pe_high:
            return {
                'value': pe_ratio,
                'rating': 'FAIR',
                'score': 0.0,
                'message': f'Moderate P/E ratio ({self.pe_low}-{self.pe_high})'
            }
        else:
            return {
                'value': pe_ratio,
                'rating': 'EXPENSIVE',
                'score': -1.0,
                'message': f'High P/E ratio (> {self.pe_high})'
            }
    
    def _analyze_roe(self, roe: float) -> Dict[str, Any]:
        """
        Analyze Return on Equity
        
        Returns:
            Dictionary with ROE analysis and score (-1 to +1)
        """
        if roe >= self.roe_good:
            return {
                'value': roe,
                'rating': 'EXCELLENT',
                'score': 1.0,
                'message': f'High ROE (≥ {self.roe_good}%)'
            }
        elif roe > self.roe_poor:
            return {
                'value': roe,
                'rating': 'FAIR',
                'score': 0.0,
                'message': f'Moderate ROE ({self.roe_poor}-{self.roe_good}%)'
            }
        else:
            return {
                'value': roe,
                'rating': 'POOR',
                'score': -1.0,
                'message': f'Low/Negative ROE (≤ {self.roe_poor}%)'
            }
    
    def _analyze_debt(self, debt_to_equity: float) -> Dict[str, Any]:
        """
        Analyze Debt-to-Equity ratio
        
        Returns:
            Dictionary with debt analysis and score (-0.5 to +0.5)
        """
        if debt_to_equity < 0:
            return {
                'value': debt_to_equity,
                'rating': 'N/A',
                'score': 0,
                'message': 'No debt data available'
            }
        
        if debt_to_equity < self.debt_low:
            return {
                'value': debt_to_equity,
                'rating': 'LOW',
                'score': 0.5,
                'message': f'Low debt (< {self.debt_low})'
            }
        elif debt_to_equity < self.debt_high:
            return {
                'value': debt_to_equity,
                'rating': 'MODERATE',
                'score': 0.0,
                'message': f'Moderate debt ({self.debt_low}-{self.debt_high})'
            }
        else:
            return {
                'value': debt_to_equity,
                'rating': 'HIGH',
                'score': -0.5,
                'message': f'High debt (> {self.debt_high})'
            }
    
    def _analyze_pb_ratio(self, pb_ratio: float) -> Dict[str, Any]:
        """
        Analyze Price-to-Book ratio
        
        Returns:
            Dictionary with P/B analysis and score (-0.5 to +0.5)
        """
        if pb_ratio <= 0:
            return {
                'value': pb_ratio,
                'rating': 'N/A',
                'score': 0,
                'message': 'No P/B ratio available'
            }
        
        if pb_ratio < self.pb_low:
            return {
                'value': pb_ratio,
                'rating': 'UNDERVALUED',
                'score': 0.5,
                'message': f'Low P/B ratio (< {self.pb_low})'
            }
        elif pb_ratio < self.pb_high:
            return {
                'value': pb_ratio,
                'rating': 'FAIR',
                'score': 0.0,
                'message': f'Moderate P/B ratio ({self.pb_low}-{self.pb_high})'
            }
        else:
            return {
                'value': pb_ratio,
                'rating': 'OVERVALUED',
                'score': -0.5,
                'message': f'High P/B ratio (> {self.pb_high})'
            }
    
    def _get_quality_rating(self, score: float) -> str:
        """Get overall quality rating based on score"""
        if score >= 0.75:
            return 'EXCELLENT'
        elif score >= 0.25:
            return 'GOOD'
        elif score >= -0.25:
            return 'FAIR'
        elif score >= -0.75:
            return 'POOR'
        else:
            return 'VERY_POOR'
