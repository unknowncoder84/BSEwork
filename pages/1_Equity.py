"""
PRK Exchange Suite - Equity Page
═══════════════════════════════════════════════════════════════════════════════
DATA SOURCE: yfinance (Yahoo Finance API)
- yf.download("TCS.NS", period="1mo")
- Most accurate source for historical numbers

FEATURES:
- KPI Tiles: Today's Open, High, Low, Close
- Line Chart: Historical price visualization
- Persistence: selected_ticker in st.session_state
═══════════════════════════════════════════════════════════════════════════════
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Equity | PRK Exchange Suite",
    page_icon="📈",
    layout="wide"
)

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp { font-family: 'Inter', sans-serif; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid rgba(255,255,255,0.1);
}

[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] > div {
    font-size: 0.85rem !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 8px;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

.kpi-positive { color: #22c55e !important; }
.kpi-negative { color: #ef4444 !important; }

.source-badge {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid rgba(59, 130, 246, 0.3);
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STOCK LIST
# ══════════════════════════════════════════════════════════════════════════════
NSE_STOCKS = [
    "TCS", "RELIANCE", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "SBIN",
    "BHARTIARTL", "KOTAKBANK", "ITC", "LT", "AXISBANK", "ASIANPAINT", "MARUTI",
    "BAJFINANCE", "TITAN", "SUNPHARMA", "ULTRACEMCO", "NESTLEIND", "WIPRO",
    "HCLTECH", "POWERGRID", "NTPC", "TATAMOTORS", "TATASTEEL", "ONGC", "JSWSTEEL",
    "ADANIENT", "ADANIPORTS", "TECHM", "INDUSINDBK", "BAJAJFINSV", "GRASIM"
]

# ══════════════════════════════════════════════════════════════════════════════
# YFINANCE DATA FETCHER
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def fetch_equity_data(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """
    Fetch equity data using yfinance.
    Example: yf.download("TCS.NS", period="1mo")
    """
    try:
        import yfinance as yf
        
        # Add .NS suffix for NSE stocks
        symbol = f"{ticker}.NS"
        
        # Download data
        df = yf.download(symbol, period=period, progress=False)
        
        if df.empty:
            return pd.DataFrame()
        
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
        
        # Reset index to make Date a column
        df = df.reset_index()
        
        # Ensure proper column names
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


def get_latest_quote(df: pd.DataFrame) -> dict:
    """Extract latest quote from dataframe."""
    if df.empty:
        return {"open": 0, "high": 0, "low": 0, "close": 0, "volume": 0, "change": 0, "change_pct": 0}
    
    latest = df.iloc[-1]
    prev_close = df.iloc[-2]['Close'] if len(df) > 1 else latest['Open']
    
    change = latest['Close'] - prev_close
    change_pct = (change / prev_close * 100) if prev_close > 0 else 0
    
    return {
        "open": latest['Open'],
        "high": latest['High'],
        "low": latest['Low'],
        "close": latest['Close'],
        "volume": latest['Volume'],
        "change": change,
        "change_pct": change_pct
    }


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📈 PRK Exchange Suite")
    st.caption("Equity Analysis")
    
    st.divider()
    
    st.markdown("### 📊 Stock Selection")
    
    # Get ticker from session state
    default_ticker = st.session_state.get("selected_ticker", "TCS")
    default_idx = NSE_STOCKS.index(default_ticker) if default_ticker in NSE_STOCKS else 0
    
    selected_ticker = st.selectbox(
        "Select Stock",
        NSE_STOCKS,
        index=default_idx,
        key="equity_ticker_select"
    )
    
    # Update session state (persistence)
    st.session_state["selected_ticker"] = selected_ticker
    
    st.divider()
    
    st.markdown("### 📅 Time Period")
    period = st.selectbox(
        "Select Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=0,
        key="equity_period"
    )
    
    st.divider()
    
    st.markdown("### 💾 Session State")
    st.caption(f"Ticker: **{st.session_state.get('selected_ticker', 'None')}**")
    st.caption("Persists across pages ✓")
    
    st.divider()
    
    st.markdown("### 📡 Data Source")
    st.markdown('<span class="source-badge">yfinance</span>', unsafe_allow_html=True)
    st.caption(f"`yf.download('{selected_ticker}.NS')`")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 📈 Equity Analysis")
st.caption(f"Data Source: yfinance | Symbol: {selected_ticker}.NS | Period: {period}")

st.markdown(f'<span class="source-badge">yf.download("{selected_ticker}.NS", period="{period}")</span>', unsafe_allow_html=True)

st.divider()

# Fetch Button
if st.button("🚀 Fetch Equity Data", use_container_width=True, type="primary"):
    with st.spinner(f"Fetching {selected_ticker}.NS from yfinance..."):
        df = fetch_equity_data(selected_ticker, period)
        
        if not df.empty:
            st.session_state["equity_data"] = df
            st.session_state["selected_ticker"] = selected_ticker
            st.success(f"✅ Fetched {len(df)} rows for {selected_ticker}")
        else:
            st.error("❌ No data returned. Check ticker symbol.")

st.divider()

# Display Data
if st.session_state.get("equity_data") is not None and not st.session_state["equity_data"].empty:
    df = st.session_state["equity_data"]
    quote = get_latest_quote(df)
    
    # ══════════════════════════════════════════════════════════════════════════
    # KPI TILES (Metric Cards)
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("### 📊 Today's KPIs")
    
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.metric(
            label="OPEN",
            value=f"₹{quote['open']:,.2f}",
        )
    
    with k2:
        st.metric(
            label="HIGH",
            value=f"₹{quote['high']:,.2f}",
            delta=f"Day High"
        )
    
    with k3:
        st.metric(
            label="LOW",
            value=f"₹{quote['low']:,.2f}",
            delta=f"Day Low"
        )
    
    with k4:
        delta_color = "normal" if quote['change'] >= 0 else "inverse"
        st.metric(
            label="CLOSE",
            value=f"₹{quote['close']:,.2f}",
            delta=f"{quote['change']:+.2f} ({quote['change_pct']:+.2f}%)",
            delta_color=delta_color
        )
    
    # Additional Metrics
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("VOLUME", f"{quote['volume']:,.0f}")
    
    with m2:
        avg_price = (quote['high'] + quote['low']) / 2
        st.metric("AVG PRICE", f"₹{avg_price:,.2f}")
    
    with m3:
        range_val = quote['high'] - quote['low']
        st.metric("DAY RANGE", f"₹{range_val:,.2f}")
    
    with m4:
        st.metric("RECORDS", f"{len(df)} days")
    
    st.divider()
    
    # ══════════════════════════════════════════════════════════════════════════
    # LINE CHART
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("### 📈 Price Chart")
    
    # Prepare chart data
    chart_df = df[['Date', 'Close']].copy()
    chart_df = chart_df.set_index('Date')
    
    st.line_chart(chart_df, use_container_width=True, height=400)
    
    # Volume Chart
    st.markdown("### 📊 Volume Chart")
    vol_df = df[['Date', 'Volume']].copy()
    vol_df = vol_df.set_index('Date')
    st.bar_chart(vol_df, use_container_width=True, height=200)
    
    st.divider()
    
    # ══════════════════════════════════════════════════════════════════════════
    # DATA TABLE
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("### 📋 Historical Data")
    
    # Format for display
    display_df = df.copy()
    display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
    for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
    if 'Volume' in display_df.columns:
        display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,.0f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Download
    st.download_button(
        "📥 Download CSV",
        df.to_csv(index=False),
        f"{selected_ticker}_equity.csv",
        "text/csv",
        use_container_width=True
    )

else:
    st.info("👆 Click **Fetch Equity Data** to load historical prices from yfinance")
    
    # Show example
    st.markdown("### 📖 Example Usage")
    st.code("""
import yfinance as yf

# Fetch TCS data for 1 month
df = yf.download("TCS.NS", period="1mo")

# Returns: Date, Open, High, Low, Close, Adj Close, Volume
    """, language="python")

# Footer
st.divider()
st.caption(f"📈 PRK Exchange Suite | Equity Page | {datetime.now().strftime('%H:%M:%S')}")
st.caption(f"Data: yfinance (Yahoo Finance) | Symbol: {selected_ticker}.NS")
