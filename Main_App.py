# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT CLOUD TMP CACHE FIX - MUST BE AT VERY TOP
# ══════════════════════════════════════════════════════════════════════════════
import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
# ══════════════════════════════════════════════════════════════════════════════

"""
Quantum Market Suite - Main Application (Home/Landing)
═══════════════════════════════════════════════════════════════════════════════
DEPLOYMENT: Streamlit Cloud Ready
- Main_App.py at root (Home/Landing)
- pages/1_Equity_Analysis.py (Historical & Live Equity)
- pages/2_Derivatives_Hub.py (Call/Put Option Chain)

DATA SOURCES:
- Equity: yfinance (Yahoo Finance API)
- Options: nsepython (NSE Official API) with Stealth Handshake

VALIDATION:
- Google Finance Safety Check (>2% mismatch triggers auto-restart)
═══════════════════════════════════════════════════════════════════════════════
"""
import streamlit as st
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Quantum Market Suite",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION (PERSISTENCE VAULT)
# ══════════════════════════════════════════════════════════════════════════════
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "TCS"
if "equity_data" not in st.session_state:
    st.session_state["equity_data"] = None
if "options_data" not in st.session_state:
    st.session_state["options_data"] = None
if "last_fetch_time" not in st.session_state:
    st.session_state["last_fetch_time"] = None
if "underlying_price" not in st.session_state:
    st.session_state["underlying_price"] = None
if "pcr_value" not in st.session_state:
    st.session_state["pcr_value"] = None
if "nse_session" not in st.session_state:
    st.session_state["nse_session"] = None
if "price_validated" not in st.session_state:
    st.session_state["price_validated"] = False

# ══════════════════════════════════════════════════════════════════════════════
# TERMINAL THEME CSS (Dark Mode with Green/Red Highlights)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

/* Terminal Dark Theme */
.stApp {
    background: linear-gradient(135deg, #0a0f0d 0%, #0d1117 50%, #0a0f0d 100%);
    font-family: 'Inter', sans-serif;
}

/* Metric Cards - Terminal Style */
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
    letter-spacing: 1px;
}
[data-testid="stMetricValue"] {
    color: #e6edf3 !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stMetricDelta"] > div {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Positive/Negative Colors */
[data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"] {
    color: #00ff41 !important;
}
[data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"] {
    color: #ff4757 !important;
}

/* Sidebar - Terminal Style */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    border-right: 1px solid #30363d;
}
section[data-testid="stSidebar"] .stMarkdown {
    color: #c9d1d9;
}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: #00ff41 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Buttons - Terminal Style */
.stButton > button {
    background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
    color: #ffffff;
    font-weight: 600;
    border: 1px solid #238636;
    border-radius: 6px;
    padding: 0.75rem 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
    box-shadow: 0 0 20px rgba(46, 160, 67, 0.4);
    transform: translateY(-2px);
}

