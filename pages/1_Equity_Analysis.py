# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT CLOUD TMP CACHE FIX - MUST BE AT VERY TOP
# ══════════════════════════════════════════════════════════════════════════════
import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
# ══════════════════════════════════════════════════════════════════════════════

"""
Quantum Market Suite - Equity Analysis Page
═══════════════════════════════════════════════════════════════════════════════
DATA SOURCE: yfinance (Yahoo Finance API)
FEATURES:
- KPI Tiles: LTP, Volume, % Change
- Line Chart: Historical price visualization
- Google Finance Safety Check (>2% mismatch = auto-restart)
- 3-Tab Master Excel Export
═══════════════════════════════════════════════════════════════════════════════
"""
import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import re
import io
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Equity | Quantum Market Suite",
    page_icon="📈",
    layout="wide"
)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "TCS"
if "equity_data" not in st.session_state:
    st.session_state["equity_data"] = None
if "price_validated" not in st.session_state:
    st.session_state["price_validated"] = False
if "google_price" not in st.session_state:
    st.session_state["google_price"] = None

# ══════════════════════════════════════════════════════════════════════════════
# TERMINAL THEME CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #0a0f0d 0%, #0d1117 50%, #0a0f0d 100%);
    font-family: 'Inter', sans-serif;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid #30363d;
    box-shadow: 0 0 10px rgba(0, 255, 65, 0.1);
}
[data-testid="stMetricLabel"] {
    color: #00ff41 !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stMetricValue"] {
    color: #e6edf3 !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    border-right: 1px solid #30363d;
}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: #00ff41 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stButton > button {
    background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
    color: #ffffff;
    font-weight: 600;
    border: 1px solid #238636;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
    box-shadow: 0 0 20px rgba(46, 160, 67, 0.4);
}

.source-badge {
    background: rgba(88, 166, 255, 0.15);
    color: #58a6ff;
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid rgba(88, 166, 255, 0.3);
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
}

.validation-ok {
    background: rgba(0, 255, 65, 0.1);
    color: #00ff41;
    padding: 8px 16px;
    border-radius: 4px;
    border: 1px solid rgba(0, 255, 65, 0.3);
    font-family: 'JetBrains Mono', monospace;
}
.validation-warn {
    background: rgba(255, 71, 87, 0.1);
    color: #ff4757;
    padding: 8px 16px;
    border-radius: 4px;
    border: 1px solid rgba(255, 71, 87, 0.3);
    font-family: 'JetBrains Mono', monospace;
}

