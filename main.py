"""
PRK Exchange Suite - Professional Stock Analysis Platform
═══════════════════════════════════════════════════════════════════════════════
DATA SOURCES:
- Equity: yfinance (Yahoo Finance API)
- Options: nsepython (NSE Official API)

PAGES:
- 1_Equity.py: Historical data, KPI tiles, Line charts
- 2_Derivatives.py: Option chain, PCR indicator
═══════════════════════════════════════════════════════════════════════════════
"""
import streamlit as st
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PRK Exchange Suite",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    font-family: 'Inter', sans-serif;
}

/* Metric Cards */
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
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

section[data-testid="stSidebar"] .stMarkdown {
    color: #e2e8f0;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

/* DataFrames */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
}

/* Hero */
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    color: #64748b;
    font-size: 1.1rem;
}

/* Cards */
.info-card {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 1rem;
}

.info-card h3 {
    color: #f1f5f9;
    margin-bottom: 0.5rem;
}

.info-card p {
    color: #94a3b8;
    font-size: 0.9rem;
}

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-blue {
    background: rgba(59, 130, 246, 0.2);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

.badge-green {
    background: rgba(34, 197, 94, 0.2);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.3);
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INITIALIZE SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "TCS"
if "equity_data" not in st.session_state:
    st.session_state["equity_data"] = None
if "options_data" not in st.session_state:
    st.session_state["options_data"] = None

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📈 PRK Exchange Suite")
    st.caption("Professional Stock Analysis")
    
    st.divider()
    
    st.markdown("### 📊 Data Sources")
    st.markdown('<span class="badge badge-blue">yfinance</span> Equity Data', unsafe_allow_html=True)
    st.markdown('<span class="badge badge-green">nsepython</span> Option Chain', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 🧭 Navigation")
    st.markdown("""
    - **📈 Equity** → Historical data & charts
    - **📊 Derivatives** → Option chain & PCR
    """)
    
    st.divider()
    
    st.markdown("### 💾 Session State")
    st.caption(f"Ticker: **{st.session_state.get('selected_ticker', 'None')}**")
    
    if st.session_state.get("equity_data") is not None:
        st.success("✅ Equity data loaded")
    if st.session_state.get("options_data") is not None:
        st.success("✅ Options data loaded")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="hero-title">📈 PRK Exchange Suite</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Professional Stock Analysis Platform • yfinance + nsepython</p>', unsafe_allow_html=True)

st.divider()

# Feature Cards
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="info-card">
        <h3>📈 Equity Analysis</h3>
        <p>Fetch historical stock data using <strong>yfinance</strong>. View KPI tiles for Open, High, Low, Close and beautiful line charts.</p>
        <span class="badge badge-blue">yf.download("TCS.NS")</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3>📊 Option Chain</h3>
        <p>Live option chain data from <strong>nsepython</strong>. View Call/Put OI, LTP, and Put-Call Ratio (PCR) indicator.</p>
        <span class="badge badge-green">option_chain("NIFTY")</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Quick Start
st.markdown("### 🚀 Quick Start")
st.info("""
1. **Select a ticker** in the sidebar or on the Equity page
2. **Fetch Equity Data** → View historical prices and charts
3. **Switch to Derivatives** → View option chain with the same ticker
4. **Data persists** across pages via `st.session_state`
""")

# Stats
st.markdown("### 📊 Platform Stats")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Data Source", "yfinance", delta="Equity")
with c2:
    st.metric("Options API", "nsepython", delta="NSE")
with c3:
    st.metric("Pages", "2", delta="Equity + Derivatives")
with c4:
    st.metric("Persistence", "Active", delta="Session State")

# Footer
st.divider()
st.caption(f"📈 PRK Exchange Suite | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Data: yfinance (Yahoo Finance) • nsepython (NSE India)")