/* Hero Title */
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00ff41, #00d4aa, #00ff41);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    text-shadow: 0 0 30px rgba(0, 255, 65, 0.3);
}
.hero-subtitle {
    color: #8b949e;
    font-size: 1rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Info Cards - Terminal Style */
.info-card {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border-radius: 8px;
    padding: 1.5rem;
    border: 1px solid #30363d;
    margin-bottom: 1rem;
    box-shadow: 0 0 15px rgba(0, 255, 65, 0.05);
}
.info-card h3 {
    color: #00ff41;
    margin-bottom: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
}
.info-card p {
    color: #8b949e;
    font-size: 0.9rem;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-green {
    background: rgba(0, 255, 65, 0.15);
    color: #00ff41;
    border: 1px solid rgba(0, 255, 65, 0.3);
}
.badge-blue {
    background: rgba(88, 166, 255, 0.15);
    color: #58a6ff;
    border: 1px solid rgba(88, 166, 255, 0.3);
}
.badge-red {
    background: rgba(255, 71, 87, 0.15);
    color: #ff4757;
    border: 1px solid rgba(255, 71, 87, 0.3);
}

/* Status Indicators */
.status-ok {
    background: rgba(0, 255, 65, 0.1);
    color: #00ff41;
    padding: 8px 16px;
    border-radius: 4px;
    border: 1px solid rgba(0, 255, 65, 0.3);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
}
.status-pending {
    background: rgba(255, 193, 7, 0.1);
    color: #ffc107;
    padding: 8px 16px;
    border-radius: 4px;
    border: 1px solid rgba(255, 193, 7, 0.3);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
}

/* Terminal Cursor Blink */
@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}
.cursor {
    animation: blink 1s infinite;
    color: #00ff41;
}

/* DataFrames */
.stDataFrame {
    border: 1px solid #30363d !important;
}

/* Dividers */
hr {
    border-color: #30363d !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📈 Quantum Market Suite")
    st.caption("Professional Stock Analysis Terminal")
    st.divider()
    
    st.markdown("### 📡 Data Sources")
    st.markdown('<span class="badge badge-blue">yfinance</span> Equity Data', unsafe_allow_html=True)
    st.markdown('<span class="badge badge-green">nsepython</span> Option Chain', unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### 🧭 Navigation")
    st.markdown("""
    - **📈 Equity Analysis** → Historical & Live Data
    - **📊 Derivatives Hub** → Call/Put Option Chain
    """)
    st.divider()
    
    st.markdown("### 💾 Persistence Vault")
    st.caption(f"Active Ticker: **{st.session_state.get('selected_ticker', 'None')}**")
    
    if st.session_state.get("equity_data") is not None:
        st.markdown('<div class="status-ok">✅ EQUITY DATA LOADED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-pending">⏳ EQUITY PENDING</div>', unsafe_allow_html=True)
    
    st.write("")
    
    if st.session_state.get("options_data") is not None:
        st.markdown('<div class="status-ok">✅ OPTIONS DATA LOADED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-pending">⏳ OPTIONS PENDING</div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🔐 Session Status")
    if st.session_state.get("nse_session"):
        st.markdown('<div class="status-ok">🔗 NSE SESSION ACTIVE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-pending">🔌 NSE SESSION IDLE</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="hero-title">📈 Quantum Market Suite<span class="cursor">_</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">> Professional Stock Analysis Terminal • yfinance + nsepython</p>', unsafe_allow_html=True)
st.divider()

# Feature Cards
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="info-card">
        <h3>📈 Equity Analysis</h3>
        <p>Fetch historical stock data using <strong>yfinance</strong>. View KPI tiles for LTP, Volume, % Change with beautiful charts.</p>
        <span class="badge badge-blue">yf.download("TCS.NS")</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3>📊 Derivatives Hub</h3>
        <p>Live option chain from <strong>nsepython</strong> with Stealth Handshake. View Call/Put OI, LTP, and PCR indicator.</p>
        <span class="badge badge-green">option_chain("NIFTY")</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# KPI Metrics Row
st.markdown("### 📊 Session State Status")
s1, s2, s3, s4 = st.columns(4)
with s1:
    ticker = st.session_state.get("selected_ticker", "None")
    st.metric("ACTIVE TICKER", ticker)
with s2:
    equity_status = "LOADED" if st.session_state.get("equity_data") is not None else "EMPTY"
    st.metric("EQUITY DATA", equity_status)
with s3:
    options_status = "LOADED" if st.session_state.get("options_data") is not None else "EMPTY"
    st.metric("OPTIONS DATA", options_status)
with s4:
    validated = "YES" if st.session_state.get("price_validated") else "PENDING"
    st.metric("VALIDATED", validated)

st.divider()

# Quick Start
st.markdown("### 🚀 Quick Start")
st.info("""
**1.** Select a ticker on the **Equity Analysis** page → Fetch historical data  
**2.** Switch to **Derivatives Hub** → Same ticker auto-loads via Persistence Vault  
**3.** Google Finance Safety Check validates prices (>2% mismatch = auto-restart session)  
**4.** Download 3-tab Master Excel from either page
""")

# Platform Stats
st.markdown("### 📡 Platform Configuration")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("EQUITY SOURCE", "yfinance")
with c2:
    st.metric("OPTIONS SOURCE", "nsepython")
with c3:
    st.metric("VALIDATION", "Google Finance")
with c4:
    st.metric("EXPORT", "3-Tab Excel")

# Footer
st.divider()
st.caption(f"📈 Quantum Market Suite | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Data: yfinance (Yahoo Finance) • nsepython (NSE India) • Google Finance Safety Check")
st.caption("Deployment: Streamlit Cloud with /tmp cache fix | Stealth Handshake enabled")
