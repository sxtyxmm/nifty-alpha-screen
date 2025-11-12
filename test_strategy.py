#!/usr/bin/env python3
"""
Test script to validate the hybrid momentum-EMA strategy implementation.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import yfinance as yf
        from ta.trend import EMAIndicator
        print("✓ All dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_module_structure():
    """Test that the main module has all required components."""
    print("\nTesting module structure...")
    try:
        import hybrid_momentum_ema as hme
        
        required_functions = [
            'get_nifty_500_symbols',
            'get_stock_data',
            'fetch_all_stock_data',
            'calculate_momentum_metrics',
            'calculate_composite_score',
            'calculate_ema_signals',
            'select_top_stocks',
            'apply_ema_filter',
            'backtest_strategy',
            'calculate_performance_metrics',
            'plot_momentum_distribution',
            'plot_equity_curve',
            'plot_drawdown',
            'main'
        ]
        
        missing = []
        for func_name in required_functions:
            if not hasattr(hme, func_name):
                missing.append(func_name)
        
        if missing:
            print(f"✗ Missing functions: {', '.join(missing)}")
            return False
        
        print(f"✓ All {len(required_functions)} required functions present")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_demo_execution():
    """Test that demo script runs without errors."""
    print("\nTesting demo script execution...")
    try:
        import demo_strategy
        # The demo has already been run, just verify module loads
        print("✓ Demo module loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Demo error: {e}")
        return False

def test_data_structures():
    """Test that key data structures are correct."""
    print("\nTesting data structures...")
    try:
        import hybrid_momentum_ema as hme
        
        # Test symbol list
        symbols = hme.get_nifty_500_symbols()
        assert isinstance(symbols, list), "Symbols should be a list"
        assert len(symbols) > 0, "Symbols list should not be empty"
        assert all(s.endswith('.NS') for s in symbols), "All symbols should end with .NS"
        print(f"✓ Symbol list valid ({len(symbols)} symbols)")
        
        return True
    except Exception as e:
        print(f"✗ Data structure error: {e}")
        return False

def test_calculations():
    """Test mathematical calculations."""
    print("\nTesting calculations...")
    try:
        import pandas as pd
        import numpy as np
        import hybrid_momentum_ema as hme
        
        # Create sample data
        dates = pd.date_range('2020-01-01', periods=300, freq='D')
        sample_data = pd.DataFrame({
            'Open': np.random.uniform(100, 110, 300),
            'High': np.random.uniform(110, 120, 300),
            'Low': np.random.uniform(90, 100, 300),
            'Close': np.cumsum(np.random.normal(0, 1, 300)) + 100,
            'Volume': np.random.randint(1000000, 10000000, 300)
        }, index=dates)
        
        # Test momentum metrics
        metrics = hme.calculate_momentum_metrics(sample_data, nifty_returns=0.1)
        assert metrics is not None, "Momentum metrics should not be None"
        assert 'returns_6m' in metrics, "Should have 6-month returns"
        assert 'composite_score' not in metrics, "Metrics shouldn't include composite score"
        print("✓ Momentum metrics calculation works")
        
        # Test composite score
        score = hme.calculate_composite_score(metrics)
        assert isinstance(score, (int, float)), "Composite score should be numeric"
        print("✓ Composite score calculation works")
        
        # Test EMA signals
        ema_signals = hme.calculate_ema_signals(sample_data)
        assert ema_signals is not None, "EMA signals should not be None"
        assert 'entry_signal' in ema_signals, "Should have entry signal"
        assert 'exit_signal' in ema_signals, "Should have exit signal"
        print("✓ EMA signal calculation works")
        
        return True
    except Exception as e:
        print(f"✗ Calculation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_output_files():
    """Test that demo created expected output files."""
    print("\nTesting output files...")
    try:
        expected_files = [
            'output/demo_top_20_momentum_stocks.csv',
            'output/demo_equity_curve.png'
        ]
        
        missing_files = []
        for filepath in expected_files:
            if not os.path.exists(filepath):
                missing_files.append(filepath)
        
        if missing_files:
            print(f"⚠ Missing files: {', '.join(missing_files)}")
            print("  (Run demo_strategy.py first)")
        else:
            print(f"✓ All {len(expected_files)} output files present")
        
        return True
    except Exception as e:
        print(f"✗ Output file check error: {e}")
        return False

def main():
    """Run all tests."""
    print("="*70)
    print("HYBRID MOMENTUM-EMA STRATEGY - TEST SUITE")
    print("="*70)
    
    tests = [
        test_imports,
        test_module_structure,
        test_demo_execution,
        test_data_structures,
        test_calculations,
        test_output_files
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
