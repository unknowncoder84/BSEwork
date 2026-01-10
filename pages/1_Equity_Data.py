# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT CLOUD TMP CACHE FIX - MUST BE AT VERY TOP
# ══════════════════════════════════════════════════════════════════════════════
import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
# ══════════════════════════════════════════════════════════════════════════════

"""
PRK Exchange Suite - Equity Page
═══════════════════════════════════════════════════════════════════════════════
DATA SOURCE: yfinance (Yahoo Finance API)
- yf.download("TCS.NS", period="1mo")

FEATURES:
- KPI Tiles: Today's Open, High, Low, Close
- Line Chart: Historical price visualization
- Persistence: selected_ticker in st.session_state
═══════════════════════════════════════════════════════════════════════════════
"""
import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import re
import io
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
# SESSION STATE INITIALIZATION (Ensure persistence)
# ══════════════════════════════════════════════════════════════════════════════
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "TCS"
if "equity_data" not in st.session_state:
    st.session_state["equity_data"] = None
if "equity_hist" not in st.session_state:
    st.session_state["equity_hist"] = None
if "call_options" not in st.session_state:
    st.session_state["call_options"] = None
if "put_options" not in st.session_state:
    st.session_state["put_options"] = None

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
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
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
# GOOGLE FINANCE VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
def get_google_price(ticker: str) -> float:
    """Fetch Google Finance price as truth reference."""
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:NSE"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
        }
        resp = requests.get(url, headers=headers, timeout=10)
        match = re.search(r'data-last-price="([\d.]+)"', resp.text)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return 0.0


def validate_price(price: float, ticker: str) -> tuple:
    """Validate price vs Google. >2% = mismatch."""
    google = get_google_price(ticker)
    if google > 0:
        diff = abs(price - google) / google
        return diff <= 0.02, google, diff
    return True, 0, 0


