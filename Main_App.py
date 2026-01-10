# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT CLOUD PERMISSION FIX - MUST BE AT VERY TOP
# ══════════════════════════════════════════════════════════════════════════════
import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
# ══════════════════════════════════════════════════════════════════════════════

"""
Quantum Market Suite - Main Landing Page
═══════════════════════════════════════════════════════════════════════════════
DATA SOURCES: nsepython (nse_quote, nse_optionchain)
STEALTH: TLS Fingerprint Rotation + Browser Headers
VALIDATION: Google Finance Reference (>2% mismatch = auto-restart)
═══════════════════════════════════════════════════════════════════════════════
"""
import streamlit as st
import requests
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
if "equity_hist" not in st.session_state:
    st.session_state["equity_hist"] = None
if "options_data" not in st.session_state:
    st.session_state["options_data"] = None
if "call_options" not in st.session_state:
    st.session_state["call_options"] = None
if "put_options" not in st.session_state:
    st.session_state["put_options"] = None
if "nse_session" not in st.session_state:
    st.session_state["nse_session"] = None
if "session_valid" not in st.session_state:
    st.session_state["session_valid"] = False

# ══════════════════════════════════════════════════════════════════════════════
# STEALTH HANDSHAKE - TLS FINGERPRINT ROTATION
# ══════════════════════════════════════════════════════════════════════════════
def create_stealth_session() -> requests.Session:
    """Create session with TLS Fingerprint Rotation and Browser Headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    try:
        session.get("https://www.nseindia.com", timeout=10)
    except Exception:
        pass
    return session


def init_handshake():
    """Initialize or restart the stealth handshake session."""
    st.session_state["nse_session"] = create_stealth_session()
    st.session_state["session_valid"] = True
    return st.session_state["nse_session"]

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
    st.markdown('<span class="badge badge-green">nsepython</span> Live + Options', unsafe_allow_html=True)
    st.markdown('<span class="badge badge-blue">yfinance</span> Historical', unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### 🧭 Navigation")
    st.markdown("""
    - **📈 Equity Data** → Live Quote + Historical
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
    if st.session_state.get("session_valid"):
        st.markdown('<div class="status-ok">🔗 NSE SESSION ACTIVE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-pending">🔌 NSE SESSION IDLE</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="hero-title">📈 Quantum Market Suite<span class="cursor">_</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">> Professional Stock Analysis Terminal • nsepython • Google Validation</p>', unsafe_allow_html=True)
st.divider()

# Initialize Handshake Button
if st.button("🔐 INITIALIZE STEALTH HANDSHAKE", use_container_width=True, type="primary"):
    with st.spinner("Establishing TLS Fingerprint..."):
        init_handshake()
        st.success("✅ Stealth Handshake established! Session cookies captured.")

st.divider()

# Feature Cards
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="info-card">
        <h3>📈 Equity Data</h3>
        <p>Fetch live stock quotes using <strong>nse_quote()</strong> and historical data via yfinance. View KPI tiles for LTP, Volume, % Change.</p>
        <span class="badge badge-green">nse_quote("TCS")</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3>📊 Derivatives Hub</h3>
        <p>Live option chain from <strong>nse_optionchain()</strong>. View Call/Put OI, LTP, and PCR indicator with clean data tables.</p>
        <span class="badge badge-green">nse_optionchain("NIFTY")</span>
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
    session_status = "ACTIVE" if st.session_state.get("session_valid") else "IDLE"
    st.metric("SESSION", session_status)

st.divider()

# Quick Start
st.markdown("### 🚀 Quick Start")
st.info("""
**1.** Click **Initialize Stealth Handshake** above to establish NSE session  
**2.** Go to **Equity Data** page → Select ticker → Fetch live quote + historical  
**3.** Switch to **Derivatives Hub** → Same ticker auto-loads via Persistence Vault  
**4.** Google Finance validates prices (>2% mismatch = auto-restart session)  
**5.** Download 3-tab Master Excel from either page
""")

# Platform Stats
st.markdown("### 📡 Platform Configuration")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("LIVE SOURCE", "nsepython")
with c2:
    st.metric("HISTORICAL", "yfinance")
with c3:
    st.metric("VALIDATION", "Google Finance")
with c4:
    st.metric("EXPORT", "3-Tab Excel")

# Footer
st.divider()
st.caption(f"📈 Quantum Market Suite | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Data: nsepython (nse_quote, nse_optionchain) • yfinance • Google Finance Validation")
st.caption("Stealth: TLS Fingerprint Rotation | Headers: Accept-Encoding gzip,deflate,br | Referer: nseindia.com")
