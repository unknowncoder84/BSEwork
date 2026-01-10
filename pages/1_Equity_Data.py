# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT CLOUD PERMISSION FIX - MUST BE AT VERY TOP
# ══════════════════════════════════════════════════════════════════════════════
import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
# ══════════════════════════════════════════════════════════════════════════════

"""
Quantum Market Suite - Equity Data Page
═══════════════════════════════════════════════════════════════════════════════
DATA: nsepython nse_quote() + yfinance historical
VALIDATION: Google Finance (>2% mismatch = auto-restart)
OUTPUT: Clean rows and columns only
═══════════════════════════════════════════════════════════════════════════════
"""
import streamlit as st
import pandas as pd
import requests
import re
import io
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Equity Data | Quantum", page_icon="📈", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "TCS"
if "equity_data" not in st.session_state:
    st.session_state["equity_data"] = None
if "equity_hist" not in st.session_state:
    st.session_state["equity_hist"] = None

# ══════════════════════════════════════════════════════════════════════════════
# TERMINAL THEME CSS (Dark Mode with Green/Red Highlights)
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
    background: rgba(0, 255, 65, 0.15);
    color: #00ff41;
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid rgba(0, 255, 65, 0.3);
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
    "BHARTIARTL", "KOTAKBANK", "ITC", "LT", "AXISBANK", "MARUTI", "BAJFINANCE",
    "TITAN", "SUNPHARMA", "TATAMOTORS", "TATASTEEL", "WIPRO", "HCLTECH", "TECHM"
]

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE FINANCE VALIDATION (TRUTH REFERENCE)
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


def validate_price(nse_price: float, ticker: str) -> tuple:
    """Validate NSE price vs Google. >2% = mismatch."""
    google = get_google_price(ticker)
    if google > 0:
        diff = abs(nse_price - google) / google
        return diff <= 0.02, google, diff
    return True, 0, 0

# ══════════════════════════════════════════════════════════════════════════════
# NSE DATA FETCHERS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=120)
def fetch_live_quote(ticker: str) -> dict:
    """Fetch live quote using nsepython nse_quote()."""
    try:
        from nsepython import nse_quote
        data = nse_quote(ticker)
        if data and 'priceInfo' in data:
            pi = data['priceInfo']
            return {
                "symbol": ticker,
                "ltp": pi.get('lastPrice', 0),
                "open": pi.get('open', 0),
                "high": pi.get('intraDayHighLow', {}).get('max', 0),
                "low": pi.get('intraDayHighLow', {}).get('min', 0),
                "close": pi.get('close', 0),
                "prev_close": pi.get('previousClose', 0),
                "change": pi.get('change', 0),
                "pct_change": pi.get('pChange', 0),
                "volume": data.get('securityWiseDP', {}).get('quantityTraded', 0),
            }
    except Exception as e:
        st.error(f"nse_quote error: {e}")
    return {}