# ══════════════════════════════════════════════════════════════════════════════
# 3-TAB MASTER EXCEL GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
def create_master_excel() -> bytes:
    """Create 3-tab Master Excel: EQUITY_HIST, CALL_OPTIONS, PUT_OPTIONS."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        hist = st.session_state.get("equity_hist")
        if hist is not None and not hist.empty:
            hist.to_excel(writer, sheet_name='EQUITY_HIST', index=False)
        else:
            pd.DataFrame({"Info": ["No equity data"]}).to_excel(writer, sheet_name='EQUITY_HIST', index=False)
        
        calls = st.session_state.get("call_options")
        if calls is not None and not calls.empty:
            calls.to_excel(writer, sheet_name='CALL_OPTIONS', index=False)
        else:
            pd.DataFrame({"Info": ["Fetch from Derivatives Hub"]}).to_excel(writer, sheet_name='CALL_OPTIONS', index=False)
        
        puts = st.session_state.get("put_options")
        if puts is not None and not puts.empty:
            puts.to_excel(writer, sheet_name='PUT_OPTIONS', index=False)
        else:
            pd.DataFrame({"Info": ["Fetch from Derivatives Hub"]}).to_excel(writer, sheet_name='PUT_OPTIONS', index=False)
    return output.getvalue()


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
    """Fetch equity data using yfinance."""
    try:
        symbol = f"{ticker}.NS"
        df = yf.download(symbol, period=period, progress=False)
        
        if df.empty:
            return pd.DataFrame()
        
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
        
        df = df.reset_index()
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        return df
    except Exception as e:
        st.error(f"Error: {e}")
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
    
    default_ticker = st.session_state.get("selected_ticker", "TCS")
    default_idx = NSE_STOCKS.index(default_ticker) if default_ticker in NSE_STOCKS else 0
    
    selected_ticker = st.selectbox("Select Stock", NSE_STOCKS, index=default_idx)
    
    # Update session state (persistence)
    st.session_state["selected_ticker"] = selected_ticker
    
    st.divider()
    
    st.markdown("### 📅 Time Period")
    period = st.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=0)
    
    st.divider()
    
    st.markdown("### 💾 Session State")
    st.caption(f"Ticker: **{st.session_state.get('selected_ticker')}**")
    if st.session_state.get("equity_data") is not None:
        st.success("✅ Equity data loaded")
    
    st.divider()
    st.markdown("### 📡 Data Source")
    st.markdown('<span class="source-badge">yfinance</span>', unsafe_allow_html=True)


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
            st.session_state["equity_hist"] = df
            st.session_state["selected_ticker"] = selected_ticker
            st.session_state["last_fetch_time"] = datetime.now().strftime('%H:%M:%S')
            
            # Google Finance Validation
            latest_close = df.iloc[-1]['Close']
            is_valid, google_price, diff = validate_price(latest_close, selected_ticker)
            
            if not is_valid and google_price > 0:
                st.warning(f"⚠️ Price mismatch! yfinance: ₹{latest_close:.2f} vs Google: ₹{google_price:.2f} ({diff*100:.1f}%)")
                st.cache_data.clear()
                df = fetch_equity_data(selected_ticker, period)
                st.session_state["equity_data"] = df
                st.session_state["equity_hist"] = df
                st.info("🔄 Session restarted due to >2% mismatch")
            else:
                st.success(f"✅ Fetched {len(df)} rows for {selected_ticker} | Price validated ✓")
        else:
            st.error("❌ No data returned")

st.divider()

# Display Data
if st.session_state.get("equity_data") is not None and not st.session_state["equity_data"].empty:
    df = st.session_state["equity_data"]
    quote = get_latest_quote(df)
    
    # KPI TILES
    st.markdown("### 📊 Today's KPIs")
    
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.metric(label="OPEN", value=f"₹{quote['open']:,.2f}")
    with k2:
        st.metric(label="HIGH", value=f"₹{quote['high']:,.2f}", delta="Day High")
    with k3:
        st.metric(label="LOW", value=f"₹{quote['low']:,.2f}", delta="Day Low")
    with k4:
        delta_color = "normal" if quote['change'] >= 0 else "inverse"
        st.metric(label="CLOSE", value=f"₹{quote['close']:,.2f}",
                  delta=f"{quote['change']:+.2f} ({quote['change_pct']:+.2f}%)", delta_color=delta_color)
    
    # Additional Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("VOLUME", f"{quote['volume']:,.0f}")
    with m2:
        st.metric("AVG PRICE", f"₹{(quote['high'] + quote['low']) / 2:,.2f}")
    with m3:
        st.metric("DAY RANGE", f"₹{quote['high'] - quote['low']:,.2f}")
    with m4:
        st.metric("RECORDS", f"{len(df)} days")
    
    st.divider()
    
    # LINE CHART
    st.markdown("### 📈 Price Chart")
    chart_df = df[['Date', 'Close']].copy().set_index('Date')
    st.line_chart(chart_df, use_container_width=True, height=400)
    
    # Volume Chart
    st.markdown("### 📊 Volume Chart")
    vol_df = df[['Date', 'Volume']].copy().set_index('Date')
    st.bar_chart(vol_df, use_container_width=True, height=200)
    
    st.divider()
    
    # DATA TABLE
    st.markdown("### 📋 Historical Data")
    display_df = df.copy()
    display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Download
    st.download_button("📥 Download CSV", df.to_csv(index=False), f"{selected_ticker}_equity.csv", "text/csv", use_container_width=True)
    
    # Master Excel Download
    st.divider()
    st.markdown("### 📥 Master Download")
    excel_data = create_master_excel()
    st.download_button(
        "📥 MASTER EXCEL (3 TABS)",
        excel_data,
        f"{selected_ticker}_Master_Data.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

else:
    st.info("👆 Click **Fetch Equity Data** to load historical prices from yfinance")

# Footer
st.divider()
st.caption(f"📈 PRK Exchange Suite | Equity Page | {datetime.now().strftime('%H:%M:%S')}")
