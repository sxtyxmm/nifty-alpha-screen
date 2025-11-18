#!/usr/bin/env python3
"""
Streamlit Dashboard for Stock Analysis
Advanced dashboard with charts, filters, and comprehensive analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import yfinance as yf
from data_pipeline import StockDataPipeline
from nse_data_fetcher import NSEDataFetcher
import time


# Page configuration
st.set_page_config(
    page_title="NSE Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .buy-signal {
        color: #00ff00;
        font-weight: bold;
    }
    .hold-signal {
        color: #ffaa00;
        font-weight: bold;
    }
    .avoid-signal {
        color: #ff0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_stock_data(use_delivery=True, num_stocks=None):
    """Load and cache stock data."""
    fetcher = NSEDataFetcher()
    symbols = fetcher.fetch_all_nse_symbols()
    
    # Limit number of stocks if specified
    if num_stocks:
        symbols = symbols[:num_stocks]
    
    pipeline = StockDataPipeline(symbols=symbols, max_workers=10)
    df = pipeline.fetch_all_data(use_delivery=use_delivery)
    
    return df


@st.cache_data(ttl=300)
def load_stock_history(symbol, period='6mo'):
    """Load historical data for a specific stock."""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        hist = ticker.history(period=period)
        hist['EMA_44'] = hist['Close'].ewm(span=44, adjust=False).mean()
        return hist
    except:
        return None


@st.cache_data(ttl=3600)
def load_delivery_history(symbol, days=10):
    """Load delivery data history for a stock."""
    try:
        fetcher = NSEDataFetcher()
        bhavcopy_data = fetcher.fetch_multiple_bhavcopy(days=days)
        
        delivery_history = []
        for date in sorted(bhavcopy_data.keys()):
            df = bhavcopy_data[date]
            delivery = fetcher.get_delivery_data(symbol, df)
            if delivery:
                delivery_history.append({
                    'date': date,
                    'delivery_pct': delivery['delivery_pct']
                })
        
        return pd.DataFrame(delivery_history)
    except:
        return None


def create_price_ema_chart(hist_data, symbol):
    """Create interactive price and EMA-44 chart."""
    fig = go.Figure()
    
    # Add Close price
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['Close'],
        name='Close Price',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Add EMA-44
    fig.add_trace(go.Scatter(
        x=hist_data.index,
        y=hist_data['EMA_44'],
        name='EMA-44',
        line=dict(color='#ff7f0e', width=2, dash='dash')
    ))
    
    # Highlight crossovers
    hist_data['crossover'] = (hist_data['Close'] > hist_data['EMA_44']).astype(int).diff()
    
    # Bullish crossovers
    bullish = hist_data[hist_data['crossover'] == 1]
    if not bullish.empty:
        fig.add_trace(go.Scatter(
            x=bullish.index,
            y=bullish['Close'],
            mode='markers',
            name='Bullish Crossover',
            marker=dict(color='green', size=10, symbol='triangle-up')
        ))
    
    # Bearish crossovers
    bearish = hist_data[hist_data['crossover'] == -1]
    if not bearish.empty:
        fig.add_trace(go.Scatter(
            x=bearish.index,
            y=bearish['Close'],
            mode='markers',
            name='Bearish Crossover',
            marker=dict(color='red', size=10, symbol='triangle-down')
        ))
    
    fig.update_layout(
        title=f'{symbol} - Price vs EMA-44',
        xaxis_title='Date',
        yaxis_title='Price (₹)',
        hovermode='x unified',
        height=500,
        showlegend=True,
        template='plotly_white'
    )
    
    return fig


def create_delivery_chart(delivery_df):
    """Create delivery percentage bar chart."""
    if delivery_df is None or delivery_df.empty:
        return None
    
    fig = go.Figure()
    
    # Determine color based on delivery %
    colors = ['green' if x > 35 else 'orange' if x > 20 else 'red' 
              for x in delivery_df['delivery_pct']]
    
    fig.add_trace(go.Bar(
        x=delivery_df['date'],
        y=delivery_df['delivery_pct'],
        marker_color=colors,
        text=delivery_df['delivery_pct'].round(1),
        textposition='auto',
    ))
    
    # Add threshold line at 35%
    fig.add_hline(y=35, line_dash="dash", line_color="green", 
                  annotation_text="High Accumulation (35%)")
    
    fig.update_layout(
        title='Delivery % Trend',
        xaxis_title='Date',
        yaxis_title='Delivery %',
        height=400,
        template='plotly_white'
    )
    
    return fig


def display_fundamentals_box(stock_row):
    """Display fundamentals in a structured box."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Market Cap", 
                  f"₹{stock_row['market_cap']/1e7:.2f} Cr" if pd.notna(stock_row['market_cap']) else "N/A")
        st.metric("P/E (Trailing)", 
                  f"{stock_row['pe_trailing']:.2f}" if pd.notna(stock_row['pe_trailing']) else "N/A")
        st.metric("Price to Book", 
                  f"{stock_row['price_to_book']:.2f}" if pd.notna(stock_row['price_to_book']) else "N/A")
    
    with col2:
        st.metric("ROE", 
                  f"{stock_row['roe']*100:.2f}%" if pd.notna(stock_row['roe']) else "N/A")
        st.metric("Debt to Equity", 
                  f"{stock_row['debt_to_equity']:.2f}" if pd.notna(stock_row['debt_to_equity']) else "N/A")
        st.metric("Beta", 
                  f"{stock_row['beta']:.2f}" if pd.notna(stock_row['beta']) else "N/A")
    
    with col3:
        st.metric("Sector", stock_row['sector'])
        st.metric("Industry", stock_row['industry'])
        st.metric("P/E (Forward)", 
                  f"{stock_row['pe_forward']:.2f}" if pd.notna(stock_row['pe_forward']) else "N/A")


