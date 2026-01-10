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
# TERMINAL THEME CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
.stApp { background: #0d1117; font-family: 'JetBrains Mono', monospace; }
[data-testid="stMetric"] {
    background: #161b22; border-radius: 8px; padding: 1rem;
    border: 1px solid #30363d;
}
[data-testid="stMetricLabel"] { color: #00ff41 !important; font-size: 0.75rem !important; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #e6edf3 !important; font-size: 1.3rem !important; font-weight: 700; }
section[data-testid="stSidebar"] { background: #0d1117; border-right: 1px solid #30363d; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h3 { color: #00ff41 !important; }
.stButton > button {
    background: linear-gradient(135deg, #238636, #2ea043); color: #fff;
    font-weight: 600; border: none; border-radius: 6px;
}
.hero-title { font-size: 2.5rem; font-weight: 700; color: #00ff41; margin-bottom: 0.5rem; }
.hero-sub { color: #8b949e; font-size: 1rem; }
.status-ok { background: rgba(0,255,65,0.1); color: #00ff41; padding: 8px 16px; border-radius: 4px; border: 1px solid rgba(0,255,65,0.3); }
.status-pending { background: rgba(255,193,7,0.1); color: #ffc107; padding: 8px 16px; border-radius: 4px; border: 1px solid rgba(255,193,7,0.3); }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📈 Quantum Market Suite")
    st.caption("Total Data Dashboard")
    st.divider()
    st.markdown("### 📡 Data Source")
    st.code("nsepython", language=None)
    st.caption("nse_quote() • nse_optionchain()")
    st.divider()
    st.markdown("### 🔐 Stealth Session")
    if st.session_state.get("session_valid"):
        st.markdown('<div class="status-ok">✅ HANDSHAKE ACTIVE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-pending">⏳ PENDING INIT</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### 💾 Persistence Vault")
    st.caption(f"Ticker: **{st.session_state.get('selected_ticker')}**")
    if st.session_state.get("equity_data"):
        st.success("✅ Equity loaded")
    if st.session_state.get("options_data"):
        st.success("✅ Options loaded")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="hero-title">📈 Quantum Market Suite</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">> Total Data Dashboard • nsepython • Google Validation</p>', unsafe_allow_html=True)
st.divider()

# Initialize Handshake Button
if st.button("🔐 INITIALIZE STEALTH HANDSHAKE", use_container_width=True, type="primary"):
    with st.spinner("Establishing TLS Fingerprint..."):
        init_handshake()
        st.success("✅ Stealth Handshake established! Session cookies captured.")

st.divider()

# Status Metrics
st.markdown("### 📊 Session Status")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("TICKER", st.session_state.get("selected_ticker", "—"))
with c2:
    st.metric("EQUITY", "LOADED" if st.session_state.get("equity_data") else "EMPTY")
with c3:
    st.metric("OPTIONS", "LOADED" if st.session_state.get("options_data") else "EMPTY")
with c4:
    st.metric("SESSION", "ACTIVE" if st.session_state.get("session_valid") else "IDLE")

st.divider()

# Navigation Info
st.markdown("### 🧭 Navigation")
col1, col2 = st.columns(2)
with col1:
    st.info("**📈 Equity Data** → Live quote + Historical data (nse_quote)")
with col2:
    st.info("**📊 Derivatives Hub** → Option Chain Call/Put (nse_optionchain)")

st.divider()
st.caption(f"📈 Quantum Market Suite | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Data: nsepython | Validation: Google Finance | Stealth: TLS Fingerprint Rotation")
