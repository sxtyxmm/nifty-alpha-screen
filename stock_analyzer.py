#!/usr/bin/env python3
"""
Stock Analyzer for Indian Markets
Analyzes fundamentals, technical indicators (EMA-44), and delivery data
to provide investment recommendations.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tabulate import tabulate
import os
import sys


class StockAnalyzer:
    """Analyzes Indian stocks with fundamentals, EMA-44, and delivery data."""
    
    def __init__(self, symbol):
        """
        Initialize the analyzer with a stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS' or just 'RELIANCE')
        """
        # Ensure symbol has .NS suffix for NSE
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            symbol = f"{symbol}.NS"
        
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
        self.fundamentals = {}
        self.price_data = None
        self.ema_44 = None
        self.ema_slope = None
        self.delivery_data = None
        self.delivery_trend = None
        
    def fetch_fundamentals(self):
        """Fetch fundamental data from Yahoo Finance."""
        try:
            info = self.ticker.info
            
            self.fundamentals = {
                'market_cap': info.get('marketCap', None),
                'pe_trailing': info.get('trailingPE', None),
                'pe_forward': info.get('forwardPE', None),
                'price_to_book': info.get('priceToBook', None),
                'debt_to_equity': info.get('debtToEquity', None),
                'roe': info.get('returnOnEquity', None),
                'beta': info.get('beta', None),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', None)),
                'company_name': info.get('longName', info.get('shortName', self.symbol)),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
            }
            
            return True
        except Exception as e:
            print(f"Error fetching fundamentals: {e}")
            return False
    
    def fetch_price_history(self, period='6mo'):
        """
        Fetch historical price data and calculate EMA-44.
        
        Args:
            period: Time period for history (default: 6 months)
        """
        try:
            # Fetch historical data
            self.price_data = self.ticker.history(period=period)
            
            if self.price_data.empty:
                print(f"No price data available for {self.symbol}")
                return False
            
            # Calculate EMA-44 using adjusted close
            if 'Close' in self.price_data.columns:
                self.price_data['EMA_44'] = self.price_data['Close'].ewm(span=44, adjust=False).mean()
                self.ema_44 = self.price_data['EMA_44'].iloc[-1]
                
                # Calculate EMA slope (change over last 5 days)
                if len(self.price_data) >= 5:
                    ema_5_days_ago = self.price_data['EMA_44'].iloc[-6]
                    self.ema_slope = (self.ema_44 - ema_5_days_ago) / ema_5_days_ago * 100
                else:
                    self.ema_slope = 0
                
                return True
            else:
                print("Close price data not available")
                return False
                
        except Exception as e:
            print(f"Error fetching price history: {e}")
            return False
    
    def load_delivery_data(self, csv_path=None):
        """
        Load NSE delivery data from CSV file.
        
        Args:
            csv_path: Path to bhavcopy CSV file
        """
        if csv_path is None or not os.path.exists(csv_path):
            print("Delivery data CSV not provided or not found.")
            self.delivery_data = None
            return False
        
        try:
            # Read CSV - format may vary, adjust as needed
            df = pd.read_csv(csv_path)
            
            # Extract base symbol (without .NS)
            base_symbol = self.symbol.replace('.NS', '').replace('.BO', '')
            
            # Try to find the symbol in the CSV
            # Common column names: SYMBOL, Symbol, symbol
            symbol_col = None
            for col in df.columns:
                if col.upper() == 'SYMBOL':
                    symbol_col = col
                    break
            
            if symbol_col is None:
                print("Cannot find SYMBOL column in CSV")
                return False
            
            # Filter for our symbol
            stock_data = df[df[symbol_col].str.upper() == base_symbol.upper()]
            
            if stock_data.empty:
                print(f"Symbol {base_symbol} not found in delivery data")
                return False
            
            # Extract delivery data (column names may vary)
            row = stock_data.iloc[0]
            
            # Common column mappings
            delivery_qty_cols = ['DELIV_QTY', 'DeliveryQuantity', 'Delivery Quantity']
            traded_qty_cols = ['TRADED_QTY', 'TradedQuantity', 'Traded Quantity', 'TTL_TRD_QNTY']
            
            deliv_qty = None
            traded_qty = None
            
            for col in delivery_qty_cols:
                if col in df.columns:
                    deliv_qty = row[col]
                    break
            
            for col in traded_qty_cols:
                if col in df.columns:
                    traded_qty = row[col]
                    break
            
            if deliv_qty is not None and traded_qty is not None and traded_qty > 0:
                self.delivery_data = {
                    'deliverable_qty': deliv_qty,
                    'traded_qty': traded_qty,
                    'delivery_pct': (deliv_qty / traded_qty) * 100
                }
                return True
            else:
                print("Could not extract delivery data from CSV")
                return False
                
        except Exception as e:
            print(f"Error loading delivery data: {e}")
            return False
    
    def analyze_delivery_trend(self, csv_paths=None):
        """
        Analyze 3-day delivery trend if multiple CSV files are provided.
        
        Args:
            csv_paths: List of CSV paths for last 3 days
        """
        if csv_paths is None or len(csv_paths) < 2:
            self.delivery_trend = "insufficient_data"
            return
        
        delivery_pcts = []
        
        for csv_path in csv_paths[:3]:  # Max 3 days
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    base_symbol = self.symbol.replace('.NS', '').replace('.BO', '')
                    
                    symbol_col = None
                    for col in df.columns:
                        if col.upper() == 'SYMBOL':
                            symbol_col = col
                            break
                    
                    if symbol_col:
                        stock_data = df[df[symbol_col].str.upper() == base_symbol.upper()]
                        if not stock_data.empty:
                            row = stock_data.iloc[0]
                            
                            # Find delivery columns
                            deliv_qty = None
                            traded_qty = None
                            
                            for col in ['DELIV_QTY', 'DeliveryQuantity']:
                                if col in df.columns:
                                    deliv_qty = row[col]
                                    break
                            
                            for col in ['TRADED_QTY', 'TradedQuantity', 'TTL_TRD_QNTY']:
                                if col in df.columns:
                                    traded_qty = row[col]
                                    break
                            
                            if deliv_qty and traded_qty and traded_qty > 0:
                                delivery_pcts.append((deliv_qty / traded_qty) * 100)
                except:
                    continue
        
        # Analyze trend
        if len(delivery_pcts) >= 2:
            if delivery_pcts[-1] > delivery_pcts[0] * 1.05:  # 5% increase
                self.delivery_trend = "rising"
            elif delivery_pcts[-1] < delivery_pcts[0] * 0.95:  # 5% decrease
                self.delivery_trend = "falling"
            else:
                self.delivery_trend = "flat"
        else:
            self.delivery_trend = "insufficient_data"
    
    def calculate_score(self):
        """
        Calculate investment score from -2 to +3.
        
        Returns:
            tuple: (score, reasons)
        """
        score = 0
        reasons = []
        
        # Check if we have current price
        current_price = self.fundamentals.get('current_price')
        if current_price is None and self.price_data is not None:
            current_price = self.price_data['Close'].iloc[-1]
        
        # 1. EMA-44 position (+1 if above, -1 if below)
        if self.ema_44 is not None and current_price is not None:
            if current_price > self.ema_44:
                score += 1
                pct_above = ((current_price - self.ema_44) / self.ema_44) * 100
                reasons.append(f"✓ Price above EMA-44 by {pct_above:.2f}% (Bullish)")
            else:
                score -= 1
                pct_below = ((self.ema_44 - current_price) / self.ema_44) * 100
                reasons.append(f"✗ Price below EMA-44 by {pct_below:.2f}% (Bearish)")
        
        # 2. EMA slope (+1 if rising, -1 if falling)
        if self.ema_slope is not None:
            if self.ema_slope > 1:  # Rising by >1%
                score += 1
                reasons.append(f"✓ EMA-44 rising ({self.ema_slope:.2f}% over 5 days)")
            elif self.ema_slope < -1:  # Falling by >1%
                score -= 1
                reasons.append(f"✗ EMA-44 falling ({self.ema_slope:.2f}% over 5 days)")
            else:
                reasons.append(f"○ EMA-44 flat ({self.ema_slope:.2f}% over 5 days)")
        
        # 3. Delivery percentage (+1 if >35%, 0 otherwise)
        if self.delivery_data is not None:
            deliv_pct = self.delivery_data['delivery_pct']
            if deliv_pct > 35:
                score += 1
                reasons.append(f"✓ High delivery % ({deliv_pct:.2f}% > 35%)")
            else:
                reasons.append(f"○ Moderate delivery % ({deliv_pct:.2f}%)")
        else:
            reasons.append("○ Delivery data not available")
        
        # 4. Fundamentals check (PE ratio)
        pe = self.fundamentals.get('pe_trailing')
        if pe is not None:
            if pe < 25 and pe > 0:  # Reasonable PE
                score += 0.5
                reasons.append(f"✓ Reasonable P/E ({pe:.2f})")
            elif pe > 40:
                score -= 0.5
                reasons.append(f"✗ High P/E ({pe:.2f})")
            else:
                reasons.append(f"○ P/E at {pe:.2f}")
        
        # 5. ROE check
        roe = self.fundamentals.get('roe')
        if roe is not None:
            roe_pct = roe * 100
            if roe_pct > 15:
                score += 0.5
                reasons.append(f"✓ Strong ROE ({roe_pct:.2f}%)")
            elif roe_pct < 0:
                score -= 0.5
                reasons.append(f"✗ Negative ROE ({roe_pct:.2f}%)")
            else:
                reasons.append(f"○ ROE at {roe_pct:.2f}%")
        
        # Cap score between -2 and +3
        score = max(-2, min(3, score))
        
        return score, reasons
    
    def get_verdict(self, score):
        """
        Get investment verdict based on score.
        
        Args:
            score: Investment score
            
        Returns:
            tuple: (verdict, confidence)
        """
        if score >= 2:
            return "INVEST", "High"
        elif score >= 1:
            return "INVEST", "Moderate"
        elif score >= 0:
            return "HOLD", "Moderate"
        elif score >= -1:
            return "AVOID", "Moderate"
        else:
            return "AVOID", "High"
    
    def format_number(self, num, prefix=''):
        """Format large numbers for display."""
        if num is None:
            return "N/A"
        
        if num >= 1e7:  # 1 crore
            return f"{prefix}{num/1e7:.2f} Cr"
        elif num >= 1e5:  # 1 lakh
            return f"{prefix}{num/1e5:.2f} L"
        else:
            return f"{prefix}{num:.2f}"
    
    def generate_report(self):
        """Generate comprehensive analysis report."""
        print("=" * 80)
        print(f"STOCK ANALYSIS REPORT: {self.fundamentals.get('company_name', self.symbol)}")
        print(f"Symbol: {self.symbol}")
        print(f"Sector: {self.fundamentals.get('sector', 'N/A')} | Industry: {self.fundamentals.get('industry', 'N/A')}")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Key Fundamentals Table
        print("📊 KEY FUNDAMENTALS")
        print("-" * 80)
        
        current_price = self.fundamentals.get('current_price')
        if current_price is None and self.price_data is not None:
            current_price = self.price_data['Close'].iloc[-1]
        
        fundamentals_data = [
            ["Current Price", f"₹{current_price:.2f}" if current_price else "N/A"],
            ["Market Cap", self.format_number(self.fundamentals.get('market_cap'), '₹')],
            ["P/E (Trailing)", f"{self.fundamentals.get('pe_trailing', 'N/A'):.2f}" if self.fundamentals.get('pe_trailing') else "N/A"],
            ["P/E (Forward)", f"{self.fundamentals.get('pe_forward', 'N/A'):.2f}" if self.fundamentals.get('pe_forward') else "N/A"],
            ["Price to Book", f"{self.fundamentals.get('price_to_book', 'N/A'):.2f}" if self.fundamentals.get('price_to_book') else "N/A"],
            ["Debt to Equity", f"{self.fundamentals.get('debt_to_equity', 'N/A'):.2f}" if self.fundamentals.get('debt_to_equity') else "N/A"],
            ["ROE", f"{self.fundamentals.get('roe', 0)*100:.2f}%" if self.fundamentals.get('roe') else "N/A"],
            ["Beta", f"{self.fundamentals.get('beta', 'N/A'):.2f}" if self.fundamentals.get('beta') else "N/A"],
        ]
        
        print(tabulate(fundamentals_data, headers=["Metric", "Value"], tablefmt="grid"))
        print()
        
        # EMA Trend Table
        print("📈 EMA-44 TREND ANALYSIS")
        print("-" * 80)
        
        if self.ema_44 is not None and current_price is not None:
            position = "ABOVE ✓" if current_price > self.ema_44 else "BELOW ✗"
            deviation = ((current_price - self.ema_44) / self.ema_44) * 100
            
            ema_data = [
                ["Current Price", f"₹{current_price:.2f}"],
                ["EMA-44", f"₹{self.ema_44:.2f}"],
                ["Position", position],
                ["Deviation", f"{deviation:+.2f}%"],
                ["EMA Slope (5d)", f"{self.ema_slope:+.2f}%" if self.ema_slope is not None else "N/A"],
                ["Trend", "Rising ↗" if self.ema_slope and self.ema_slope > 1 else "Falling ↘" if self.ema_slope and self.ema_slope < -1 else "Flat →"],
            ]
            
            print(tabulate(ema_data, headers=["Metric", "Value"], tablefmt="grid"))
        else:
            print("EMA data not available")
        print()
        
        # Delivery Data Table
        print("📦 NSE DELIVERY DATA")
        print("-" * 80)
        
        if self.delivery_data is not None:
            delivery_table = [
                ["Deliverable Qty", f"{self.delivery_data['deliverable_qty']:,.0f}"],
                ["Traded Qty", f"{self.delivery_data['traded_qty']:,.0f}"],
                ["Delivery %", f"{self.delivery_data['delivery_pct']:.2f}%"],
                ["Assessment", "High ✓" if self.delivery_data['delivery_pct'] > 35 else "Moderate" if self.delivery_data['delivery_pct'] > 20 else "Low"],
                ["3-Day Trend", self.delivery_trend if self.delivery_trend else "N/A"],
            ]
            
            print(tabulate(delivery_table, headers=["Metric", "Value"], tablefmt="grid"))
        else:
            print("⚠️  Delivery data not available.")
            print("   To include delivery analysis, provide bhavcopy CSV file(s).")
        print()
        
        # Calculate score and verdict
        score, reasons = self.calculate_score()
        verdict, confidence = self.get_verdict(score)
        
        # Fundamental Grade
        print("⭐ FUNDAMENTAL GRADE")
        print("-" * 80)
        
        # Calculate fundamental grade
        grade_points = 0
        grade_max = 0
        
        if self.fundamentals.get('pe_trailing'):
            grade_max += 1
            if 0 < self.fundamentals['pe_trailing'] < 25:
                grade_points += 1
        
        if self.fundamentals.get('roe'):
            grade_max += 1
            if self.fundamentals['roe'] > 0.15:
                grade_points += 1
        
        if self.fundamentals.get('debt_to_equity') is not None:
            grade_max += 1
            if self.fundamentals['debt_to_equity'] < 1:
                grade_points += 1
        
        if grade_max > 0:
            grade_pct = (grade_points / grade_max) * 100
            if grade_pct >= 80:
                grade = "A (Excellent)"
            elif grade_pct >= 60:
                grade = "B (Good)"
            elif grade_pct >= 40:
                grade = "C (Fair)"
            else:
                grade = "D (Weak)"
        else:
            grade = "Insufficient Data"
        
        print(f"Grade: {grade} ({grade_points}/{grade_max} criteria met)")
        print()
        
        # Final Verdict
        print("🎯 FINAL VERDICT")
        print("=" * 80)
        
        verdict_color = "🟢" if verdict == "INVEST" else "🟡" if verdict == "HOLD" else "🔴"
        
        print(f"{verdict_color} Decision: {verdict}")
        print(f"Score: {score:.1f} / 3.0")
        print(f"Confidence: {confidence}")
        print()
        print("Reasoning:")
        for i, reason in enumerate(reasons, 1):
            print(f"  {i}. {reason}")
        print()
        print("=" * 80)
        
        return {
            'verdict': verdict,
            'score': score,
            'confidence': confidence,
            'reasons': reasons
        }


def main():
    """Main function to run stock analysis."""
    if len(sys.argv) < 2:
        print("Usage: python stock_analyzer.py <SYMBOL> [delivery_csv_path]")
        print("Example: python stock_analyzer.py RELIANCE")
        print("Example: python stock_analyzer.py RELIANCE /path/to/bhavcopy.csv")
        sys.exit(1)
    
    symbol = sys.argv[1]
    delivery_csv = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Analyzing {symbol}...")
    print()
    
    # Create analyzer
    analyzer = StockAnalyzer(symbol)
    
    # Fetch fundamentals
    print("Fetching fundamentals...")
    if not analyzer.fetch_fundamentals():
        print("Failed to fetch fundamentals. Please check the symbol.")
        sys.exit(1)
    
    # Fetch price history and calculate EMA
    print("Fetching price history and calculating EMA-44...")
    if not analyzer.fetch_price_history():
        print("Failed to fetch price history.")
        sys.exit(1)
    
    # Load delivery data if provided
    if delivery_csv:
        print(f"Loading delivery data from {delivery_csv}...")
        analyzer.load_delivery_data(delivery_csv)
    
    print()
    
    # Generate report
    analyzer.generate_report()


if __name__ == "__main__":
    main()
