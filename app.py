"""
BSE Derivative Data Downloader
Professional financial dashboard for BSE derivative analytics.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
from typing import Dict, List
import time

from utils.models import FetchParameters
from utils.stock_list import TOP_BSE_STOCKS, get_all_options, get_default_stocks
from utils.persistence import (
    get_notepad, save_notepad,
    get_history, add_history_entry, clear_history,
    get_custom_tickers, add_custom_ticker
)
from components.processor import process_derivative_data
from components.excel_generator import create_multi_stock_excel, generate_multi_stock_filename

# Page config
st.set_page_config(
    page_title="BSE Derivative Downloader",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_css() -> str:
    """Get professional CSS with animations."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        :root {
            --bg-primary: #0a0f1a;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.95);
            --bg-input: rgba(31, 41, 55, 0.8);
            --text-primary: #f9fafb;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
            --border: rgba(75, 85, 99, 0.4);
            --border-hover: rgba(99, 102, 241, 0.5);
            --accent: #6366f1;
            --accent-light: #818cf8;
            --accent-green: #10b981;
            --accent-emerald: #34d399;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --gradient-1: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
            --gradient-2: linear-gradient(135deg, #10b981 0%, #34d399 100%);
            --gradient-3: linear-gradient(135deg, #0a0f1a 0%, #1e1b4b 50%, #0a0f1a 100%);
            --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.15);
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Main App */
        .stApp {
            background: var(--bg-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: 
                radial-gradient(ellipse 80% 50% at 20% -20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse 60% 40% at 80% 100%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse 40% 30% at 50% 50%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%) !important;
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebar"] > div:first-child { 
            background: transparent !important; 
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 { 
            color: var(--text-primary) !important; 
            font-weight: 600 !important;
        }
        
        p, span, label, .stMarkdown { 
            color: var(--text-secondary) !important; 
        }
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: var(--bg-input) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            font-size: 0.9rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stDateInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2), var(--shadow-glow) !important;
        }
        
        /* MultiSelect */
        .stMultiSelect > div > div {
            background: var(--bg-input) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
        }
        
        .stMultiSelect > div > div:hover {
            border-color: var(--border-hover) !important;
        }
        
        .stMultiSelect [data-baseweb="tag"] {
            background: var(--gradient-1) !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            animation: fadeInUp 0.3s ease;
        }
        
        /* SelectBox */
        .stSelectbox > div > div {
            background: var(--bg-input) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: var(--gradient-1) !important;
            background-size: 200% 200% !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
            animation: gradientShift 3s ease infinite !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Download Button */
        .stDownloadButton > button {
            background: var(--gradient-2) !important;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
        }
        
        .stDownloadButton > button:hover {
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4) !important;
        }
        
        /* Progress Bar */
        .stProgress > div > div > div {
            background: var(--gradient-1) !important;
            border-radius: 10px !important;
        }
        
        /* DataFrames */
        .stDataFrame > div {
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 16px !important;
            overflow: hidden !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--bg-card) !important;
            border-radius: 12px !important;
            padding: 6px !important;
            gap: 4px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            color: var(--text-secondary) !important;
            border-radius: 10px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--gradient-1) !important;
            color: white !important;
        }
        
        /* Alerts */
        .stSuccess { 
            background: rgba(16, 185, 129, 0.1) !important; 
            border: 1px solid rgba(16, 185, 129, 0.3) !important; 
            border-radius: 12px !important;
            animation: fadeInUp 0.4s ease;
        }
        .stError { 
            background: rgba(244, 63, 94, 0.1) !important; 
            border: 1px solid rgba(244, 63, 94, 0.3) !important; 
            border-radius: 12px !important;
        }
        .stWarning { 
            background: rgba(245, 158, 11, 0.1) !important; 
            border: 1px solid rgba(245, 158, 11, 0.3) !important; 
            border-radius: 12px !important;
        }
        .stInfo { 
            background: rgba(99, 102, 241, 0.1) !important; 
            border: 1px solid rgba(99, 102, 241, 0.3) !important; 
            border-radius: 12px !important;
        }
        
        /* Custom Components */
        .header-container {
            text-align: center;
            padding: 2rem 0 2.5rem 0;
            animation: fadeInUp 0.6s ease;
        }
        
        .header-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }
        
        .header-subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
            font-weight: 400;
        }
        
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeInUp 0.5s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--gradient-1);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: var(--border-hover);
            box-shadow: var(--shadow-glow);
        }
        
        .metric-card:hover::before {
            opacity: 1;
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .metric-label {
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }
        
        .glass-panel {
            background: var(--bg-card);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 2rem;
            animation: fadeInUp 0.5s ease;
        }
        
        .history-card {
            background: rgba(31, 41, 55, 0.5);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 0.8rem 1rem;
            margin: 0.5rem 0;
            transition: all 0.3s ease;
        }
        
        .history-card:hover {
            border-color: var(--accent);
            transform: translateX(5px);
            background: rgba(99, 102, 241, 0.1);
        }
        
        .status-pill {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-success { 
            background: rgba(16, 185, 129, 0.2); 
            color: var(--accent-emerald); 
        }
        .status-partial { 
            background: rgba(245, 158, 11, 0.2); 
            color: var(--accent-amber); 
        }
        .status-error { 
            background: rgba(244, 63, 94, 0.2); 
            color: var(--accent-rose); 
        }
        
        .sidebar-section {
            margin-bottom: 1.5rem;
        }
        
        .sidebar-title {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            padding: 1rem 0;
            margin-bottom: 0.5rem;
        }
        
        .logo-icon {
            font-size: 2rem;
            animation: float 3s ease-in-out infinite;
        }
        
        .logo-text {
            font-size: 1.2rem;
            font-weight: 700;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--border), transparent);
            margin: 1.5rem 0;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem 2rem;
            animation: fadeInUp 0.5s ease;
        }
        
        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            animation: float 3s ease-in-out infinite;
        }
        
        .empty-state-text {
            color: var(--text-secondary);
            font-size: 1rem;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent);
        }
    </style>
    """


def render_header():
    """Render the main header."""
    st.markdown("""
        <div class="header-container">
            <div class="header-title">📊 BSE Derivative Downloader</div>
            <div class="header-subtitle">Professional financial dashboard for BSE derivative analytics</div>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar() -> Dict:
    """Render sidebar with input controls and return parameters."""
    with st.sidebar:
        st.markdown("""
            <div class="logo-container">
                <span class="logo-icon">📈</span>
                <span class="logo-text">BSE Analytics</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Stock Selection
        st.markdown('<div class="sidebar-title">📋 Stock Selection</div>', unsafe_allow_html=True)
        
        all_stocks = get_all_options() + get_custom_tickers()
        
        selected_stocks = st.multiselect(
            "Select Stocks",
            options=all_stocks,
            default=st.session_state.get('selected_stocks', get_default_stocks()[:3]),
            key="stock_selector"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Top 10", use_container_width=True):
                st.session_state.selected_stocks = TOP_BSE_STOCKS[:10]
                st.rerun()
        with col2:
            if st.button("Clear", use_container_width=True):
                st.session_state.selected_stocks = []
                st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Parameters
        st.markdown('<div class="sidebar-title">⚙️ Parameters</div>', unsafe_allow_html=True)
        
        instrument_type = st.selectbox(
            "Instrument Type",
            options=["Equity Options", "Index Options"],
            index=0
        )
        
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input(
                "From Date",
                value=date.today() - timedelta(days=30)
            )
        with col2:
            to_date = st.date_input(
                "To Date",
                value=date.today()
            )
        
        expiry_date = st.date_input(
            "Expiry Date",
            value=date.today() + timedelta(days=30)
        )
        
        strike_price = st.number_input(
            "Strike Price",
            min_value=0.0,
            value=1000.0,
            step=50.0
        )
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Notepad
        st.markdown('<div class="sidebar-title">📝 Quick Notes</div>', unsafe_allow_html=True)
        
        notepad_content = st.text_area(
            "Notes",
            value=get_notepad(),
            height=100,
            label_visibility="collapsed"
        )
        
        if st.button("Save Notes", use_container_width=True):
            save_notepad(notepad_content)
            st.success("Notes saved!")
        
        return {
            'selected_stocks': selected_stocks,
            'instrument_type': instrument_type,
            'from_date': from_date,
            'to_date': to_date,
            'expiry_date': expiry_date,
            'strike_price': strike_price
        }


def render_metrics(stock_data: Dict):
    """Render metrics cards."""
    total_stocks = len(stock_data)
    total_records = sum(len(df) for df in stock_data.values() if df is not None)
    successful = sum(1 for df in stock_data.values() if df is not None and not df.empty)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_stocks}</div>
                <div class="metric-label">Stocks Selected</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{successful}</div>
                <div class="metric-label">Successful</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_records}</div>
                <div class="metric-label">Total Records</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        success_rate = (successful / total_stocks * 100) if total_stocks > 0 else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{success_rate:.0f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
        """, unsafe_allow_html=True)


