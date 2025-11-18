#!/usr/bin/env python3
"""
CLI Tool for Stock Analysis
Simple command-line interface for quick analysis
"""

import argparse
import sys
import pandas as pd
from data_pipeline import StockDataPipeline
from nse_data_fetcher import NSEDataFetcher
from tabulate import tabulate


def analyze_single_stock(symbol, use_delivery=True):
    """Analyze a single stock."""
    print(f"\nAnalyzing {symbol}...\n")
    
    pipeline = StockDataPipeline(symbols=[symbol], max_workers=1)
    df = pipeline.fetch_all_data(use_delivery=use_delivery)
    
    if df.empty:
        print(f"❌ Could not fetch data for {symbol}")
        return
    
    stock = df.iloc[0]
    
    # Display results
    print("=" * 80)
    print(f"STOCK ANALYSIS: {stock['company_name']} ({symbol})")
    print("=" * 80)
    print()
    
    # Fundamentals
    print("📊 FUNDAMENTALS")
    print("-" * 80)
    fundamentals_data = [
        ["Current Price", f"₹{stock['current_price']:.2f}"],
        ["Market Cap", f"₹{stock['market_cap']/1e7:.2f} Cr" if stock['market_cap'] else "N/A"],
        ["P/E (Trailing)", f"{stock['pe_trailing']:.2f}" if stock['pe_trailing'] else "N/A"],
        ["P/E (Forward)", f"{stock['pe_forward']:.2f}" if stock['pe_forward'] else "N/A"],
        ["Price to Book", f"{stock['price_to_book']:.2f}" if stock['price_to_book'] else "N/A"],
        ["ROE", f"{stock['roe']*100:.2f}%" if stock['roe'] else "N/A"],
        ["Debt to Equity", f"{stock['debt_to_equity']:.2f}" if stock['debt_to_equity'] else "N/A"],
        ["Beta", f"{stock['beta']:.2f}" if stock['beta'] else "N/A"],
        ["Sector", stock['sector']],
    ]
    print(tabulate(fundamentals_data, headers=["Metric", "Value"], tablefmt="grid"))
    print()
    
    # Technical
    print("📈 TECHNICAL ANALYSIS")
    print("-" * 80)
    technical_data = [
        ["EMA-44", f"₹{stock['ema_44']:.2f}"],
        ["Position", stock['price_vs_ema']],
        ["Deviation", f"{stock['price_ema_pct']:+.2f}%"],
        ["EMA Slope", f"{stock['ema_slope']:+.2f}%"],
    ]
    print(tabulate(technical_data, headers=["Metric", "Value"], tablefmt="grid"))
    print()
    
    # Delivery
    if use_delivery and stock['delivery_pct']:
        print("📦 DELIVERY DATA")
        print("-" * 80)
        delivery_data = [
            ["Delivery %", f"{stock['delivery_pct']:.2f}%"],
            ["Trend", stock['delivery_trend']],
        ]
        print(tabulate(delivery_data, headers=["Metric", "Value"], tablefmt="grid"))
        print()
    
    # Final verdict
    print("🎯 FINAL VERDICT")
    print("=" * 80)
    
    signal_emoji = "🚀" if stock['signal'] == 'BUY' else "⏸️" if stock['signal'] == 'HOLD' else "🛑"
    print(f"{signal_emoji} Signal: {stock['signal']}")
    print(f"Score: {stock['score']:.1f} / 5.0")
    print("=" * 80)
    print()


def analyze_multiple_stocks(symbols=None, top_n=20, use_delivery=True):
    """Analyze multiple stocks and show rankings."""
    if symbols is None:
        print("Fetching all NSE stocks...")
        pipeline = StockDataPipeline(max_workers=10)
    else:
        pipeline = StockDataPipeline(symbols=symbols, max_workers=10)
    
    df = pipeline.fetch_all_data(use_delivery=use_delivery)
    
    if df.empty:
        print("❌ Could not fetch data")
        return
    
    # Display top BUY signals
    print("\n" + "=" * 80)
    print(f"TOP {top_n} BUY OPPORTUNITIES")
    print("=" * 80)
    print()
    
    buy_stocks = df[df['signal'] == 'BUY'].head(top_n)
    
    if buy_stocks.empty:
        print("No BUY signals found.")
    else:
        display_data = []
        for idx, row in buy_stocks.iterrows():
            display_data.append([
                row['symbol'],
                row['company_name'][:30],
                f"₹{row['current_price']:.2f}",
                row['price_vs_ema'],
                f"{row['ema_slope']:+.2f}%",
                f"{row['delivery_pct']:.1f}%" if row['delivery_pct'] else "N/A",
                f"{row['score']:.1f}",
                row['signal']
            ])
        
        headers = ["Symbol", "Company", "Price", "EMA", "Slope", "Deliv%", "Score", "Signal"]
        print(tabulate(display_data, headers=headers, tablefmt="grid"))
    
    print()
    
    # Summary statistics
    print("📊 SUMMARY STATISTICS")
    print("-" * 80)
    summary_data = [
        ["Total Stocks", len(df)],
        ["BUY Signals", len(df[df['signal'] == 'BUY'])],
        ["HOLD Signals", len(df[df['signal'] == 'HOLD'])],
        ["AVOID Signals", len(df[df['signal'] == 'AVOID'])],
        ["Avg Score", f"{df['score'].mean():.2f}"],
        ["Max Score", f"{df['score'].max():.2f}"],
    ]
    print(tabulate(summary_data, headers=["Metric", "Value"], tablefmt="grid"))
    print()
    
    # Export option
    export = input("Export results to CSV? (y/n): ").strip().lower()
    if export == 'y':
        filename = f"stock_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        pipeline.export_to_csv(filename)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="NSE Stock Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single stock
  python cli.py --symbol RELIANCE
  
  # Analyze multiple stocks
  python cli.py --symbols RELIANCE TCS INFY
  
  # Get top 30 BUY signals from all NSE stocks
  python cli.py --scan --top 30
  
  # Analyze without delivery data (faster)
  python cli.py --symbol RELIANCE --no-delivery
        """
    )
    
    parser.add_argument('--symbol', type=str, help='Single stock symbol to analyze')
    parser.add_argument('--symbols', nargs='+', help='Multiple stock symbols to analyze')
    parser.add_argument('--scan', action='store_true', help='Scan all NSE stocks')
    parser.add_argument('--top', type=int, default=20, help='Number of top stocks to show (default: 20)')
    parser.add_argument('--no-delivery', action='store_true', help='Skip delivery data (faster)')
    
    args = parser.parse_args()
    
    use_delivery = not args.no_delivery
    
    if args.symbol:
        analyze_single_stock(args.symbol, use_delivery=use_delivery)
    elif args.symbols:
        analyze_multiple_stocks(symbols=args.symbols, top_n=args.top, use_delivery=use_delivery)
    elif args.scan:
        analyze_multiple_stocks(top_n=args.top, use_delivery=use_delivery)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
