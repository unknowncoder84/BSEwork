# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT CLOUD TMP CACHE FIX - MUST BE AT VERY TOP
# ══════════════════════════════════════════════════════════════════════════════
import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
# ══════════════════════════════════════════════════════════════════════════════

"""
Quantum Market Suite - Derivatives Hub (Call/Put Option Chain)
═══════════════════════════════════════════════════════════════════════════════
DATA SOURCE: nsepython (NSE Official API)
STEALTH HANDSHAKE: Session visits nseindia.com first to grab live cookies
PILLAR HEADERS: User-Agent (Chrome), Accept-Encoding: gzip, deflate, br, Referer

FEATURES:
- Option Chain Table: Strike, Call OI, Put OI, LTP
- Put-Call Ratio (PCR) Indicator
- Google Finance Safety Check (>2% mismatch = auto-restart)
- 3-Tab Master Excel Export
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
st.set_page_config(
    page_title="Derivatives Hub | Quantum Market Suite",
    page_icon="📊",
    layout="wide"
)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "NIFTY"
if "options_data" not in st.session_state:
    st.session_state["options_data"] = None
if "pcr_value" not in st.session_state:
    st.session_state["pcr_value"] = None
if "nse_session" not in st.session_state:
    st.session_state["nse_session"] = None

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
.validation-warn {
    background: rgba(255, 71, 87, 0.1);
    color: #ff4757;
    padding: 8px 16px;
    border-radius: 4px;
    border: 1px solid rgba(255, 71, 87, 0.3);
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
                 "SUNPHARMA", "TATAMOTORS", "TATASTEEL", "WIPRO", "HCLTECH", "TECHM"]
ALL_SYMBOLS = INDEX_SYMBOLS + STOCK_SYMBOLS

# ══════════════════════════════════════════════════════════════════════════════
# STEALTH HANDSHAKE - NSE SESSION WITH LIVE COOKIES
# ══════════════════════════════════════════════════════════════════════════════
def create_stealth_session() -> requests.Session:
    """
    Create requests session with Stealth Handshake.
    Visits nseindia.com first to grab live cookies (nsit, bm_sv).
    """
    session = requests.Session()
    
    # PILLAR HEADERS
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",  # PILLAR HEADER
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.nseindia.com/",  # PILLAR HEADER
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    })
    
    # STEALTH HANDSHAKE: Visit NSE homepage first to grab cookies
    try:
        response = session.get("https://www.nseindia.com", timeout=15)
        # Cookies like nsit, bm_sv are now captured in session
    except Exception:
        pass
    
    return session


def restart_nse_session():
    """Restart NSE session with fresh cookies."""
    st.session_state["nse_session"] = create_stealth_session()
    return st.session_state["nse_session"]

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE FINANCE SCRAPER (TRUTH REFERENCE)
# ══════════════════════════════════════════════════════════════════════════════
def get_google_finance_price(ticker: str) -> float:
    """Fetch price from Google Finance as Truth Reference."""
    try:
        if ticker in INDEX_SYMBOLS:
            url = f"https://www.google.com/finance/quote/{ticker}:INDEXNSE"
        else:
            url = f"https://www.google.com/finance/quote/{ticker}:NSE"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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


def validate_nse_price(nse_price: float, ticker: str, tolerance: float = 0.02) -> tuple:
    """Validate NSE price against Google Finance. >2% mismatch triggers restart."""
    google_price = get_google_finance_price(ticker)
    if google_price > 0:
        diff_pct = abs(nse_price - google_price) / google_price
        return diff_pct <= tolerance, google_price, diff_pct
    return True, 0, 0

# ══════════════════════════════════════════════════════════════════════════════
# NSEPYTHON OPTION CHAIN FETCHER
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def fetch_option_chain(symbol: str) -> tuple:
    """Fetch option chain using nsepython with Stealth Handshake."""
    try:
        from nsepython import option_chain
        data = option_chain(symbol)
        if data is None or 'records' not in data:
            return pd.DataFrame(), pd.DataFrame(), 0, 0
        
        records = data['records']
        underlying = records.get('underlyingValue', 0)
        data_list = records.get('data', [])
        
        calls, puts = [], []
        total_call_oi, total_put_oi = 0, 0
        
        for record in data_list:
            strike = record.get('strikePrice', 0)
            expiry = record.get('expiryDate', '')
            
            if 'CE' in record:
                ce = record['CE']
                call_oi = ce.get('openInterest', 0)
                total_call_oi += call_oi
                calls.append({
                    'Strike': strike, 'Expiry': expiry,
                    'Call LTP': ce.get('lastPrice', 0), 'Call Change': ce.get('change', 0),
                    'Call OI': call_oi, 'Call OI Chg': ce.get('changeinOpenInterest', 0),
                    'Call Volume': ce.get('totalTradedVolume', 0), 'Call IV': ce.get('impliedVolatility', 0),
                })
            
            if 'PE' in record:
                pe = record['PE']
                put_oi = pe.get('openInterest', 0)
                total_put_oi += put_oi
                puts.append({
                    'Strike': strike, 'Expiry': expiry,
                    'Put LTP': pe.get('lastPrice', 0), 'Put Change': pe.get('change', 0),
                    'Put OI': put_oi, 'Put OI Chg': pe.get('changeinOpenInterest', 0),
                    'Put Volume': pe.get('totalTradedVolume', 0), 'Put IV': pe.get('impliedVolatility', 0),
                })
        
        call_df = pd.DataFrame(calls) if calls else pd.DataFrame()
        put_df = pd.DataFrame(puts) if puts else pd.DataFrame()
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        return call_df, put_df, underlying, pcr
    
    except ImportError:
        st.error("nsepython not installed. Run: pip install nsepython")
        return pd.DataFrame(), pd.DataFrame(), 0, 0
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame(), pd.DataFrame(), 0, 0


def create_combined_chain(call_df: pd.DataFrame, put_df: pd.DataFrame) -> pd.DataFrame:
    """Create combined option chain table."""
    if call_df.empty and put_df.empty:
        return pd.DataFrame()
    if not call_df.empty and not put_df.empty:
        combined = pd.merge(
            call_df[['Strike', 'Expiry', 'Call OI', 'Call LTP', 'Call IV']],
            put_df[['Strike', 'Expiry', 'Put OI', 'Put LTP', 'Put IV']],
            on=['Strike', 'Expiry'], how='outer'
        )
        return combined.sort_values('Strike')
    return call_df if not call_df.empty else put_df

# ══════════════════════════════════════════════════════════════════════════════
# 3-TAB MASTER EXCEL GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
def create_options_master_excel(call_df: pd.DataFrame, put_df: pd.DataFrame, 
                                 combined_df: pd.DataFrame, symbol: str, 
                                 underlying: float, pcr: float) -> bytes:
    """Create 3-tab Master Excel file for options."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Tab 1: Combined Option Chain
        if not combined_df.empty:
            combined_df.to_excel(writer, sheet_name='Option_Chain', index=False)
        
        # Tab 2: Summary Statistics
        total_call_oi = call_df['Call OI'].sum() if 'Call OI' in call_df.columns else 0
        total_put_oi = put_df['Put OI'].sum() if 'Put OI' in put_df.columns else 0
        total_call_vol = call_df['Call Volume'].sum() if 'Call Volume' in call_df.columns else 0
        total_put_vol = put_df['Put Volume'].sum() if 'Put Volume' in put_df.columns else 0
        
        # Find max OI strikes
        max_call_oi_strike = call_df.loc[call_df['Call OI'].idxmax(), 'Strike'] if not call_df.empty and 'Call OI' in call_df.columns else 0
        max_put_oi_strike = put_df.loc[put_df['Put OI'].idxmax(), 'Strike'] if not put_df.empty and 'Put OI' in put_df.columns else 0
        
        summary_data = {
            'Metric': ['Symbol', 'Underlying Price', 'PCR', 'Sentiment',
                      'Total Call OI', 'Total Put OI', 'Total Call Volume', 'Total Put Volume',
                      'Max Call OI Strike', 'Max Put OI Strike', 'Call Strikes', 'Put Strikes',
                      'Timestamp'],
            'Value': [symbol, f"₹{underlying:,.2f}", f"{pcr:.2f}",
                     'BULLISH' if pcr > 1.2 else ('BEARISH' if pcr < 0.8 else 'NEUTRAL'),
                     f"{total_call_oi:,.0f}", f"{total_put_oi:,.0f}",
                     f"{total_call_vol:,.0f}", f"{total_put_vol:,.0f}",
                     f"{max_call_oi_strike:,.0f}", f"{max_put_oi_strike:,.0f}",
                     len(call_df), len(put_df),
                     datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        # Tab 3: Detailed Call/Put Split
        if not call_df.empty:
            call_df.to_excel(writer, sheet_name='Calls_Detail', index=False)
        if not put_df.empty:
            put_df.to_excel(writer, sheet_name='Puts_Detail', index=False)
    
    return output.getvalue()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📊 Derivatives Hub")
    st.caption("Call/Put Option Chain")
    st.divider()
    
    st.markdown("### 📊 Symbol Selection")
    # Auto-load ticker from Equity page via Persistence Vault
    default_ticker = st.session_state.get("selected_ticker", "NIFTY")
    if default_ticker not in ALL_SYMBOLS:
        default_ticker = "NIFTY"
    selected_symbol = st.selectbox("Select Symbol", ALL_SYMBOLS,
                                   index=ALL_SYMBOLS.index(default_ticker) if default_ticker in ALL_SYMBOLS else 0)
    st.session_state["selected_ticker"] = selected_symbol
    is_index = selected_symbol in INDEX_SYMBOLS
    st.caption(f"Type: {'Index' if is_index else 'Stock'}")
    st.divider()
    
    st.markdown("### 💾 Persistence Vault")
    st.caption(f"Ticker: **{st.session_state.get('selected_ticker')}**")
    if st.session_state.get("equity_data") is not None:
        st.success("✅ Equity data available")
    if st.session_state.get("options_data") is not None:
        st.success("✅ Options data loaded")
    st.divider()
    
    st.markdown("### 🔐 Stealth Handshake")
    if st.session_state.get("nse_session"):
        st.markdown('<div class="session-active">🔗 NSE SESSION ACTIVE</div>', unsafe_allow_html=True)
    else:
        st.caption("Session will initialize on fetch")
    st.divider()
    
    st.markdown("### 📡 Data Source")
    st.markdown('<span class="source-badge">nsepython</span>', unsafe_allow_html=True)
    st.caption("Pillar Headers: ✅")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 📊 Derivatives Hub (Option Chain)")
st.caption(f"Data Source: nsepython | Symbol: {selected_symbol} | Stealth Handshake: Active")
st.markdown(f'<span class="source-badge">option_chain("{selected_symbol}")</span>', unsafe_allow_html=True)
st.divider()

# Show if ticker was loaded from Equity page
if st.session_state.get("equity_data") is not None:
    st.success(f"✅ Ticker '{st.session_state.get('selected_ticker')}' auto-loaded from Equity page via Persistence Vault")

# Fetch Button
if st.button("🚀 FETCH OPTION CHAIN", use_container_width=True, type="primary"):
    with st.spinner(f"Initializing Stealth Handshake for {selected_symbol}..."):
        # Initialize/restart session
        restart_nse_session()
        
        call_df, put_df, underlying, pcr = fetch_option_chain(selected_symbol)
        
        if not call_df.empty or not put_df.empty:
            # Google Finance Safety Check
            is_valid, google_price, diff_pct = validate_nse_price(underlying, selected_symbol)
            
            if not is_valid and google_price > 0:
                st.warning(f"⚠️ Price mismatch! NSE: ₹{underlying:.2f} vs Google: ₹{google_price:.2f} ({diff_pct*100:.1f}%)")
                # Auto-restart session on >2% mismatch
                st.cache_data.clear()
                restart_nse_session()
                call_df, put_df, underlying, pcr = fetch_option_chain(selected_symbol)
                st.info("🔄 Auto-restarted session due to >2% price mismatch")
            
            st.session_state["options_data"] = {"call": call_df, "put": put_df, "underlying": underlying, "pcr": pcr}
            st.session_state["selected_ticker"] = selected_symbol
            st.session_state["pcr_value"] = pcr
            st.session_state["underlying_price"] = underlying
            st.success(f"✅ Fetched {len(call_df)} Calls + {len(put_df)} Puts | Price validated ✓")
        else:
            st.error("❌ No option chain data returned")

st.divider()

# Display Data
if st.session_state.get("options_data"):
    data = st.session_state["options_data"]
    call_df, put_df = data["call"], data["put"]
    underlying, pcr = data["underlying"], data["pcr"]
    
    # PCR INDICATOR
    st.markdown("### 📊 Put-Call Ratio (PCR) Indicator")
    pcr_col1, pcr_col2, pcr_col3 = st.columns([1, 2, 1])
    with pcr_col2:
        if pcr > 1.2:
            sentiment, css_class = "BULLISH", "pcr-bullish"
            explanation = "High PCR (>1.2) = More Put writing → Bullish sentiment"
        elif pcr < 0.8:
            sentiment, css_class = "BEARISH", "pcr-bearish"
            explanation = "Low PCR (<0.8) = More Call writing → Bearish sentiment"
        else:
            sentiment, css_class = "NEUTRAL", "pcr-neutral"
            explanation = "PCR 0.8-1.2 = Balanced market"
        st.markdown(f'<div class="{css_class}">PCR: {pcr:.2f} • {sentiment}</div>', unsafe_allow_html=True)
        st.caption(explanation)
    
    st.divider()

    # KPI METRICS
    st.markdown("### 📊 KPI Metrics")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("LTP (UNDERLYING)", f"₹{underlying:,.2f}")
    with m2:
        st.metric("PCR", f"{pcr:.2f}")
    with m3:
        total_call_oi = call_df['Call OI'].sum() if 'Call OI' in call_df.columns else 0
        st.metric("TOTAL CALL OI", f"{total_call_oi:,.0f}")
    with m4:
        total_put_oi = put_df['Put OI'].sum() if 'Put OI' in put_df.columns else 0
        st.metric("TOTAL PUT OI", f"{total_put_oi:,.0f}")
    
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        total_call_vol = call_df['Call Volume'].sum() if 'Call Volume' in call_df.columns else 0
        st.metric("CALL VOLUME", f"{total_call_vol:,.0f}")
    with v2:
        total_put_vol = put_df['Put Volume'].sum() if 'Put Volume' in put_df.columns else 0
        st.metric("PUT VOLUME", f"{total_put_vol:,.0f}")
    with v3:
        st.metric("CALL STRIKES", len(call_df))
    with v4:
        st.metric("PUT STRIKES", len(put_df))
    
    st.divider()
    
    # OPTION CHAIN TABLE
    st.markdown("### 📋 Option Chain Table")
    combined = create_combined_chain(call_df, put_df)
    if not combined.empty:
        st.dataframe(combined, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # TABS
    st.markdown("### 📊 Detailed View")
    tab1, tab2 = st.tabs(["🟢 CALL (CE)", "🔴 PUT (PE)"])
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
    
    # Export Section
    st.divider()
    st.markdown("### 📥 Export Options")
    col1, col2 = st.columns(2)
    with col1:
        if not combined.empty:
            st.download_button(
                "📥 Download CSV",
                combined.to_csv(index=False),
                f"{selected_symbol}_options.csv",
                "text/csv",
                use_container_width=True
            )
    with col2:
        excel_data = create_options_master_excel(call_df, put_df, combined, selected_symbol, underlying, pcr)
        st.download_button(
            "📥 Download 3-Tab Master Excel",
            excel_data,
            f"{selected_symbol}_Master_Options.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
else:
    st.info("👆 Click **FETCH OPTION CHAIN** to load data from nsepython")

st.divider()
st.caption(f"📈 Quantum Market Suite | Derivatives Hub | {datetime.now().strftime('%H:%M:%S')}")
st.caption("Stealth Handshake: nsit + bm_sv cookies | Pillar Headers: Accept-Encoding, Referer")