.price-up { color: #00ff41 !important; }
.price-down { color: #ff4757 !important; }
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
# GOOGLE FINANCE SCRAPER (TRUTH REFERENCE)
# ══════════════════════════════════════════════════════════════════════════════
def get_google_finance_price(ticker: str) -> float:
    """Fetch price from Google Finance as Truth Reference."""
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:NSE"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            match = re.search(r'data-last-price="([\d.]+)"', response.text)
            if match:
                return float(match.group(1))
    except Exception:
        pass
    return 0.0


def validate_price(yf_price: float, ticker: str, tolerance: float = 0.02) -> tuple:
    """Validate yfinance price against Google Finance. >2% mismatch triggers restart."""
    google_price = get_google_finance_price(ticker)
    if google_price > 0:
        diff_pct = abs(yf_price - google_price) / google_price
        return diff_pct <= tolerance, google_price, diff_pct
    return True, 0, 0

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
        "open": latest['Open'], "high": latest['High'], "low": latest['Low'],
        "close": latest['Close'], "volume": latest['Volume'],
        "change": change, "change_pct": change_pct
    }

# ══════════════════════════════════════════════════════════════════════════════
# 3-TAB MASTER EXCEL GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
def create_master_excel(df: pd.DataFrame, ticker: str, quote: dict) -> bytes:
    """Create 3-tab Master Excel file."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Tab 1: Historical Data
        df.to_excel(writer, sheet_name='Historical_Data', index=False)
        
        # Tab 2: Summary Statistics
        summary_data = {
            'Metric': ['Ticker', 'Period Start', 'Period End', 'Total Records',
                      'Latest Open', 'Latest High', 'Latest Low', 'Latest Close',
                      'Day Change', 'Day Change %', 'Latest Volume',
                      'Avg Close', 'Max High', 'Min Low', 'Avg Volume'],
            'Value': [ticker, str(df['Date'].min())[:10], str(df['Date'].max())[:10], len(df),
                     f"₹{quote['open']:,.2f}", f"₹{quote['high']:,.2f}", 
                     f"₹{quote['low']:,.2f}", f"₹{quote['close']:,.2f}",
                     f"₹{quote['change']:+,.2f}", f"{quote['change_pct']:+.2f}%",
                     f"{quote['volume']:,.0f}",
                     f"₹{df['Close'].mean():,.2f}", f"₹{df['High'].max():,.2f}",
                     f"₹{df['Low'].min():,.2f}", f"{df['Volume'].mean():,.0f}"]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        # Tab 3: Technical Analysis
        tech_df = df.copy()
        tech_df['SMA_5'] = tech_df['Close'].rolling(window=5).mean()
        tech_df['SMA_20'] = tech_df['Close'].rolling(window=20).mean()
        tech_df['Daily_Return'] = tech_df['Close'].pct_change() * 100
        tech_df['Volatility'] = tech_df['Daily_Return'].rolling(window=5).std()
        tech_df.to_excel(writer, sheet_name='Technical_Analysis', index=False)
    
    return output.getvalue()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📈 Equity Analysis")
    st.caption("Historical & Live Data")
    st.divider()
    
    st.markdown("### 📊 Stock Selection")
    default_ticker = st.session_state.get("selected_ticker", "TCS")
    default_idx = NSE_STOCKS.index(default_ticker) if default_ticker in NSE_STOCKS else 0
    selected_ticker = st.selectbox("Select Stock", NSE_STOCKS, index=default_idx)
    st.session_state["selected_ticker"] = selected_ticker
    st.divider()
    
    st.markdown("### 📅 Time Period")
    period = st.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=0)
    st.divider()
    
    st.markdown("### 💾 Persistence Vault")
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
if st.button("🚀 FETCH EQUITY DATA", use_container_width=True, type="primary"):
    with st.spinner(f"Fetching {selected_ticker}.NS from yfinance..."):
        df = fetch_equity_data(selected_ticker, period)
        if not df.empty:
            st.session_state["equity_data"] = df
            st.session_state["selected_ticker"] = selected_ticker
            st.session_state["last_fetch_time"] = datetime.now().strftime('%H:%M:%S')
            
            # Google Finance Safety Check
            latest_close = df.iloc[-1]['Close']
            is_valid, google_price, diff_pct = validate_price(latest_close, selected_ticker)
            st.session_state["price_validated"] = is_valid
            st.session_state["google_price"] = google_price
            
            if is_valid:
                st.success(f"✅ Fetched {len(df)} rows for {selected_ticker} | Price validated ✓")
            else:
                st.warning(f"⚠️ Price mismatch detected! yfinance: ₹{latest_close:.2f} vs Google: ₹{google_price:.2f} ({diff_pct*100:.1f}%)")
                st.cache_data.clear()
                df = fetch_equity_data(selected_ticker, period)
                st.session_state["equity_data"] = df
                st.info("🔄 Auto-restarted session due to >2% price mismatch")
        else:
            st.error("❌ No data returned")

st.divider()

# Display Data
if st.session_state.get("equity_data") is not None and not st.session_state["equity_data"].empty:
    df = st.session_state["equity_data"]
    quote = get_latest_quote(df)
    
    # Validation Status
    if st.session_state.get("price_validated"):
        google_price = st.session_state.get("google_price", 0)
        if google_price > 0:
            st.markdown(f'<div class="validation-ok">✅ PRICE VALIDATED | Google Finance: ₹{google_price:,.2f}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="validation-ok">✅ PRICE VALIDATED</div>', unsafe_allow_html=True)
    
    st.markdown("### 📊 KPI Metrics")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(label="LTP (CLOSE)", value=f"₹{quote['close']:,.2f}",
                  delta=f"{quote['change']:+.2f} ({quote['change_pct']:+.2f}%)")
    with k2:
        st.metric(label="VOLUME", value=f"{quote['volume']:,.0f}")
    with k3:
        st.metric(label="DAY HIGH", value=f"₹{quote['high']:,.2f}")
    with k4:
        st.metric(label="DAY LOW", value=f"₹{quote['low']:,.2f}")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("OPEN", f"₹{quote['open']:,.2f}")
    with m2:
        st.metric("AVG PRICE", f"₹{(quote['high'] + quote['low']) / 2:,.2f}")
    with m3:
        st.metric("DAY RANGE", f"₹{quote['high'] - quote['low']:,.2f}")
    with m4:
        st.metric("RECORDS", f"{len(df)} days")
    
    st.divider()
    st.markdown("### 📈 Price Chart")
    chart_df = df[['Date', 'Close']].copy().set_index('Date')
    st.line_chart(chart_df, use_container_width=True, height=400)
    
    st.markdown("### 📊 Volume Chart")
    vol_df = df[['Date', 'Volume']].copy().set_index('Date')
    st.bar_chart(vol_df, use_container_width=True, height=200)
    
    st.divider()
    st.markdown("### 📋 Historical Data")
    display_df = df.copy()
    display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Export Section
    st.divider()
    st.markdown("### 📥 Export Options")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False),
            f"{selected_ticker}_equity.csv",
            "text/csv",
            use_container_width=True
        )
    with col2:
        excel_data = create_master_excel(df, selected_ticker, quote)
        st.download_button(
            "📥 Download 3-Tab Master Excel",
            excel_data,
            f"{selected_ticker}_Master_Equity.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
else:
    st.info("👆 Click **FETCH EQUITY DATA** to load historical prices from yfinance")

st.divider()
st.caption(f"📈 Quantum Market Suite | Equity Analysis | {datetime.now().strftime('%H:%M:%S')}")
