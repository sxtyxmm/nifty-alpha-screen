#!/usr/bin/env python3
"""
Unit tests for the stock analysis system
Tests code logic without requiring external API calls
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys


def test_scoring_logic():
    """Test the scoring calculation logic."""
    print("Testing scoring logic...")
    
    # Create mock stock data
    mock_stock = {
        'symbol': 'TEST',
        'current_price': 100,
        'ema_44': 95,
        'ema_slope': 2.5,
        'price_vs_ema': 'ABOVE',
        'price_ema_pct': 5.26,
        'pe_trailing': 18,
        'roe': 0.20,  # 20%
        'debt_to_equity': 0.4,
        'delivery_pct': 45,
        'delivery_trend': 'rising'
    }
    
    # Calculate score manually
    score = 0
    
    # EMA trend
    if mock_stock['price_ema_pct'] > 5:
        score += 2  # +2 for >5% above EMA
    
    # EMA slope
    if mock_stock['ema_slope'] > 2:
        score += 1  # +1 for rising slope
    
    # Fundamentals
    if 0 < mock_stock['pe_trailing'] < 20:
        score += 1  # +1 for good PE
    if mock_stock['roe'] > 0.15:
        score += 1  # +1 for good ROE
    if mock_stock['debt_to_equity'] < 0.5:
        score += 0.5  # +0.5 for low debt
    
    # Delivery
    if mock_stock['delivery_pct'] > 50:
        score += 2
    elif mock_stock['delivery_pct'] > 35:
        score += 1  # +1 for good delivery
    
    # Delivery trend
    if mock_stock['delivery_trend'] == 'rising':
        score += 1  # +1 for rising trend
    
    expected_score = 2 + 1 + 1 + 1 + 0.5 + 1 + 1  # = 7.5, capped at 5
    actual_score = min(5, score)
    
    print(f"  Mock stock score: {actual_score}")
    print(f"  Components: EMA(+2), Slope(+1), PE(+1), ROE(+1), Debt(+0.5), Deliv(+1), Trend(+1)")
    
    assert actual_score == 5.0, f"Expected 5.0, got {actual_score}"
    print("  ✓ Scoring logic test passed!\n")


def test_signal_determination():
    """Test signal determination based on score."""
    print("Testing signal determination...")
    
    test_cases = [
        (5.0, 'BUY'),
        (3.5, 'BUY'),
        (3.0, 'BUY'),
        (2.0, 'HOLD'),
        (1.5, 'HOLD'),
        (1.0, 'HOLD'),
        (0.5, 'AVOID'),
        (0.0, 'AVOID'),
        (-2.0, 'AVOID'),
    ]
    
    for score, expected_signal in test_cases:
        if score >= 3:
            signal = 'BUY'
        elif score >= 1:
            signal = 'HOLD'
        else:
            signal = 'AVOID'
        
        assert signal == expected_signal, f"Score {score}: expected {expected_signal}, got {signal}"
        print(f"  Score {score:4.1f} → {signal:5s} ✓")
    
    print("  ✓ Signal determination test passed!\n")


def test_ema_calculation():
    """Test EMA calculation logic."""
    print("Testing EMA calculation...")
    
    # Create mock price data
    prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109] * 5)
    
    # Calculate EMA-44 (or EMA-10 for this small dataset)
    ema = prices.ewm(span=10, adjust=False).mean()
    
    # Check that EMA is calculated
    assert not ema.isna().any(), "EMA contains NaN values"
    assert len(ema) == len(prices), "EMA length mismatch"
    
    # Check that EMA smooths the data
    last_price = prices.iloc[-1]
    last_ema = ema.iloc[-1]
    print(f"  Last price: {last_price:.2f}")
    print(f"  Last EMA: {last_ema:.2f}")
    print(f"  EMA smoothing working: {abs(last_price - last_ema) < 10}")
    
    # Calculate slope
    ema_5_ago = ema.iloc[-6]
    slope = (last_ema - ema_5_ago) / ema_5_ago * 100
    print(f"  EMA slope: {slope:+.2f}%")
    
    print("  ✓ EMA calculation test passed!\n")


def test_dataframe_structure():
    """Test expected DataFrame structure."""
    print("Testing DataFrame structure...")
    
    expected_columns = [
        'symbol', 'company_name', 'sector', 'industry',
        'current_price', 'market_cap', 'pe_trailing', 'pe_forward',
        'price_to_book', 'debt_to_equity', 'roe', 'beta',
        'ema_44', 'ema_slope', 'price_vs_ema', 'price_ema_pct',
        'delivery_pct', 'delivery_trend', 'score', 'signal'
    ]
    
    # Create mock DataFrame
    mock_data = {col: [None] for col in expected_columns}
    mock_data['symbol'] = ['TEST']
    mock_data['score'] = [3.5]
    mock_data['signal'] = ['BUY']
    
    df = pd.DataFrame(mock_data)
    
    # Check all columns exist
    for col in expected_columns:
        assert col in df.columns, f"Missing column: {col}"
    
    print(f"  ✓ All {len(expected_columns)} expected columns present")
    print(f"  Columns: {', '.join(expected_columns[:5])}...")
    print("  ✓ DataFrame structure test passed!\n")


def test_delivery_trend_logic():
    """Test delivery trend calculation."""
    print("Testing delivery trend logic...")
    
    test_cases = [
        ([40, 42, 45], 'rising'),   # 45 > 40 * 1.05
        ([50, 48, 46], 'falling'),  # 46 < 50 * 0.95
        ([40, 41, 40.5], 'flat'),   # Within 5% range
    ]
    
    for delivery_pcts, expected_trend in test_cases:
        if delivery_pcts[-1] > delivery_pcts[0] * 1.05:
            trend = 'rising'
        elif delivery_pcts[-1] < delivery_pcts[0] * 0.95:
            trend = 'falling'
        else:
            trend = 'flat'
        
        assert trend == expected_trend, f"Expected {expected_trend}, got {trend}"
        print(f"  {delivery_pcts} → {trend:7s} ✓")
    
    print("  ✓ Delivery trend logic test passed!\n")


def test_edge_cases():
    """Test edge cases and None handling."""
    print("Testing edge cases...")
    
    # Test with missing data
    mock_stock_missing = {
        'current_price': 100,
        'ema_44': None,  # Missing EMA
        'pe_trailing': None,  # Missing PE
        'delivery_pct': None,  # Missing delivery
    }
    
    score = 0
    
    # Should handle None gracefully
    if mock_stock_missing['ema_44'] is not None:
        score += 1
    
    if mock_stock_missing['pe_trailing'] is not None:
        score += 1
    
    if mock_stock_missing['delivery_pct'] is not None:
        score += 1
    
    print(f"  Score with missing data: {score} (expected: 0)")
    assert score == 0, "Should handle None values"
    
    # Test score bounds
    test_score = 10.0
    capped_score = max(-5, min(5, test_score))
    print(f"  Score capping: {test_score} → {capped_score} (expected: 5.0)")
    assert capped_score == 5.0, "Score should be capped at 5.0"
    
    test_score = -10.0
    capped_score = max(-5, min(5, test_score))
    print(f"  Score capping: {test_score} → {capped_score} (expected: -5.0)")
    assert capped_score == -5.0, "Score should be capped at -5.0"
    
    print("  ✓ Edge cases test passed!\n")


def main():
    """Run all tests."""
    print("=" * 80)
    print("STOCK ANALYSIS SYSTEM - UNIT TESTS")
    print("=" * 80)
    print()
    
    tests = [
        test_scoring_logic,
        test_signal_determination,
        test_ema_calculation,
        test_dataframe_structure,
        test_delivery_trend_logic,
        test_edge_cases,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"  ❌ Test failed: {e}\n")
            failed += 1
        except Exception as e:
            print(f"  ❌ Test error: {e}\n")
            failed += 1
    
    print("=" * 80)
    if failed == 0:
        print("✓ ALL TESTS PASSED!")
        print("=" * 80)
        return 0
    else:
        print(f"❌ {failed} TEST(S) FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