def display_score_card(stock_row):
    """Display score and verdict in a prominent card."""
    score = stock_row['score']
    signal = stock_row['signal']
    
    # Determine color based on signal
    if signal == 'BUY':
        color = '#00ff00'
        emoji = '🚀'
    elif signal == 'HOLD':
        color = '#ffaa00'
        emoji = '⏸️'
    else:
        color = '#ff0000'
        emoji = '🛑'
    
    # Create score breakdown
    st.markdown(f"""
    <div style='background-color: {color}22; padding: 30px; border-radius: 15px; border: 3px solid {color};'>
        <h1 style='text-align: center; color: {color}; margin: 0;'>{emoji} {signal}</h1>
        <h2 style='text-align: center; margin: 10px 0;'>Score: {score:.1f} / 5.0</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Score breakdown
    st.markdown("### Score Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**EMA Analysis:**")
        st.write(f"- Position: {stock_row['price_vs_ema']}")
        st.write(f"- Deviation: {stock_row['price_ema_pct']:+.2f}%")
        st.write(f"- Slope: {stock_row['ema_slope']:+.2f}%")
    
    with col2:
        st.write("**Delivery Data:**")
        if pd.notna(stock_row['delivery_pct']):
            st.write(f"- Delivery %: {stock_row['delivery_pct']:.2f}%")
            st.write(f"- Trend: {stock_row['delivery_trend']}")
        else:
            st.write("- Delivery data not available")


def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<h1 class="main-header">📈 NSE Stock Analysis Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Data loading options
        st.subheader("Data Options")
        use_delivery = st.checkbox("Include Delivery Data", value=True,
                                   help="Fetch NSE delivery data (slower)")
        
        num_stocks = st.number_input("Number of Stocks", 
                                     min_value=10, max_value=500, value=100, step=10,
                                     help="Limit analysis to top N stocks")
        
        # Load data button
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        
        # Filters
        st.subheader("Filters")
        signal_filter = st.multiselect(
            "Signal Type",
            options=['BUY', 'HOLD', 'AVOID'],
            default=['BUY', 'HOLD', 'AVOID']
        )
        
        min_score = st.slider("Minimum Score", -5.0, 5.0, -5.0, 0.5)
        
        st.divider()
        
        # Display options
        st.subheader("Display Options")
        show_charts = st.checkbox("Show Charts", value=True)
        show_fundamentals = st.checkbox("Show Fundamentals", value=True)
        
        st.divider()
        
        # Export options
        st.subheader("Export")
        if st.button("📥 Export to CSV"):
            st.session_state['export_csv'] = True
        
        if st.button("📊 Export to Excel"):
            st.session_state['export_excel'] = True
    
    # Load data
    with st.spinner('Loading stock data... This may take a few minutes.'):
        try:
            df = load_stock_data(use_delivery=use_delivery, num_stocks=num_stocks)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.info("Using fallback data...")
            df = load_stock_data(use_delivery=False, num_stocks=50)
    
    if df.empty:
        st.error("No data available. Please try again later.")
        return
    
    # Apply filters
    filtered_df = df[
        (df['signal'].isin(signal_filter)) & 
        (df['score'] >= min_score)
    ]
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Stock Details", "📈 Rankings"])
    
    with tab1:
        # Summary metrics
        st.header("Market Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            buy_count = len(df[df['signal'] == 'BUY'])
            st.metric("BUY Signals", buy_count, 
                     f"{buy_count/len(df)*100:.1f}%")
        
        with col2:
            hold_count = len(df[df['signal'] == 'HOLD'])
            st.metric("HOLD Signals", hold_count,
                     f"{hold_count/len(df)*100:.1f}%")
        
        with col3:
            avoid_count = len(df[df['signal'] == 'AVOID'])
            st.metric("AVOID Signals", avoid_count,
                     f"{avoid_count/len(df)*100:.1f}%")
        
        with col4:
            avg_score = df['score'].mean()
            st.metric("Avg Score", f"{avg_score:.2f}",
                     f"Max: {df['score'].max():.1f}")
        
        st.divider()
        
        # Top BUY stocks
        st.header("🚀 Top BUY Opportunities")
        top_buys = df[df['signal'] == 'BUY'].head(10)
        
        if not top_buys.empty:
            display_cols = ['symbol', 'company_name', 'current_price', 'price_vs_ema', 
                           'ema_slope', 'delivery_pct', 'score', 'signal']
            st.dataframe(
                top_buys[display_cols].style.background_gradient(
                    subset=['score'], cmap='RdYlGn', vmin=-5, vmax=5
                ),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No BUY signals found with current filters.")
        
        # Signal distribution
        st.header("Signal Distribution")
        signal_counts = df['signal'].value_counts()
        
        fig_pie = px.pie(
            values=signal_counts.values,
            names=signal_counts.index,
            title='Signal Distribution',
            color=signal_counts.index,
            color_discrete_map={'BUY': 'green', 'HOLD': 'orange', 'AVOID': 'red'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        st.header("🔍 Detailed Stock Analysis")
        
        # Stock selector
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_symbol = st.selectbox(
                "Select Stock",
                options=filtered_df['symbol'].tolist(),
                format_func=lambda x: f"{x} - {filtered_df[filtered_df['symbol']==x]['company_name'].iloc[0]}"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")
            if st.button("🔄 Refresh Stock"):
                st.cache_data.clear()
        
        if selected_symbol:
            stock_row = filtered_df[filtered_df['symbol'] == selected_symbol].iloc[0]
            
            # Stock header
            st.subheader(f"{stock_row['company_name']} ({selected_symbol})")
            st.write(f"**Current Price:** ₹{stock_row['current_price']:.2f}")
            
            st.divider()
            
            # Score card
            display_score_card(stock_row)
            
            st.divider()
            
            # Charts
            if show_charts:
                st.subheader("📈 Technical Charts")
                
                # Price and EMA chart
                hist_data = load_stock_history(selected_symbol)
                if hist_data is not None and not hist_data.empty:
                    fig_price = create_price_ema_chart(hist_data, selected_symbol)
                    st.plotly_chart(fig_price, use_container_width=True)
                else:
                    st.warning("Price history not available")
                
                # Delivery chart
                if use_delivery:
                    delivery_df = load_delivery_history(selected_symbol)
                    if delivery_df is not None and not delivery_df.empty:
                        fig_delivery = create_delivery_chart(delivery_df)
                        if fig_delivery:
                            st.plotly_chart(fig_delivery, use_container_width=True)
                
                st.divider()
            
            # Fundamentals
            if show_fundamentals:
                st.subheader("📊 Fundamentals")
                display_fundamentals_box(stock_row)
    
    with tab3:
        st.header("📈 Complete Stock Rankings")
        
        # Additional filters for ranking table
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sector_filter = st.multiselect(
                "Sector",
                options=sorted(df['sector'].dropna().unique()),
                default=[]
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort By",
                options=['score', 'current_price', 'delivery_pct', 'ema_slope', 'market_cap'],
                index=0
            )
        
        with col3:
            sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)
        
        # Apply sector filter
        ranking_df = filtered_df.copy()
        if sector_filter:
            ranking_df = ranking_df[ranking_df['sector'].isin(sector_filter)]
        
        # Sort
        ascending = (sort_order == "Ascending")
        ranking_df = ranking_df.sort_values(sort_by, ascending=ascending)
        
        # Display table
        st.dataframe(
            ranking_df[['symbol', 'company_name', 'sector', 'current_price', 
                       'price_vs_ema', 'ema_slope', 'delivery_pct', 'score', 'signal']].style.applymap(
                lambda x: 'color: green; font-weight: bold' if x == 'BUY' 
                else 'color: orange; font-weight: bold' if x == 'HOLD'
                else 'color: red; font-weight: bold' if x == 'AVOID'
                else '', subset=['signal']
            ).background_gradient(subset=['score'], cmap='RdYlGn', vmin=-5, vmax=5),
            use_container_width=True,
            height=600
        )
        
        # Download buttons
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            csv = ranking_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f'stock_analysis_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
            )
        
        with col2:
            # For Excel, we need to create it in memory
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                ranking_df.to_excel(writer, index=False, sheet_name='Analysis')
            
            st.download_button(
                label="📊 Download as Excel",
                data=buffer.getvalue(),
                file_name=f'stock_analysis_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>📊 NSE Stock Analysis Dashboard | Data refreshes every hour</p>
        <p>⚠️ For educational purposes only. Not financial advice.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
