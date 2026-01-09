"""
PRK's Exchange Suite - Quantum Market Platform
═══════════════════════════════════════════════════════════════════════════════
MULTI-PAGE STRUCTURE:
- main.py (Home/Landing)
- pages/1_Equity.py (Equity Data)
- pages/2_Derivatives.py (Call/Put Options)

TRUE-DATA ENGINE:
- Excel Trick Session (nsit + bm_sv cookies)
- Internal API Protocol (api/quote-equity, api/historical/cm/equity, api/option-chain-indices)
- Google Cross-Check (>2% diff = auto-restart)

PERSISTENCE VAULT:
- st.session_state shares data across pages
═══════════════════════════════════════════════════════════════════════════════
"""
import streamlit as st
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PRK's Exchange Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
# BLOOMBERG-STYLE CSS
# ══════════════════════════════════════════════════════════════════════════════
BLOOMBERG_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: #1a1a24;
    --accent-blue: #00d4ff;
    --accent-green: #00ff88;
    --accent-red: #ff4757;
    --accent-orange: #ffa502;
    --text-primary: #ffffff;
    --text-secondary: #8b8b9a;
    --border-color: #2a2a3a;
}

.stApp {
    background: linear-gradient(180deg, var(--bg-primary) 0%, #0d0d14 100%);
    font-family: 'Inter', sans-serif;
}

/* Sidebar Branding */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d14 0%, #1a1a24 100%) !important;
    border-right: 1px solid var(--border-color) !important;
}

section[data-testid="stSidebar"] .stMarkdown h1 {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-green));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'JetBrains Mono', monospace;
}

/* Bloomberg Terminal Tables */
.stDataFrame {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}

.stDataFrame table {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
}

.stDataFrame th {
    background: linear-gradient(180deg, #1e1e2e 0%, #16161f 100%) !important;
    color: var(--accent-blue) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.5px !important;
    border-bottom: 2px solid var(--accent-blue) !important;
}

.stDataFrame td {
    color: var(--text-primary) !important;
    border-bottom: 1px solid var(--border-color) !important;
}

.stDataFrame tr:hover td {
    background: rgba(0, 212, 255, 0.05) !important;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, var(--bg-card) 0%, #1e1e2e 100%);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] svg {
    display: none;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-blue) 0%, #0099cc 100%) !important;
    color: #000 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3) !important;
}

/* Status Badges */
.status-live {
    background: linear-gradient(135deg, var(--accent-green), #00cc6a);
    color: #000;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: inline-block;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.api-badge {
    background: var(--bg-card);
    border: 1px solid var(--accent-blue);
    color: var(--accent-blue);
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    margin: 4px;
}

/* Hero Section */
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #fff 0%, var(--accent-blue) 50%, var(--accent-green) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Inter', sans-serif;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    color: var(--text-secondary);
    font-size: 1.1rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Cards */
.feature-card {
    background: linear-gradient(135deg, var(--bg-card) 0%, #1e1e2e 100%);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.feature-card:hover {
    border-color: var(--accent-blue);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 212, 255, 0.15);
}

/* Dividers */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    margin: 2rem 0;
}

/* Expanders */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
}