@st.cache_data(ttl=300)
def fetch_historical(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """Fetch historical data using yfinance."""
    try:
        import yfinance as yf
        df = yf.download(f"{ticker}.NS", period=period, progress=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df = df.reset_index()
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        st.error(f"yfinance error: {e}")
    return pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
# MASTER EXCEL GENERATOR (3 TABS)
# ══════════════════════════════════════════════════════════════════════════════
def create_master_excel() -> bytes:
    """Create 3-tab Master Excel: EQUITY_HIST, CALL_OPTIONS, PUT_OPTIONS."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Tab 1: EQUITY_HIST
        hist = st.session_state.get("equity_hist")
        if hist is not None and not hist.empty:
            hist.to_excel(writer, sheet_name='EQUITY_HIST', index=False)
        else:
            pd.DataFrame({"Info": ["No equity data"]}).to_excel(writer, sheet_name='EQUITY_HIST', index=False)
        
        # Tab 2: CALL_OPTIONS
        calls = st.session_state.get("call_options")
        if calls is not None and not calls.empty:
            calls.to_excel(writer, sheet_name='CALL_OPTIONS', index=False)
        else:
            pd.DataFrame({"Info": ["No call options - fetch from Derivatives Hub"]}).to_excel(writer, sheet_name='CALL_OPTIONS', index=False)
        
        # Tab 3: PUT_OPTIONS
        puts = st.session_state.get("put_options")
        if puts is not None and not puts.empty:
            puts.to_excel(writer, sheet_name='PUT_OPTIONS', index=False)
        else:
            pd.DataFrame({"Info": ["No put options - fetch from Derivatives Hub"]}).to_excel(writer, sheet_name='PUT_OPTIONS', index=False)
    
    return output.getvalue()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📈 Equity Data")
    st.caption("Live Quote + Historical")
    st.divider()
    
    st.markdown("### 📊 Stock Selection")
    default_idx = NSE_STOCKS.index(st.session_state["selected_ticker"]) if st.session_state["selected_ticker"] in NSE_STOCKS else 0
    ticker = st.selectbox("Select Stock", NSE_STOCKS, index=default_idx)
    st.session_state["selected_ticker"] = ticker
    st.divider()
    
    st.markdown("### 📅 Period")
    period = st.selectbox("Historical Period", ["1mo", "3mo", "6mo", "1y"], index=0)
    st.divider()
    
    st.markdown("### 💾 Persistence Vault")
    st.caption(f"Ticker: **{st.session_state.get('selected_ticker')}**")
    if st.session_state.get("equity_data"):
        st.success("✅ Equity data loaded")
    if st.session_state.get("options_data"):
        st.success("✅ Options available")
    st.divider()
    
    st.markdown("### 📡 Data Source")
    st.markdown('<span class="source-badge">nse_quote() + yfinance</span>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 📈 Equity Data")
st.caption(f"Symbol: {ticker} | Source: nsepython nse_quote() + yfinance")
st.markdown(f'<span class="source-badge">nse_quote("{ticker}")</span>', unsafe_allow_html=True)
st.divider()

# Fetch Button
if st.button("🚀 FETCH EQUITY DATA", use_container_width=True, type="primary"):
    with st.spinner(f"Fetching {ticker}..."):
        # Live Quote
        quote = fetch_live_quote(ticker)
        if quote:
            # Validate against Google
            ltp = quote.get('ltp', 0)
            is_valid, google_price, diff = validate_price(ltp, ticker)
            
            if not is_valid:
                st.warning(f"⚠️ Price mismatch! NSE: ₹{ltp:.2f} vs Google: ₹{google_price:.2f} ({diff*100:.1f}%)")
                st.cache_data.clear()
                quote = fetch_live_quote(ticker)
                st.info("🔄 Session restarted due to >2% mismatch")
            else:
                if google_price > 0:
                    st.markdown(f'<div class="validation-ok">✅ PRICE VALIDATED | Google: ₹{google_price:,.2f}</div>', unsafe_allow_html=True)
            
            st.session_state["equity_data"] = quote
            
            # Historical
            hist = fetch_historical(ticker, period)
            st.session_state["equity_hist"] = hist
            
            st.success(f"✅ Loaded {ticker} | LTP: ₹{quote.get('ltp', 0):,.2f} | {len(hist)} historical records")
        else:
            st.error("❌ Failed to fetch data")

st.divider()

# Display Data
if st.session_state.get("equity_data"):
    q = st.session_state["equity_data"]
    
    st.markdown("### 📊 Live Quote KPIs")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        delta_color = "normal" if q.get('change', 0) >= 0 else "inverse"
        st.metric("LTP", f"₹{q.get('ltp', 0):,.2f}", 
                  f"{q.get('change', 0):+.2f} ({q.get('pct_change', 0):+.2f}%)",
                  delta_color=delta_color)
    with k2:
        st.metric("VOLUME", f"{q.get('volume', 0):,}")
    with k3:
        st.metric("DAY HIGH", f"₹{q.get('high', 0):,.2f}")
    with k4:
        st.metric("DAY LOW", f"₹{q.get('low', 0):,.2f}")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("OPEN", f"₹{q.get('open', 0):,.2f}")
    with m2:
        st.metric("PREV CLOSE", f"₹{q.get('prev_close', 0):,.2f}")
    with m3:
        st.metric("CHANGE", f"₹{q.get('change', 0):+,.2f}")
    with m4:
        st.metric("% CHANGE", f"{q.get('pct_change', 0):+.2f}%")
    
    st.divider()
    
    # Historical Table
    if st.session_state.get("equity_hist") is not None and not st.session_state["equity_hist"].empty:
        st.markdown("### 📈 Price Chart")
        chart_df = st.session_state["equity_hist"].copy()
        chart_df['Date'] = pd.to_datetime(chart_df['Date'])
        st.line_chart(chart_df.set_index('Date')['Close'], use_container_width=True, height=350)
        
        st.markdown("### 📊 Volume Chart")
        st.bar_chart(chart_df.set_index('Date')['Volume'], use_container_width=True, height=200)
        
        st.divider()
        st.markdown("### 📋 Historical Data (Clean Rows & Columns)")
        st.dataframe(st.session_state["equity_hist"], use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Export Section
    st.markdown("### 📥 Master Download")
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.get("equity_hist") is not None:
            st.download_button(
                "📥 Download CSV",
                st.session_state["equity_hist"].to_csv(index=False),
                f"{ticker}_equity.csv",
                "text/csv",
                use_container_width=True
            )
    with col2:
        excel_data = create_master_excel()
        st.download_button(
            "📥 MASTER EXCEL (3 TABS)",
            excel_data,
            f"{ticker}_Master_Data.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
else:
    st.info("👆 Click **FETCH EQUITY DATA** to load live quote and historical data")

st.divider()
st.caption(f"📈 Quantum Market Suite | Equity Data | {datetime.now().strftime('%H:%M:%S')}")
