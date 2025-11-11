#!/usr/bin/env python3
"""
Unit tests for Nifty Alpha Screen functionality.
Tests core functions with synthetic/mock data.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TestMetricsCalculation(unittest.TestCase):
    """Test metrics calculation functions."""
    
    def setUp(self):
        """Set up test data."""
        # Create synthetic stock data
        dates = pd.date_range(end=datetime.now(), periods=300, freq='D')
        np.random.seed(42)
        prices = 100 * (1 + np.random.randn(300).cumsum() * 0.01)
        
        self.stock_df = pd.DataFrame({
            'Open': prices * 0.99,
            'High': prices * 1.01,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1000000, 5000000, 300)
        }, index=dates)
        
    def test_retracement_calculation(self):
        """Test 52-week high retracement calculation."""
        from nifty_alpha_screen import calculate_retracement_from_52w_high
        
        retracement = calculate_retracement_from_52w_high(self.stock_df)
        
        # Should return a valid percentage
        self.assertIsInstance(retracement, (int, float))
        self.assertGreaterEqual(retracement, 0)
        self.assertLessEqual(retracement, 100)
        
    def test_returns_calculation(self):
        """Test return calculation."""
        from nifty_alpha_screen import calculate_returns
        
        return_6m = calculate_returns(self.stock_df, 6)
        
        # Should return a valid percentage
        self.assertIsInstance(return_6m, (int, float))
        
    def test_volatility_calculation(self):
        """Test volatility calculation."""
        from nifty_alpha_screen import calculate_volatility
        
        volatility = calculate_volatility(self.stock_df, 6)
        
        # Should return a positive number
        self.assertIsInstance(volatility, (int, float))
        self.assertGreater(volatility, 0)


class TestFilteringAndRanking(unittest.TestCase):
    """Test filtering and ranking functions."""
    
    def setUp(self):
        """Set up test data."""
        self.test_df = pd.DataFrame({
            'Symbol': ['STOCK1.NS', 'STOCK2.NS', 'STOCK3.NS', 'STOCK4.NS'],
            'Retracement_52W': [10, 25, 35, 40],  # 2 should pass ≤30%
            'Return_6M': [20, 15, 10, 5],
            'Vol_Adj_Return_6M': [1.2, 0.9, 0.6, 0.3],
            'Relative_Strength_6M': [5, 3, -2, -5]  # 2 should pass >0
        })
    
    def test_filters_applied(self):
        """Test that filters are applied correctly."""
        from nifty_alpha_screen import apply_filters
        
        filtered = apply_filters(self.test_df)
        
        # Should filter based on criteria
        self.assertLessEqual(len(filtered), len(self.test_df))
        
        # All filtered stocks should meet criteria
        if len(filtered) > 0:
            self.assertTrue(all(filtered['Retracement_52W'] <= 30))
            self.assertTrue(all(filtered['Relative_Strength_6M'] > 0))
    
    def test_composite_score_calculation(self):
        """Test composite score calculation."""
        from nifty_alpha_screen import calculate_composite_score
        
        scored = calculate_composite_score(self.test_df.copy())
        
        # Should add composite score column
        self.assertIn('Composite_Score', scored.columns)
        
        # Scores should be between 0 and 1
        self.assertTrue(all(scored['Composite_Score'] >= 0))
        self.assertTrue(all(scored['Composite_Score'] <= 1))
    
    def test_top_stocks_selection(self):
        """Test top stocks selection."""
        from nifty_alpha_screen import calculate_composite_score, select_top_stocks
        
        scored = calculate_composite_score(self.test_df.copy())
        top_stocks = select_top_stocks(scored, top_n=2)
        
        # Should return correct number
        self.assertEqual(len(top_stocks), 2)
        
        # Should be sorted by score (descending)
        scores = top_stocks['Composite_Score'].values
        self.assertTrue(all(scores[i] >= scores[i+1] for i in range(len(scores)-1)))


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics calculations."""
    
    def setUp(self):
        """Set up test data."""
        dates = pd.date_range(end=datetime.now(), periods=12, freq='ME')
        values = [100, 105, 103, 108, 112, 110, 115, 118, 116, 120, 122, 125]
        self.returns = pd.Series(values, index=dates)
    
    def test_cagr_calculation(self):
        """Test CAGR calculation."""
        from nifty_alpha_screen import calculate_cagr
        
        cagr = calculate_cagr(self.returns)
        
        # Should return a valid percentage
        self.assertIsInstance(cagr, (int, float))
        
    def test_max_drawdown_calculation(self):
        """Test maximum drawdown calculation."""
        from nifty_alpha_screen import calculate_max_drawdown
        
        max_dd = calculate_max_drawdown(self.returns)
        
        # Should return a negative number or zero
        self.assertIsInstance(max_dd, (int, float))
        self.assertLessEqual(max_dd, 0)
    
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation."""
        from nifty_alpha_screen import calculate_sharpe_ratio
        
        sharpe = calculate_sharpe_ratio(self.returns)
        
        # Should return a valid number
        self.assertIsInstance(sharpe, (int, float))
    
    def test_win_rate_calculation(self):
        """Test win rate calculation."""
        from nifty_alpha_screen import calculate_win_rate
        
        win_rate = calculate_win_rate(self.returns)
        
        # Should return a percentage between 0 and 100
        self.assertIsInstance(win_rate, (int, float))
        self.assertGreaterEqual(win_rate, 0)
        self.assertLessEqual(win_rate, 100)


class TestDataFetching(unittest.TestCase):
    """Test data fetching functions."""
    
    def test_get_nifty_symbols(self):
        """Test getting Nifty symbols."""
        from nifty_alpha_screen import get_nifty_500_symbols
        
        symbols = get_nifty_500_symbols()
        
        # Should return a list
        self.assertIsInstance(symbols, list)
        
        # Should have some symbols
        self.assertGreater(len(symbols), 0)
        
        # Symbols should end with .NS
        for symbol in symbols:
            self.assertTrue(symbol.endswith('.NS'))


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestMetricsCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestFilteringAndRanking))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestDataFetching))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