/* Progress */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-green)) !important;
}
</style>
"""

st.markdown(BLOOMBERG_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INITIALIZE PERSISTENCE VAULT
# ══════════════════════════════════════════════════════════════════════════════
if "stock_ticker" not in st.session_state:
    st.session_state["stock_ticker"] = "RELIANCE"
if "captured_equity" not in st.session_state:
    st.session_state["captured_equity"] = None
if "captured_options" not in st.session_state:
    st.session_state["captured_options"] = None
if "last_ltp" not in st.session_state:
    st.session_state["last_ltp"] = None
if "google_price" not in st.session_state:
    st.session_state["google_price"] = None
if "session_valid" not in st.session_state:
    st.session_state["session_valid"] = False

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR BRANDING
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# ⚡ PRK's Exchange Suite")
    st.markdown('<span class="status-live">● LIVE</span>', unsafe_allow_html=True)
    st.caption("Quantum Market Platform v2.0")
    
    st.divider()
    
    st.markdown("### 📡 True-Data Engine")
    st.markdown('<span class="api-badge">api/quote-equity</span>', unsafe_allow_html=True)
    st.markdown('<span class="api-badge">api/historical/cm/equity</span>', unsafe_allow_html=True)
    st.markdown('<span class="api-badge">api/option-chain-indices</span>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 🔒 Session Protocol")
    st.caption("Excel Trick: nsit + bm_sv cookies")
    st.caption("Google Cross-Check: >2% = Auto-Restart")
    
    if st.session_state.get("session_valid"):
        st.success("✅ Session Active")
    else:
        st.warning("⏳ Session Pending")
    
    st.divider()
    
    st.markdown("### 📊 Persistence Vault")
    st.caption(f"Active Ticker: **{st.session_state.get('stock_ticker', 'None')}**")
    
    if st.session_state.get("last_ltp"):
        st.metric("Last LTP", f"₹{st.session_state['last_ltp']:,.2f}")
    
    if st.session_state.get("google_price"):
        st.metric("Google Price", f"₹{st.session_state['google_price']:,.2f}")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT - LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="hero-title">⚡ PRK\'s Exchange Suite</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Quantum Market Platform • True-Data Engine • Bloomberg Terminal UI</p>', unsafe_allow_html=True)

st.divider()

# Feature Cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Equity Data</h3>
        <p style="color: #8b8b9a;">Real-time quotes from NSE Internal API with Google Finance cross-validation.</p>
        <p style="color: #00d4ff; font-family: 'JetBrains Mono';">api/quote-equity</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Option Chain</h3>
        <p style="color: #8b8b9a;">Live Call/Put data from NSE option chain with strike-wise analysis.</p>
        <p style="color: #00ff88; font-family: 'JetBrains Mono';">api/option-chain-indices</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🔒 True-Data Engine</h3>
        <p style="color: #8b8b9a;">Excel Trick session with cookie capture. No Ghost Data ever.</p>
        <p style="color: #ffa502; font-family: 'JetBrains Mono';">nsit + bm_sv</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Navigation Guide
st.markdown("### 🧭 Navigation")
st.info("""
**Use the sidebar to navigate:**
- **📈 Equity** → Fetch live equity quotes and historical data
- **📊 Derivatives** → Fetch Call/Put option chain data

Data persists across pages via the **Persistence Vault**.
""")

# Quick Stats
st.markdown("### 📊 Platform Status")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Engine", "True-Data", delta="Active")
with c2:
    st.metric("API Protocol", "Internal", delta="Secure")
with c3:
    st.metric("Validation", "Google", delta=">2% Check")
with c4:
    st.metric("Session", "Excel Trick", delta="8s Warmup")

st.divider()

# Tech Stack
st.markdown("### ⚙️ Tech Stack")

tech_col1, tech_col2 = st.columns(2)

with tech_col1:
    st.markdown("""
    **Data Sources:**
    - `api/quote-equity` - Live equity quotes
    - `api/historical/cm/equity` - Historical OHLCV
    - `api/option-chain-indices` - Option chain (NIFTY/BANKNIFTY)
    - `api/option-chain-equities` - Stock options
    """)

with tech_col2:
    st.markdown("""
    **Security Protocol:**
    - Excel Trick Session (requests.Session)
    - Cookie Capture: `nsit`, `bm_sv`
    - 8-second handshake warmup
    - Google Finance cross-validation
    - Auto-restart on >2% mismatch
    """)

# Footer
st.divider()
st.markdown("---")
st.caption("⚡ **PRK's Exchange Suite** | Quantum Market Platform v2.0")
st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | True-Data Engine | Bloomberg Terminal UI")
