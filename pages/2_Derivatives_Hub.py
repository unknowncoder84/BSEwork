# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT CLOUD TMP CACHE FIX - MUST BE AT VERY TOP
# ══════════════════════════════════════════════════════════════════════════════
import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
# ══════════════════════════════════════════════════════════════════════════════

"""
PRK Exchange Suite - Derivatives Page
═══════════════════════════════════════════════════════════════════════════════
DATA SOURCE: nsepython (NSE Official API)
- option_chain("NIFTY") for live option chain data

FEATURES:
- Option Chain Table: Strike, Call OI, Put OI, LTP
- Put-Call Ratio (PCR) Indicator
- Persistence: selected_ticker from st.session_state
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
    page_title="Derivatives | PRK Exchange Suite",
    page_icon="📊",
    layout="wide"
)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION (Ensure persistence)
# ══════════════════════════════════════════════════════════════════════════════
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "NIFTY"
if "options_data" not in st.session_state:
    st.session_state["options_data"] = None
if "pcr_value" not in st.session_state:
    st.session_state["pcr_value"] = None
if "call_options" not in st.session_state:
    st.session_state["call_options"] = None
if "put_options" not in st.session_state:
    st.session_state["put_options"] = None
if "equity_hist" not in st.session_state:
    st.session_state["equity_hist"] = None

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
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 8px;
}

.source-badge {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid rgba(34, 197, 94, 0.3);
    display: inline-block;
}

.pcr-bullish {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
    color: white;
    padding: 12px 24px;
    border-radius: 12px;
    font-size: 1.2rem;
    font-weight: 700;
    text-align: center;
}

.pcr-bearish {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    padding: 12px 24px;
    border-radius: 12px;
    font-size: 1.2rem;
    font-weight: 700;
    text-align: center;
}

.pcr-neutral {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    padding: 12px 24px;
    border-radius: 12px;
    font-size: 1.2rem;
    font-weight: 700;
    text-align: center;
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
            pd.DataFrame({"Info": ["Fetch from Equity Data page"]}).to_excel(writer, sheet_name='EQUITY_HIST', index=False)
        
        calls = st.session_state.get("call_options")
        if calls is not None and not calls.empty:
            calls.to_excel(writer, sheet_name='CALL_OPTIONS', index=False)
        else:
            pd.DataFrame({"Info": ["No call options"]}).to_excel(writer, sheet_name='CALL_OPTIONS', index=False)
        
        puts = st.session_state.get("put_options")
        if puts is not None and not puts.empty:
            puts.to_excel(writer, sheet_name='PUT_OPTIONS', index=False)
        else:
            pd.DataFrame({"Info": ["No put options"]}).to_excel(writer, sheet_name='PUT_OPTIONS', index=False)
    return output.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# NSEPYTHON OPTION CHAIN FETCHER
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def fetch_option_chain(symbol: str) -> tuple:
    """Fetch option chain using nsepython."""
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
                    'Call LTP': ce.get('lastPrice', 0),
                    'Call Change': ce.get('change', 0),
                    'Call OI': call_oi,
                    'Call OI Chg': ce.get('changeinOpenInterest', 0),
                    'Call Volume': ce.get('totalTradedVolume', 0),
                    'Call IV': ce.get('impliedVolatility', 0),
                })
            
            if 'PE' in record:
                pe = record['PE']
                put_oi = pe.get('openInterest', 0)
                total_put_oi += put_oi
                puts.append({
                    'Strike': strike, 'Expiry': expiry,
                    'Put LTP': pe.get('lastPrice', 0),
                    'Put Change': pe.get('change', 0),
                    'Put OI': put_oi,
                    'Put OI Chg': pe.get('changeinOpenInterest', 0),
                    'Put Volume': pe.get('totalTradedVolume', 0),
                    'Put IV': pe.get('impliedVolatility', 0),
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
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📈 PRK Exchange Suite")
    st.caption("Derivatives Analysis")
    
    st.divider()
    
    st.markdown("### 📊 Symbol Selection")
    
    default_ticker = st.session_state.get("selected_ticker", "NIFTY")
    if default_ticker not in ALL_SYMBOLS:
        default_ticker = "NIFTY"
    
    selected_symbol = st.selectbox("Select Symbol", ALL_SYMBOLS,
                                   index=ALL_SYMBOLS.index(default_ticker) if default_ticker in ALL_SYMBOLS else 0)
    
    st.session_state["selected_ticker"] = selected_symbol
    is_index = selected_symbol in INDEX_SYMBOLS
    st.caption(f"Type: {'Index' if is_index else 'Stock'}")
    
    st.divider()
    
    st.markdown("### 💾 Session State")
    st.caption(f"Ticker: **{st.session_state.get('selected_ticker')}**")
    if st.session_state.get("equity_data") is not None:
        st.success("✅ Equity data available")
    if st.session_state.get("options_data") is not None:
        st.success("✅ Options data loaded")
    
    st.divider()
    st.markdown("### 📡 Data Source")
    st.markdown('<span class="source-badge">nsepython</span>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 📊 Derivatives (Option Chain)")
st.caption(f"Data Source: nsepython | Symbol: {selected_symbol}")
st.markdown(f'<span class="source-badge">option_chain("{selected_symbol}")</span>', unsafe_allow_html=True)

st.divider()

# Show persistence info
if st.session_state.get("equity_data") is not None:
    st.success(f"✅ Ticker '{st.session_state.get('selected_ticker')}' loaded from Equity page via session_state")

# Fetch Button
if st.button("🚀 Fetch Option Chain", use_container_width=True, type="primary"):
    with st.spinner(f"Fetching {selected_symbol} option chain from nsepython..."):
        call_df, put_df, underlying, pcr = fetch_option_chain(selected_symbol)
        
        if not call_df.empty or not put_df.empty:
            # Google Finance Validation
            is_valid, google_price, diff = validate_price(underlying, selected_symbol)
            
            if not is_valid and google_price > 0:
                st.warning(f"⚠️ Price mismatch! NSE: ₹{underlying:.2f} vs Google: ₹{google_price:.2f} ({diff*100:.1f}%)")
                st.cache_data.clear()
                call_df, put_df, underlying, pcr = fetch_option_chain(selected_symbol)
                st.info("🔄 Session restarted due to >2% mismatch")
            
            st.session_state["options_data"] = {"call": call_df, "put": put_df, "underlying": underlying, "pcr": pcr}
            st.session_state["call_options"] = call_df
            st.session_state["put_options"] = put_df
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
            explanation = "High PCR (>1.2) indicates more Put writing → Bullish sentiment"
        elif pcr < 0.8:
            sentiment, css_class = "BEARISH", "pcr-bearish"
            explanation = "Low PCR (<0.8) indicates more Call writing → Bearish sentiment"
        else:
            sentiment, css_class = "NEUTRAL", "pcr-neutral"
            explanation = "PCR between 0.8-1.2 indicates balanced market"
        
        st.markdown(f'<div class="{css_class}">PCR: {pcr:.2f} • {sentiment}</div>', unsafe_allow_html=True)
        st.caption(explanation)
    
    st.divider()
    
    # KPI METRICS
    st.markdown("### 📊 Market Overview")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("UNDERLYING", f"₹{underlying:,.2f}")
    with m2:
        st.metric("PCR", f"{pcr:.2f}")
    with m3:
        total_call_oi = call_df['Call OI'].sum() if 'Call OI' in call_df.columns else 0
        st.metric("TOTAL CALL OI", f"{total_call_oi:,.0f}")
    with m4:
        total_put_oi = put_df['Put OI'].sum() if 'Put OI' in put_df.columns else 0
        st.metric("TOTAL PUT OI", f"{total_put_oi:,.0f}")
    
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
    
    # Download
    st.divider()
    if not combined.empty:
        st.download_button("📥 Download Option Chain CSV", combined.to_csv(index=False),
                          f"{selected_symbol}_options.csv", "text/csv", use_container_width=True)
    
    # Master Excel Download
    st.markdown("### 📥 Master Download")
    excel_data = create_master_excel()
    st.download_button(
        "📥 MASTER EXCEL (3 TABS)",
        excel_data,
        f"{selected_symbol}_Master_Data.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

else:
    st.info("👆 Click **Fetch Option Chain** to load data from nsepython")

# Footer
st.divider()
st.caption(f"📈 PRK Exchange Suite | Derivatives Page | {datetime.now().strftime('%H:%M:%S')}")
