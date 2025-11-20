#!/usr/bin/env python3
"""
NSE Stock Analysis CLI - High-Performance Async Version
10-20x faster than sync version using async/await
"""

import argparse
import sys
import asyncio
from pathlib import Path
from tabulate import tabulate
import time
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.async_pipeline import AsyncStockDataPipeline
from src.utils.logger import setup_logger
from src.data_fetchers import NSEDataFetcher

# Setup logger
logger = setup_logger("cli_async", log_file="logs/cli_async.log", level="INFO")


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_performance_stats(start_time: float, total_stocks: int):
    """Print performance statistics"""
    elapsed = time.time() - start_time
    stocks_per_sec = total_stocks / elapsed if elapsed > 0 else 0
    
    print(f"\n⚡ PERFORMANCE")
    print(f"Total time: {elapsed:.2f}s")
    print(f"Processing rate: {stocks_per_sec:.1f} stocks/second")
    print(f"Average time per stock: {elapsed/total_stocks:.3f}s" if total_stocks > 0 else "")


async def analyze_single_stock_async(symbol: str, use_delivery: bool = True):
    """Analyze a single stock using async pipeline"""
    print(f"\n🔍 Analyzing {symbol} (async mode)...\n")
    
    start_time = time.time()
    pipeline = AsyncStockDataPipeline(max_workers=1, use_delivery=use_delivery)
    
    result = await pipeline._analyze_stock_async(symbol)
    
    if result:
        # Print detailed analysis
        print_header(f"📈 Analysis for {result['Symbol']} - {result['Company']}")
        
        print("\n📊 BASIC INFORMATION")
        print("-" * 80)
        print(f"Sector: {result['Sector']}")
        print(f"Market Cap: ₹{result['Market_Cap_Cr']:.0f} Cr")
        print(f"Current Price: ₹{result['Price']:.2f}")
        
        print("\n📈 TECHNICAL ANALYSIS")
        print("-" * 80)
        print(f"EMA-44: ₹{result['EMA-44']:.2f}")
        print(f"Price vs EMA: {result['Price_vs_EMA']} ({result['Price_Diff_%']:+.2f}%)")
        print(f"EMA Slope: {result['EMA_Slope_%']:+.2f}%")
        print(f"Trend: {result['Trend']}")
        
        print("\n💼 FUNDAMENTAL ANALYSIS")
        print("-" * 80)
        print(f"P/E Ratio: {result['P/E']:.2f}")
        print(f"ROE: {result['ROE_%']:.2f}%")
        print(f"Debt/Equity: {result['Debt/Equity']:.2f}")
        
        if result['Delivery_%'] > 0:
            print("\n📦 DELIVERY DATA")
            print("-" * 80)
            print(f"Delivery %: {result['Delivery_%']:.2f}%")
            print(f"Trend: {result['Delivery_Trend']}")
        
        print("\n🎯 SCORE BREAKDOWN")
        print("-" * 80)
        print(f"Technical Score: {result['Tech_Score']:.2f}")
        print(f"Fundamental Score: {result['Fund_Score']:.2f}")
        print(f"Delivery Score: {result['Deliv_Score']:.2f}")
        
        print_header("🎯 FINAL VERDICT")
        signal_emoji = {'BUY': '🚀', 'HOLD': '⏸️', 'AVOID': '❌'}
        print(f"\n{signal_emoji.get(result['Signal'], '❓')} Signal: {result['Signal']}")
        print(f"Score: {result['Score']:.2f} / 5.0")
        print("=" * 80 + "\n")
        
        print_performance_stats(start_time, 1)
    else:
        print(f"❌ Failed to analyze {symbol}")


async def scan_all_stocks_async(top_n: int = 30, use_delivery: bool = True, limit: Optional[int] = None):
    """Scan all NSE stocks using async pipeline"""
    print(f"\n🚀 Scanning stocks with ASYNC pipeline (10-20x faster)...\n")
    
    start_time = time.time()
    
    pipeline = AsyncStockDataPipeline(max_workers=50, use_delivery=use_delivery)
    
    # Optionally warmup delivery cache for massive speedup
    if use_delivery and pipeline.delivery_fetcher:
        print("🔥 Warming up delivery data cache (90 days for smart money detection)...")
        warmup_start = time.time()
        cached = pipeline.delivery_fetcher.warmup_cache(days=90, max_workers=10)
        print(f"✓ Cache warmed up in {time.time() - warmup_start:.2f}s ({cached} files)\n")
    
    df = await pipeline.fetch_all_data_async(limit=limit)
    
    if df.empty:
        print("❌ No data retrieved")
        return
    
    # Show top BUY signals (sorted by score)
    buys = df[df['Signal'] == 'BUY'].nlargest(top_n, 'Score')
    
    print_header(f"🚀 TOP {len(buys)} BUY SIGNALS (EMA Retracement + Smart Money)")
    
    display_columns = [
        'Symbol', 'Company', 'Daily_Diff_%', 'Weekly_Diff_%',
        'Delivery_Qty_Spike', 'Has_Qty_Spike', 'Score', 'Signal'
    ]
    
    print(tabulate(
        buys[display_columns],
        headers='keys',
        tablefmt='grid',
        floatfmt='.2f',
        showindex=False
    ))
    
    # Summary
    summary = pipeline.get_summary()
    print(f"\n📊 SUMMARY")
    print(f"Total Analyzed: {summary['total_stocks']}")
    print(f"🚀 BUY Signals: {summary['buy_signals']}")
    print(f"⏸️ HOLD Signals: {summary['hold_signals']}")
    print(f"❌ AVOID Signals: {summary['avoid_signals']}")
    print(f"✗ Failed: {summary['failed_stocks']}")
    print(f"⭐ Avg Score: {summary['avg_score']}")
    
    # Performance stats
    print_performance_stats(start_time, summary['total_stocks'])
    
    # Export
    print(f"\n💾 Exporting results...")
    export_paths = await pipeline.export_async()
    print(f"✓ CSV: {export_paths['csv']}")
    print(f"✓ Excel: {export_paths['excel']}")
    
    # Cache stats
    cache_stats = pipeline.get_cache_stats()
    print(f"\n📊 CACHE STATS")
    print(f"YFinance cached items: {cache_stats['yfinance']['total_items']}")
    print(f"Results DataFrame cached: {cache_stats['results_cached']}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NSE Stock Analysis CLI - ASYNC VERSION (10-20x faster)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_async.py --symbol RELIANCE
  python cli_async.py --scan --top 30
  python cli_async.py --scan --limit 100 --no-delivery
  python cli_async.py --scan --top 50  # Full scan of 435+ stocks
        """
    )
    
    parser.add_argument(
        '--symbol',
        type=str,
        help='Single stock symbol to analyze'
    )
    
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Scan all NSE stocks (async mode)'
    )
    
    parser.add_argument(
        '--top',
        type=int,
        default=30,
        help='Number of top results to show (default: 30)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of stocks to process (default: all)'
    )
    
    parser.add_argument(
        '--no-delivery',
        action='store_true',
        help='Skip delivery data fetching (faster)'
    )
    
    args = parser.parse_args()
    
    use_delivery = not args.no_delivery
    
    try:
        if args.symbol:
            asyncio.run(analyze_single_stock_async(args.symbol, use_delivery))
        elif args.scan:
            asyncio.run(scan_all_stocks_async(args.top, use_delivery, args.limit))
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
