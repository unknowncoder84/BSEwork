"""
Quantum Market Suite - Unified NSE & BSE Data Platform
Professional Glassmorphism UI with Persistent Memory
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
from typing import Dict, List, Optional
import time
import json

# Import persistence
from quantum.persistence import PersistenceManager
from quantum.models import SearchHistoryEntry

# Initialize persistence manager
persistence = PersistenceManager("config.json")

# Stock lists
NSE_STOCKS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "SBIN", 
    "BHARTIARTL", "KOTAKBANK", "ITC", "LT", "AXISBANK", "ASIANPAINT", "MARUTI",
    "BAJFINANCE", "TITAN", "SUNPHARMA", "ULTRACEMCO", "NESTLEIND", "WIPRO",
    "HCLTECH", "POWERGRID", "NTPC", "TATAMOTORS", "TATASTEEL", "ONGC", "JSWSTEEL",
    "ADANIENT", "ADANIPORTS", "TECHM", "INDUSINDBK", "BAJAJFINSV", "GRASIM"
]

BSE_STOCKS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "SBIN",
    "BHARTIARTL", "KOTAKBANK", "ITC", "LT", "AXISBANK", "ASIANPAINT", "MARUTI",
    "BAJFINANCE", "TITAN", "SUNPHARMA", "ULTRACEMCO", "NESTLEIND", "WIPRO"
]

st.set_page_config(
    page_title="Quantum Market Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_glassmorphism_css(is_dark: bool = True) -> str:
    """Return Glassmorphism CSS for dark/light theme."""
    if is_dark:
        return """
        <style>
            /* Dark Glassmorphism Theme */
            .stApp {
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0d0d1f 100%);
            }
            
            /* Glassmorphism sidebar */
            section[data-testid="stSidebar"] {
                background: rgba(15, 15, 35, 0.7) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
            
            section[data-testid="stSidebar"] > div {
                background: transparent !important;
            }
            
            /* Glass cards */
            .glass-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 1.5rem;
                margin-bottom: 1rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            
            /* Brand header */
            .brand-header {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 1rem 0;
                margin-bottom: 1rem;
            }
            
            .brand-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            }
            
            .brand-text {
                font-size: 1.25rem;
                font-weight: 700;
                background: linear-gradient(135deg, #fff, #a5b4fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            /* Section titles */
            .section-title {
                font-size: 0.7rem;
                color: rgba(255, 255, 255, 0.5);
                text-transform: uppercase;
                letter-spacing: 2px;
                margin: 1.5rem 0 0.75rem 0;
                font-weight: 600;
            }
            
            /* Metric cards */
            .metric-card {
                background: rgba(99, 102, 241, 0.1);
                border: 1px solid rgba(99, 102, 241, 0.2);
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
            }
            
            .metric-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: #a5b4fc;
            }
            
            .metric-label {
                font-size: 0.75rem;
                color: rgba(255, 255, 255, 0.6);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            /* History items */
            .history-item {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 0.75rem;
                margin-bottom: 0.5rem;
                font-size: 0.85rem;
            }
            
            /* Buttons */
            .stButton > button {
                background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
                border: none !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
            }
            
            /* Inputs */
            .stTextInput > div > div > input,
            .stSelectbox > div > div,
            .stMultiSelect > div > div {
                background: rgba(255, 255, 255, 0.05) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 8px !important;
            }
            
            /* DataFrames */
            .stDataFrame {
                background: rgba(255, 255, 255, 0.02) !important;
                border-radius: 12px !important;
            }
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 10px;
                padding: 4px;
            }
            
            .stTabs [data-baseweb="tab"] {
                border-radius: 8px;
            }
        </style>
        """
    else:
        return """
        <style>
            /* Light Glassmorphism Theme */
            .stApp {
                background: linear-gradient(135deg, #f0f4ff 0%, #e8ecf7 50%, #f5f7ff 100%);
            }
            
            section[data-testid="stSidebar"] {
                background: rgba(255, 255, 255, 0.7) !important;
                backdrop-filter: blur(20px) !important;
                border-right: 1px solid rgba(0, 0, 0, 0.05) !important;
            }
            
            .glass-card {
                background: rgba(255, 255, 255, 0.6);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                border: 1px solid rgba(0, 0, 0, 0.05);
                padding: 1.5rem;
                margin-bottom: 1rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .brand-text {
                background: linear-gradient(135deg, #1e1b4b, #6366f1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .section-title {
                color: rgba(0, 0, 0, 0.5);
            }
            
            .metric-value {
                color: #4f46e5;
            }
            
            .metric-label {
                color: rgba(0, 0, 0, 0.6);
            }
        </style>
        """

# Get current theme
current_theme = persistence.get_theme()
is_dark = current_theme == "dark"

# Apply theme CSS
st.markdown(get_glassmorphism_css(is_dark), unsafe_allow_html=True)

# ============== SIDEBAR ==============
with st.sidebar:
    # Brand header
    st.markdown("""
        <div class="brand-header">
            <div class="brand-icon">⚡</div>
            <div class="brand-text">Quantum Market Suite</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.caption("NSE & BSE Unified Data Platform")
    
    st.divider()
    
    # Theme toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<p class="section-title">Theme</p>', unsafe_allow_html=True)
    with col2:
        theme_toggle = st.toggle("🌙", value=is_dark, key="theme_toggle")
        if theme_toggle != is_dark:
            persistence.set_theme("dark" if theme_toggle else "light")
            st.rerun()
    
    st.divider()
    
    # Exchange Selection
    st.markdown('<p class="section-title">Exchange</p>', unsafe_allow_html=True)
    exchange = st.radio(
        "Select Exchange",
        options=["NSE", "BSE"],
        horizontal=True,
        key="exchange_selector",
        label_visibility="collapsed"
    )
    
    # Save exchange preference
    if exchange != persistence.get_exchange():
        persistence.set_exchange(exchange)
    
    st.divider()
    
    # Data Mode Selection
    st.markdown('<p class="section-title">Data Mode</p>', unsafe_allow_html=True)
    data_mode = st.radio(
        "Select Data Mode",
        options=["Equity (EQ)", "Derivatives (OPT)", "Both"],
        key="data_mode",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Stock Selection
    st.markdown('<p class="section-title">Stock Selection</p>', unsafe_allow_html=True)
    
    stock_list = NSE_STOCKS if exchange == "NSE" else BSE_STOCKS
    selected_stocks = st.multiselect(
        "Select Stocks",
        options=stock_list,
        default=stock_list[:3],
        key="stock_selector",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Parameters Section (for Derivatives)
    if data_mode in ["Derivatives (OPT)", "Both"]:
        st.markdown('<p class="section-title">Derivative Parameters</p>', unsafe_allow_html=True)
        
        # Strike Price - USER INPUT (NOT HARDCODED)
        strike_price = st.number_input(
            "Strike Price",
            min_value=1.0,
            max_value=100000.0,
            value=st.session_state.get("strike_price_value", 2500.0),
            step=50.0,
            key="strike_price_input",
            help="Enter the strike price for options data"
        )
        st.session_state["strike_price_value"] = strike_price
        
        # Option Type
        option_type = st.selectbox(
            "Option Type",
            options=["Both (CE & PE)", "Call (CE)", "Put (PE)"],
            key="option_type"
        )
        
        # Expiry Date
        expiry_date = st.date_input(
            "Expiry Date",
            value=date.today() + timedelta(days=30),
            key="expiry_date"
        )
        
        st.divider()
    
    # Date Range - Quantum Calendar
    st.markdown('<p class="section-title">📅 Quantum Calendar</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input(
            "From",
            value=date.today() - timedelta(days=30),
            key="from_date"
        )
    with col2:
        to_date = st.date_input(
            "To",
            value=date.today(),
            key="to_date"
        )
    
    st.divider()
    
    # Fetch Button
    fetch_disabled = len(selected_stocks) == 0
    
    if st.button(
        "🚀 Fetch Data", 
        disabled=fetch_disabled, 
        use_container_width=True, 
        type="primary",
        key="fetch_button"
    ):
        st.session_state["fetch_triggered"] = True
        st.session_state["fetch_params"] = {
            "exchange": exchange,
            "stocks": selected_stocks,
            "data_mode": data_mode,
            "strike_price": strike_price if data_mode != "Equity (EQ)" else None,
            "option_type": option_type if data_mode != "Equity (EQ)" else None,
            "expiry_date": expiry_date if data_mode != "Equity (EQ)" else None,
            "from_date": from_date,
            "to_date": to_date
        }
    
    if fetch_disabled:
        st.warning("Select at least one stock")
    
    st.divider()
    
    # Persistent Notepad
    st.markdown('<p class="section-title">📝 Notepad</p>', unsafe_allow_html=True)
    
    notepad_content = st.text_area(
        "Notes",
        value=persistence.get_notepad(),
        height=120,
        key="notepad",
        label_visibility="collapsed",
        placeholder="Write your analysis notes here...\nSaved automatically to config.json"
    )
    
    # Auto-save notepad
    if notepad_content != persistence.get_notepad():
        persistence.update_notepad(notepad_content)
        st.toast("📝 Notes saved!", icon="✅")


# ============== MAIN CONTENT ==============
st.markdown(f"""
    <h1 style="background: linear-gradient(135deg, {'#fff' if is_dark else '#1e1b4b'}, {'#a5b4fc' if is_dark else '#6366f1'}); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem;">
        ⚡ Quantum Market Suite
    </h1>
""", unsafe_allow_html=True)
st.caption(f"Unified {exchange} Data Platform • Equity & Derivatives")

# Metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Exchange", exchange)

with col2:
    st.metric("Stocks", len(selected_stocks))

with col3:
    st.metric("Date Range", f"{(to_date - from_date).days} days")

with col4:
    mode_short = data_mode.split()[0]
    st.metric("Mode", mode_short)

st.divider()

# Data fetching
if st.session_state.get("fetch_triggered", False):
    params = st.session_state.get("fetch_params", {})
    
    with st.spinner(f"Fetching data from {params.get('exchange', 'NSE')}..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        fetched_data = {}
        errors = []
        
        for i, stock in enumerate(params.get("stocks", [])):
            try:
                status_text.text(f"Fetching data for {stock}...")
                progress_bar.progress((i + 1) / len(params.get("stocks", [1])))
                
                # Create sample data structure
                # In production, this would call the actual scrapers
                sample_data = create_sample_data(
                    stock,
                    params.get("data_mode", "Both"),
                    params.get("from_date", date.today() - timedelta(days=30)),
                    params.get("to_date", date.today()),
                    params.get("strike_price"),
                    params.get("option_type")
                )
                
                fetched_data[stock] = sample_data
                
                # Add to search history
                persistence.add_search_history(SearchHistoryEntry.create(
                    symbol=stock,
                    exchange=params.get("exchange", "NSE"),
                    start_date=params.get("from_date", date.today()),
                    end_date=params.get("to_date", date.today()),
                    data_type=params.get("data_mode", "both")
                ))
                
            except Exception as e:
                errors.append(f"{stock}: {str(e)}")
        
        progress_bar.empty()
        status_text.empty()
        
        if errors:
            for error in errors:
                st.error(f"⚠️ {error}")
        
        if fetched_data:
            st.success(f"✅ Data fetched for {len(fetched_data)} stocks")
            st.session_state["fetched_data"] = fetched_data
    
    st.session_state["fetch_triggered"] = False

# Display fetched data
if st.session_state.get("fetched_data"):
    st.markdown("### 📊 Market Data")
    
    tabs = st.tabs(list(st.session_state["fetched_data"].keys()))
    
    for tab, (stock, df) in zip(tabs, st.session_state["fetched_data"].items()):
        with tab:
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Export section
    st.markdown("### 📥 Export Data")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        export_filename = st.text_input(
            "Filename",
            value=generate_export_filename(
                list(st.session_state["fetched_data"].keys()),
                st.session_state.get("fetch_params", {}).get("exchange", "NSE"),
                st.session_state.get("fetch_params", {}).get("from_date", date.today()),
                st.session_state.get("fetch_params", {}).get("to_date", date.today())
            ),
            key="export_filename"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Export Excel", use_container_width=True):
            try:
                excel_bytes = create_multi_stock_excel(
                    st.session_state["fetched_data"],
                    st.session_state.get("fetch_params", {}).get("from_date", date.today()),
                    st.session_state.get("fetch_params", {}).get("to_date", date.today())
                )
                
                st.download_button(
                    label="⬇️ Download",
                    data=excel_bytes,
                    file_name=export_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                # Record export
                persistence.add_export_history(export_filename)
                st.success("✅ Export ready!")
                
            except Exception as e:
                st.error(f"Export failed: {str(e)}")

else:
    # Empty state
    st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <h2 style="margin-bottom: 1rem;">📈 No Data Loaded</h2>
            <p style="opacity: 0.7;">Select stocks from the sidebar and click 'Fetch Data' to begin.</p>
        </div>
    """, unsafe_allow_html=True)


# Search History section
st.divider()
st.markdown("### 🕐 Search History")

history = persistence.get_search_history()

if history:
    for entry in history[:5]:
        st.markdown(f"""
            <div class="history-item">
                📁 <strong>{entry.symbol}</strong> ({entry.exchange}) | 
                {entry.start_date} → {entry.end_date} | 
                <span style="opacity: 0.6;">{entry.data_type}</span>
            </div>
        """, unsafe_allow_html=True)
    
    if st.button("🗑️ Clear History", key="clear_history"):
        persistence.clear_search_history()
        st.rerun()
else:
    st.info("No search history. Start by fetching some data!")


# Footer
st.divider()
st.caption("Quantum Market Suite v2.0 • NSE & BSE Unified Platform • Data persisted to config.json")


# ============== HELPER FUNCTIONS ==============

def create_sample_data(
    stock: str,
    data_mode: str,
    from_date: date,
    to_date: date,
    strike_price: Optional[float] = None,
    option_type: Optional[str] = None
) -> pd.DataFrame:
    """Create sample data structure for demonstration."""
    import numpy as np
    
    # Generate date range
    dates = pd.date_range(start=from_date, end=to_date, freq='B')
    
    data_rows = []
    
    # Add Equity data
    if data_mode in ["Equity (EQ)", "Both"]:
        base_price = np.random.uniform(1000, 5000)
        for d in dates:
            open_price = base_price * np.random.uniform(0.98, 1.02)
            high_price = open_price * np.random.uniform(1.0, 1.03)
            low_price = open_price * np.random.uniform(0.97, 1.0)
            close_price = np.random.uniform(low_price, high_price)
            volume = np.random.randint(100000, 10000000)
            
            data_rows.append({
                'Date': d.strftime('%Y-%m-%d'),
                'Series': 'EQ',
                'Open': round(open_price, 2),
                'High': round(high_price, 2),
                'Low': round(low_price, 2),
                'Close': round(close_price, 2),
                'Volume': volume,
                'Open Interest': '-'
            })
            
            base_price = close_price
    
    # Add Derivative data
    if data_mode in ["Derivatives (OPT)", "Both"] and strike_price:
        for d in dates[-10:]:  # Last 10 days for derivatives
            for opt_type in ['CE', 'PE']:
                if option_type == "Call (CE)" and opt_type == "PE":
                    continue
                if option_type == "Put (PE)" and opt_type == "CE":
                    continue
                
                base_premium = np.random.uniform(50, 500)
                open_price = base_premium * np.random.uniform(0.95, 1.05)
                high_price = open_price * np.random.uniform(1.0, 1.1)
                low_price = open_price * np.random.uniform(0.9, 1.0)
                close_price = np.random.uniform(low_price, high_price)
                volume = np.random.randint(10000, 500000)
                oi = np.random.randint(50000, 2000000)
                
                data_rows.append({
                    'Date': d.strftime('%Y-%m-%d'),
                    'Series': f'OPT-{opt_type}',
                    'Open': round(open_price, 2),
                    'High': round(high_price, 2),
                    'Low': round(low_price, 2),
                    'Close': round(close_price, 2),
                    'Volume': volume,
                    'Open Interest': oi
                })
    
    return pd.DataFrame(data_rows)


def generate_export_filename(stocks: List[str], exchange: str, from_date: date, to_date: date) -> str:
    """Generate filename for export."""
    from_str = from_date.strftime("%Y%m%d")
    to_str = to_date.strftime("%Y%m%d")
    
    if len(stocks) == 1:
        return f"{exchange}_{stocks[0]}_{from_str}_{to_str}.xlsx"
    elif len(stocks) <= 3:
        stock_str = "_".join(stocks)
        return f"{exchange}_{stock_str}_{from_str}_{to_str}.xlsx"
    else:
        return f"{exchange}_MultiStock_{len(stocks)}_{from_str}_{to_str}.xlsx"


def create_multi_stock_excel(stock_data: Dict[str, pd.DataFrame], from_date: date, to_date: date) -> bytes:
    """Create Excel file with multiple sheets, one per stock."""
    import io
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = []
        for stock_name, df in stock_data.items():
            if df is not None and not df.empty:
                eq_rows = len(df[df['Series'] == 'EQ']) if 'Series' in df.columns else 0
                opt_rows = len(df[df['Series'].str.startswith('OPT')]) if 'Series' in df.columns else 0
                summary_data.append({
                    'Stock': stock_name,
                    'Total Records': len(df),
                    'Equity Records': eq_rows,
                    'Option Records': opt_rows,
                    'Date Range': f"{from_date.strftime('%d-%b-%Y')} to {to_date.strftime('%d-%b-%Y')}"
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Individual stock sheets
        for stock_name, df in stock_data.items():
            if df is not None and not df.empty:
                sheet_name = stock_name[:31]  # Excel sheet name limit
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    output.seek(0)
    return output.getvalue()
