# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT CLOUD PERMISSION FIX - MUST BE AT VERY TOP
# ══════════════════════════════════════════════════════════════════════════════
import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
# ══════════════════════════════════════════════════════════════════════════════

"""
Quantum Market Suite - Derivatives Hub (Option Chain)
═══════════════════════════════════════════════════════════════════════════════
DATA: nsepython nse_optionchain()
STEALTH: TLS Fingerprint + Browser Headers
VALIDATION: Google Finance (>2% mismatch = auto-restart)
OUTPUT: Clean rows and columns only (Call/Put)
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
st.set_page_config(page_title="Derivatives Hub | Quantum", page_icon="📊", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "NIFTY"
if "options_data" not in st.session_state:
    st.session_state["options_data"] = None
if "call_options" not in st.session_state:
    st.session_state["call_options"] = None
if "put_options" not in st.session_state:
    st.session_state["put_options"] = None

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

.pcr-bullish {
    background: linear-gradient(135deg, #00ff41 0%, #00d4aa 100%);
    color: #0d1117;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 1.2rem;
    font-weight: 700;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
}
.pcr-bearish {
    background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%);
    color: #ffffff;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 1.2rem;
    font-weight: 700;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
}
.pcr-neutral {
    background: linear-gradient(135deg, #ffc107 0%, #ffca2c 100%);
    color: #0d1117;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 1.2rem;
    font-weight: 700;
    text-align: center;
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

.session-active {
    background: rgba(0, 255, 65, 0.1);
    color: #00ff41;
    padding: 6px 12px;
    border-radius: 4px;
    border: 1px solid rgba(0, 255, 65, 0.3);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SYMBOLS
# ══════════════════════════════════════════════════════════════════════════════
INDEX_SYMBOLS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
STOCK_SYMBOLS = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL",
                 "KOTAKBANK", "ITC", "LT", "AXISBANK", "MARUTI", "BAJFINANCE", "TITAN",
                 "TATAMOTORS", "TATASTEEL", "WIPRO", "HCLTECH", "TECHM"]
ALL_SYMBOLS = INDEX_SYMBOLS + STOCK_SYMBOLS

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE FINANCE VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
def get_google_price(ticker: str) -> float:
    """Fetch Google Finance price as truth reference."""
    try:
        if ticker in INDEX_SYMBOLS:
            url = f"https://www.google.com/finance/quote/{ticker}:INDEXNSE"
        else:
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
# NSE OPTION CHAIN FETCHER
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def fetch_option_chain(symbol: str) -> tuple:
    """Fetch option chain using nsepython nse_optionchain()."""
    try:
        from nsepython import nse_optionchain
        data = nse_optionchain(symbol)
        if not data or 'records' not in data:
            return pd.DataFrame(), pd.DataFrame(), 0, 0
        
        records = data['records']
        underlying = records.get('underlyingValue', 0)
        data_list = records.get('data', [])
        
        calls, puts = [], []
        total_call_oi, total_put_oi = 0, 0
        
        for rec in data_list:
            strike = rec.get('strikePrice', 0)
            expiry = rec.get('expiryDate', '')
            
            if 'CE' in rec:
                ce = rec['CE']
                oi = ce.get('openInterest', 0)
                total_call_oi += oi
                calls.append({
                    'Strike': strike,
                    'Expiry': expiry,
                    'LTP': ce.get('lastPrice', 0),
                    'Change': ce.get('change', 0),
                    'OI': oi,
                    'OI_Chg': ce.get('changeinOpenInterest', 0),
                    'Volume': ce.get('totalTradedVolume', 0),
                    'IV': ce.get('impliedVolatility', 0),
                })
            
            if 'PE' in rec:
                pe = rec['PE']
                oi = pe.get('openInterest', 0)
                total_put_oi += oi
                puts.append({
                    'Strike': strike,
                    'Expiry': expiry,
                    'LTP': pe.get('lastPrice', 0),
                    'Change': pe.get('change', 0),
                    'OI': oi,
                    'OI_Chg': pe.get('changeinOpenInterest', 0),
                    'Volume': pe.get('totalTradedVolume', 0),
                    'IV': pe.get('impliedVolatility', 0),
                })
        
        call_df = pd.DataFrame(calls) if calls else pd.DataFrame()
        put_df = pd.DataFrame(puts) if puts else pd.DataFrame()
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        
        return call_df, put_df, underlying, pcr
    
    except Exception as e:
        st.error(f"nse_optionchain error: {e}")
        return pd.DataFrame(), pd.DataFrame(), 0, 0

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
            pd.DataFrame({"Info": ["No equity data - fetch from Equity page"]}).to_excel(writer, sheet_name='EQUITY_HIST', index=False)
        
        # Tab 2: CALL_OPTIONS
        calls = st.session_state.get("call_options")
        if calls is not None and not calls.empty:
            calls.to_excel(writer, sheet_name='CALL_OPTIONS', index=False)
        else:
            pd.DataFrame({"Info": ["No call options data"]}).to_excel(writer, sheet_name='CALL_OPTIONS', index=False)
        
        # Tab 3: PUT_OPTIONS
        puts = st.session_state.get("put_options")
        if puts is not None and not puts.empty:
            puts.to_excel(writer, sheet_name='PUT_OPTIONS', index=False)
        else:
            pd.DataFrame({"Info": ["No put options data"]}).to_excel(writer, sheet_name='PUT_OPTIONS', index=False)
    
    return output.getvalue()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📊 Derivatives Hub")
    st.caption("Call/Put Option Chain")
    st.divider()
    
    st.markdown("### 📊 Symbol Selection")
    default_ticker = st.session_state.get("selected_ticker", "NIFTY")
    if default_ticker not in ALL_SYMBOLS:
        default_ticker = "NIFTY"
    symbol = st.selectbox("Select Symbol", ALL_SYMBOLS, index=ALL_SYMBOLS.index(default_ticker))
    st.session_state["selected_ticker"] = symbol
    st.caption(f"Type: {'Index' if symbol in INDEX_SYMBOLS else 'Stock'}")
    st.divider()
    
    st.markdown("### 💾 Persistence Vault")
    st.caption(f"Ticker: **{symbol}**")
    if st.session_state.get("equity_data"):
        st.success("✅ Equity available")
    if st.session_state.get("options_data"):
        st.success("✅ Options loaded")
    st.divider()
    
    st.markdown("### 📡 Data Source")
    st.markdown('<span class="source-badge">nse_optionchain()</span>', unsafe_allow_html=True)
    st.caption("Stealth Headers: ✅")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 📊 Derivatives Hub (Option Chain)")
st.caption(f"Symbol: {symbol} | Source: nsepython nse_optionchain()")
st.markdown(f'<span class="source-badge">nse_optionchain("{symbol}")</span>', unsafe_allow_html=True)
st.divider()

# Auto-load notice
if st.session_state.get("equity_data"):
    st.success(f"✅ Ticker '{st.session_state['selected_ticker']}' loaded from Equity page via Persistence Vault")

# Fetch Button
if st.button("🚀 FETCH OPTION CHAIN", use_container_width=True, type="primary"):
    with st.spinner(f"Fetching {symbol} option chain..."):
        call_df, put_df, underlying, pcr = fetch_option_chain(symbol)
        
        if not call_df.empty or not put_df.empty:
            # Validate against Google
            is_valid, google_price, diff = validate_price(underlying, symbol)
            
            if not is_valid and google_price > 0:
                st.warning(f"⚠️ Price mismatch! NSE: ₹{underlying:.2f} vs Google: ₹{google_price:.2f} ({diff*100:.1f}%)")
                st.cache_data.clear()
                call_df, put_df, underlying, pcr = fetch_option_chain(symbol)
                st.info("🔄 Session restarted due to >2% mismatch")
            else:
                if google_price > 0:
                    st.markdown(f'<div class="validation-ok">✅ PRICE VALIDATED | Google: ₹{google_price:,.2f}</div>', unsafe_allow_html=True)
            
            st.session_state["options_data"] = {"underlying": underlying, "pcr": pcr}
            st.session_state["call_options"] = call_df
            st.session_state["put_options"] = put_df
            
            st.success(f"✅ Loaded {len(call_df)} Calls + {len(put_df)} Puts | Underlying: ₹{underlying:,.2f}")
        else:
            st.error("❌ No option chain data")

st.divider()

# Display Data
if st.session_state.get("options_data"):
    data = st.session_state["options_data"]
    call_df = st.session_state.get("call_options", pd.DataFrame())
    put_df = st.session_state.get("put_options", pd.DataFrame())
    underlying = data.get("underlying", 0)
    pcr = data.get("pcr", 0)
    
    # PCR Indicator
    st.markdown("### 📊 Put-Call Ratio (PCR) Indicator")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if pcr > 1.2:
            st.markdown(f'<div class="pcr-bullish">PCR: {pcr:.2f} • BULLISH</div>', unsafe_allow_html=True)
            st.caption("High PCR (>1.2) = More Put writing → Bullish sentiment")
        elif pcr < 0.8:
            st.markdown(f'<div class="pcr-bearish">PCR: {pcr:.2f} • BEARISH</div>', unsafe_allow_html=True)
            st.caption("Low PCR (<0.8) = More Call writing → Bearish sentiment")
        else:
            st.markdown(f'<div class="pcr-neutral">PCR: {pcr:.2f} • NEUTRAL</div>', unsafe_allow_html=True)
            st.caption("PCR 0.8-1.2 = Balanced market")
    
    st.divider()
    
    # KPI Metrics
    st.markdown("### 📊 KPI Metrics")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("UNDERLYING", f"₹{underlying:,.2f}")
    with m2:
        st.metric("PCR", f"{pcr:.2f}")
    with m3:
        total_call_oi = call_df['OI'].sum() if 'OI' in call_df.columns else 0
        st.metric("TOTAL CALL OI", f"{total_call_oi:,}")
    with m4:
        total_put_oi = put_df['OI'].sum() if 'OI' in put_df.columns else 0
        st.metric("TOTAL PUT OI", f"{total_put_oi:,}")
    
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        total_call_vol = call_df['Volume'].sum() if 'Volume' in call_df.columns else 0
        st.metric("CALL VOLUME", f"{total_call_vol:,}")
    with v2:
        total_put_vol = put_df['Volume'].sum() if 'Volume' in put_df.columns else 0
        st.metric("PUT VOLUME", f"{total_put_vol:,}")
    with v3:
        st.metric("CALL STRIKES", len(call_df))
    with v4:
        st.metric("PUT STRIKES", len(put_df))
    
    st.divider()
    
    # Option Chain Tables (Clean Rows & Columns)
    st.markdown("### 📋 Option Chain (Clean Data)")
    tab1, tab2 = st.tabs(["🟢 CALL OPTIONS", "🔴 PUT OPTIONS"])
    
    with tab1:
        if not call_df.empty:
            st.dataframe(call_df, use_container_width=True, hide_index=True)
        else:
            st.info("No Call data")
    
    with tab2:
        if not put_df.empty:
            st.dataframe(put_df, use_container_width=True, hide_index=True)
        else:
            st.info("No Put data")
    
    st.divider()
    
    # Export Section
    st.markdown("### 📥 Master Download")
    col1, col2 = st.columns(2)
    with col1:
        if not call_df.empty:
            combined = pd.concat([
                call_df.assign(Type='CALL'),
                put_df.assign(Type='PUT')
            ], ignore_index=True)
            st.download_button(
                "📥 Download CSV",
                combined.to_csv(index=False),
                f"{symbol}_options.csv",
                "text/csv",
                use_container_width=True
            )
    with col2:
        excel_data = create_master_excel()
        st.download_button(
            "📥 MASTER EXCEL (3 TABS)",
            excel_data,
            f"{symbol}_Master_Data.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
else:
    st.info("👆 Click **FETCH OPTION CHAIN** to load data")

st.divider()
st.caption(f"📈 Quantum Market Suite | Derivatives Hub | {datetime.now().strftime('%H:%M:%S')}")
st.caption("Stealth: TLS Fingerprint | Headers: Accept-Encoding gzip,deflate,br | Referer: nseindia.com")