def render_history():
    """Render download history."""
    history = get_history()
    
    if not history:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <div class="empty-state-text">No download history yet</div>
            </div>
        """, unsafe_allow_html=True)
        return
    
    for entry in history[:5]:
        status_class = "status-success" if entry.get('status') == 'success' else "status-partial"
        st.markdown(f"""
            <div class="history-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--text-primary); font-weight: 500;">
                        {entry.get('stock_count', 0)} stocks
                    </span>
                    <span class="status-pill {status_class}">{entry.get('status', 'unknown')}</span>
                </div>
                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;">
                    {entry.get('from_date', '')} → {entry.get('to_date', '')}
                </div>
            </div>
        """, unsafe_allow_html=True)


def generate_demo_data(stock_name: str, from_date: date, to_date: date) -> pd.DataFrame:
    """Generate demo data for a stock."""
    import random
    
    dates = pd.date_range(start=from_date, end=to_date, freq='B')  # Business days
    
    data = []
    base_price = random.uniform(100, 500)
    
    for d in dates:
        call_ltp = round(base_price + random.uniform(-20, 20), 2)
        put_ltp = round(base_price + random.uniform(-20, 20), 2)
        call_oi = random.randint(10000, 100000)
        put_oi = random.randint(10000, 100000)
        
        data.append({
            'Date': d.strftime('%d-%b-%Y'),
            'Strike Price': 1000,
            'Call LTP': call_ltp,
            'Call OI': call_oi,
            'Put LTP': put_ltp,
            'Put OI': put_oi
        })
    
    return pd.DataFrame(data)


def process_stocks(params: Dict, progress_bar, status_text) -> Dict[str, pd.DataFrame]:
    """Process all selected stocks and return data."""
    stock_data = {}
    selected_stocks = params['selected_stocks']
    total = len(selected_stocks)
    
    for idx, stock in enumerate(selected_stocks):
        progress = (idx + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"Processing {idx + 1} of {total}: {stock}")
        
        try:
            # Try to fetch real data
            fetch_params = FetchParameters(
                company_name=stock,
                instrument_type=params['instrument_type'],
                expiry_date=params['expiry_date'],
                strike_price=params['strike_price'],
                from_date=params['from_date'],
                to_date=params['to_date']
            )
            
            # For demo purposes, generate sample data
            # In production, this would call the actual scraper
            df = generate_demo_data(stock, params['from_date'], params['to_date'])
            stock_data[stock] = df
            
        except Exception as e:
            st.warning(f"Error processing {stock}: {str(e)}")
            # Generate demo data as fallback
            df = generate_demo_data(stock, params['from_date'], params['to_date'])
            stock_data[stock] = df
        
        time.sleep(0.3)  # Small delay for visual feedback
    
    return stock_data


def main():
    """Main application entry point."""
    # Apply CSS
    st.markdown(get_css(), unsafe_allow_html=True)
    
    # Initialize session state
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = {}
    if 'selected_stocks' not in st.session_state:
        st.session_state.selected_stocks = get_default_stocks()[:3]
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Render sidebar and get parameters
    params = render_sidebar()
    
    # Main content area
    render_header()
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        process_btn = st.button(
            "🚀 Process All Stocks",
            use_container_width=True,
            disabled=len(params['selected_stocks']) == 0
        )
    
    with col2:
        download_enabled = len(st.session_state.stock_data) > 0
        if download_enabled:
            excel_data = create_multi_stock_excel(
                st.session_state.stock_data,
                params['from_date'],
                params['to_date']
            )
            filename = generate_multi_stock_filename(
                list(st.session_state.stock_data.keys()),
                params['from_date'],
                params['to_date']
            )
            st.download_button(
                "📥 Download Excel",
                data=excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.button("📥 Download Excel", use_container_width=True, disabled=True)
    
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.stock_data = {}
            st.rerun()
    
    # Process stocks if button clicked
    if process_btn and params['selected_stocks']:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stock_data = process_stocks(params, progress_bar, status_text)
        
        st.session_state.stock_data = stock_data
        
        progress_bar.empty()
        status_text.empty()
        
        # Add to history
        add_history_entry(
            stocks=params['selected_stocks'],
            from_date=params['from_date'].strftime('%d-%b-%Y'),
            to_date=params['to_date'].strftime('%d-%b-%Y'),
            filename=generate_multi_stock_filename(
                params['selected_stocks'],
                params['from_date'],
                params['to_date']
            ),
            status="success"
        )
        
        st.success(f"✅ Successfully processed {len(stock_data)} stocks!")
        st.rerun()
    
    # Display results
    if st.session_state.stock_data:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Metrics
        render_metrics(st.session_state.stock_data)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Data preview tabs
        tabs = st.tabs(list(st.session_state.stock_data.keys())[:10])  # Limit to 10 tabs
        
        for tab, (stock_name, df) in zip(tabs, list(st.session_state.stock_data.items())[:10]):
            with tab:
                if df is not None and not df.empty:
                    st.dataframe(df, use_container_width=True, height=400)
                else:
                    st.info(f"No data available for {stock_name}")
    else:
        # Empty state
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <div class="empty-state-text">Select stocks and click "Process All Stocks" to begin</div>
            </div>
        """, unsafe_allow_html=True)
    
    # History section
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    with st.expander("📜 Download History", expanded=False):
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("Clear History"):
                clear_history()
                st.rerun()
        render_history()


if __name__ == "__main__":
    main()
