#!/usr/bin/env python3
"""
Example usage of the Financial Data Automation Assistant

This script demonstrates how to use the stock screener programmatically.
"""

from stock_screener import StockDataFetcher, Strategy1, Strategy2

def example_usage():
    """
    Example: Run both strategies and get results
    """
    print("Example: Financial Data Automation Assistant\n")
    
    # 1. Initialize the data fetcher
    # Use 'nifty200' or 'nifty500' for stock universe
    fetcher = StockDataFetcher(stock_universe='nifty200')
    
    # 2. Run Strategy 1: Momentum + Retracement
    print("Running Strategy 1...")
    strategy1 = Strategy1(fetcher)
    results_s1 = strategy1.run()
    
    # Access results as DataFrame
    if len(results_s1) > 0:
        print(f"\nTop 5 stocks from Strategy 1:")
        print(results_s1.head()[['Rank', 'Symbol', 'Combined_Score']])
        
        # Get specific stock details
        top_stock = results_s1.iloc[0]
        print(f"\nTop stock: {top_stock['Symbol']}")
        print(f"  - Combined Score: {top_stock['Combined_Score']}")
        print(f"  - 6M Return: {top_stock['Return_6M_%']}%")
        print(f"  - Sharpe Ratio: {top_stock['Sharpe_Ratio']}")
    
    # 3. Run Strategy 2: EMA Retracement
    print("\n\nRunning Strategy 2...")
    strategy2 = Strategy2(fetcher)
    results_s2 = strategy2.run()
    
    if len(results_s2) > 0:
        print(f"\nStocks from Strategy 2:")
        print(results_s2[['Symbol', 'Distance_from_EMA_%']])
    
    # 4. Save to custom filenames
    results_s1.to_csv('my_custom_strategy1.csv', index=False)
    results_s2.to_csv('my_custom_strategy2.csv', index=False)
    print("\n✓ Results saved to custom CSV files")

def filter_by_criteria():
    """
    Example: Filter results by custom criteria
    """
    print("\n\nExample: Custom Filtering\n")
    
    fetcher = StockDataFetcher(stock_universe='nifty200')
    strategy1 = Strategy1(fetcher)
    results = strategy1.run()
    
    if len(results) > 0:
        # Filter stocks with Sharpe ratio > 1.5
        high_sharpe = results[results['Sharpe_Ratio'] > 1.5]
        print(f"Stocks with Sharpe Ratio > 1.5: {len(high_sharpe)}")
        
        # Filter stocks with 6M return > 20%
        high_return = results[results['Return_6M_%'] > 20]
        print(f"Stocks with 6M Return > 20%: {len(high_return)}")
        
        # Combine filters
        best_stocks = results[
            (results['Sharpe_Ratio'] > 1.5) & 
            (results['Return_6M_%'] > 20)
        ]
        print(f"\nBest stocks (both criteria): {len(best_stocks)}")
        if len(best_stocks) > 0:
            print(best_stocks[['Symbol', 'Sharpe_Ratio', 'Return_6M_%']])

def main():
    """Run examples"""
    print("=" * 60)
    print("Financial Data Automation Assistant - Examples")
    print("=" * 60)
    
    # Run examples
    example_usage()
    # filter_by_criteria()  # Uncomment to run filtering example
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
