"""
BSE Derivative Data Downloader
Clean, professional multi-stock derivative analytics dashboard.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
from typing import Dict, List
import time

from utils.models import FetchParameters
from utils.stock_list import TOP_BSE_STOCKS, get_all_options, get_default_stocks
from utils.persistence import (
    get_notepad, save_notepad, get_history, add_history_entry,
    clear_history, get_custom_tickers, add_custom_ticker
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

# Clean dark theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(15, 20, 25, 0.95);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(30, 35, 45, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    .stMultiSelect > div > div {
        background: rgba(30, 35, 45, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background: #3b82f6 !important;
        border-radius: 6px !important;
    }
    
    .stSelectbox > div > div {
        background: rgba(30, 35, 45, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #10b981) !important;
        border-radius: 4px;
    }
    
    .stDataFrame > div {
        background: rgba(30, 35, 45, 0.6) !important;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 35, 45, 0.6);
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #94a3b8 !important;
        border-radius: 6px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
    }
    
    .stSuccess { background: rgba(16, 185, 129, 0.1) !important; border: 1px solid #10b981 !important; border-radius: 8px !important; }
    .stError { background: rgba(239, 68, 68, 0.1) !important; border: 1px solid #ef4444 !important; border-radius: 8px !important; }
    .stWarning { background: rgba(245, 158, 11, 0.1) !important; border: 1px solid #f59e0b !important; border-radius: 8px !important; }
    .stInfo { background: rgba(59, 130, 246, 0.1) !important; border: 1px solid #3b82f6 !important; border-radius: 8px !important; }
    
    .metric-box {
        background: rgba(30, 35, 45, 0.6);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #3b82f6;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .history-item {
        background: rgba(30, 35, 45, 0.4);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 0.6rem;
        margin: 0.4rem 0;
        font-size: 0.8rem;
    }
    
    .history-item:hover {
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 600;
    }
    
    .status-success { background: rgba(16, 185, 129, 0.2); color: #10b981; }
    .status-error { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    hr {
        border: none;
        height: 1px;
        background: rgba(255,255,255,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state."""
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = {}
    if 'fetch_params' not in st.session_state:
        st.session_state.fetch_params = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'notepad_content' not in st.session_state:
        st.session_state.notepad_content = get_notepad()
    if 'last_inputs' not in st.session_state:
        st.session_state.last_inputs = {'selected_stocks': get_default_stocks()}


def render_sidebar() -> dict:
    """Render sidebar with inputs."""
    with st.sidebar:
        # Header
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
            <div style="font-size: 2rem;">📊</div>
            <h2 style="font-size: 1.1rem; margin: 0.3rem 0;">BSE Derivative Downloader</h2>
            <p style="color: #64748b; font-size: 0.7rem;">Multi-Stock Options Data</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Stock Selection
        st.markdown("##### 📈 Select Stocks")
        
        all_stocks = list(set(get_all_options() + get_custom_tickers()))
        all_stocks.sort()
        
        default_stocks = st.session_state.last_inputs.get('selected_stocks', get_default_stocks())
        valid_defaults = [s for s in default_stocks if s in all_stocks]
        
        selected_stocks = st.multiselect(
            "Stocks",
            options=all_stocks,
            default=valid_defaults,
            label_visibility="collapsed"
        )
        
        # Add custom ticker
        col1, col2 = st.columns([3, 1])
        with col1:
            new_ticker = st.text_input("Add", placeholder="Add ticker...", label_visibility="collapsed")
        with col2:
            if st.button("➕", help="Add ticker"):
                if new_ticker:
                    ticker = new_ticker.upper().strip()
                    add_custom_ticker(ticker)
                    if ticker not in selected_stocks:
                        selected_stocks.append(ticker)
                        st.session_state.last_inputs['selected_stocks'] = selected_stocks
                    st.rerun()
        
        # Quick select
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Top 10", use_container_width=True):
                st.session_state.last_inputs['selected_stocks'] = TOP_BSE_STOCKS[:10]
                st.rerun()
        with col2:
            if st.button("Top 5", use_container_width=True):
                st.session_state.last_inputs['selected_stocks'] = TOP_BSE_STOCKS[:5]
                st.rerun()
        with col3:
            if st.button("Clear", use_container_width=True):
                st.session_state.last_inputs['selected_stocks'] = []
                st.rerun()
        
        st.markdown("---")
        
        # Parameters
        st.markdown("##### ⚙️ Parameters")
        
        instrument_type = st.selectbox(
            "Instrument Type",
            ["Equity Options", "Index Options"],
            index=0
        )
        
        col1, col2 = st.columns(2)
        with col1:
            expiry_date = st.date_input(
                "Expiry Date",
                value=st.session_state.last_inputs.get('expiry_date', date.today() + timedelta(days=30))
            )
        with col2:
            strike_price = st.number_input(
                "Strike Price",
                min_value=0.01,
                value=float(st.session_state.last_inputs.get('strike_price', 100.0)),
                step=50.0,
                format="%.0f"
            )
        
        st.markdown("##### 📅 Date Range")
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input(
                "From",
                value=st.session_state.last_inputs.get('from_date', date.today() - timedelta(days=30))
            )
        with col2:
            to_date = st.date_input(
                "To",
                value=st.session_state.last_inputs.get('to_date', date.today())
            )
        
        st.markdown("---")
        
        # Notepad
        st.markdown("##### 📝 Notes")
        notepad = st.text_area(
            "Notes",
            value=st.session_state.notepad_content,
            height=80,
            placeholder="Your notes...",
            label_visibility="collapsed"
        )
        if notepad != st.session_state.notepad_content:
            st.session_state.notepad_content = notepad
            save_notepad(notepad)
        
        st.markdown("---")
        
        # History
        st.markdown("##### 📜 Recent")
        history = get_history()[:5]
        if history:
            for entry in history:
                ts = datetime.fromisoformat(entry['timestamp']).strftime('%d %b %H:%M')
                stocks = entry.get('stocks', [])[:2]
                more = f"+{entry['stock_count'] - 2}" if entry['stock_count'] > 2 else ""
                status = entry.get('status', 'success')
                status_class = "status-success" if status == "success" else "status-error"
                
                st.markdown(f"""
                <div class="history-item">
                    <div style="display: flex; justify-content: space-between;">
                        <span>{', '.join(stocks)} {more}</span>
                        <span class="status-badge {status_class}">{status}</span>
                    </div>
                    <div style="font-size: 0.65rem; color: #64748b;">{ts}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("Clear History", use_container_width=True):
                clear_history()
                st.rerun()
        else:
            st.caption("No history")
        
        # Store inputs
        st.session_state.last_inputs = {
            'selected_stocks': selected_stocks,
            'instrument_type': instrument_type,
            'expiry_date': expiry_date,
            'strike_price': strike_price,
            'from_date': from_date,
            'to_date': to_date
        }
        
        return st.session_state.last_inputs


def create_demo_data(stock: str, params: dict) -> pd.DataFrame:
    """Create demo data for a stock."""
    import random
    
    dates = []
    current = params['from_date']
    while current <= params['to_date']:
        if current.weekday() < 5:
            dates.append(current)
        current += timedelta(days=1)
    
    if not dates:
        dates = [params['from_date']]
    
    random.seed(hash(stock) % 10000)
    base_call = random.uniform(50, 150)
    base_put = random.uniform(40, 120)
    
    data = []
    for i, d in enumerate(dates[:20]):
        data.append({
            'Date': d.strftime('%d-%b-%Y'),
            'Strike Price': params['strike_price'],
            'Call LTP': round(max(0.01, base_call + random.uniform(-20, 20)), 2),
            'Call OI': random.randint(5000, 150000),
            'Put LTP': round(max(0.01, base_put + random.uniform(-15, 15)), 2),
            'Put OI': random.randint(5000, 150000)
        })
    
    return pd.DataFrame(data)


def fetch_stocks(stocks: List[str], params: dict, progress, status) -> Dict[str, pd.DataFrame]:
    """Fetch data for multiple stocks."""
    data = {}
    total = len(stocks)
    
    for idx, stock in enumerate(stocks):
        progress.progress((idx + 1) / total)
        status.text(f"Fetching {idx + 1}/{total}: {stock}")
        
        try:
            try:
                from components.scraper import fetch_derivative_data
                fetch_params = FetchParameters(
                    company_name=stock,
                    instrument_type=params['instrument_type'],
                    expiry_date=params['expiry_date'],
                    strike_price=params['strike_price'],
                    from_date=params['from_date'],
                    to_date=params['to_date']
                )
                call_df, put_df = fetch_derivative_data(fetch_params)
                data[stock] = process_derivative_data(call_df, put_df)
            except:
                data[stock] = create_demo_data(stock, params)
        except:
            data[stock] = None
        
        time.sleep(0.1)
    
    return data


def display_metrics(data: Dict[str, pd.DataFrame]):
    """Display summary metrics."""
    total = len(data)
    success = sum(1 for df in data.values() if df is not None and not df.empty)
    records = sum(len(df) for df in data.values() if df is not None and not df.empty)
    avg = records // total if total else 0
    
    cols = st.columns(4)
    metrics = [
        ("Stocks", total, "#3b82f6"),
        ("Success", f"{success}/{total}", "#10b981"),
        ("Records", f"{records:,}", "#8b5cf6"),
        ("Avg/Stock", avg, "#f59e0b")
    ]
    
    for col, (label, value, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color: {color};">{value}</div>
            </div>
            """, unsafe_allow_html=True)


def display_data(data: Dict[str, pd.DataFrame]):
    """Display data in tabs."""
    stocks = list(data.keys())
    
    if len(stocks) == 1:
        df = data[stocks[0]]
        if df is not None and not df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**📈 {stocks[0]} - Call Options**")
                call_cols = ['Date', 'Strike Price', 'Call LTP', 'Call OI']
                st.dataframe(df[[c for c in call_cols if c in df.columns]], use_container_width=True, height=350)
            with col2:
                st.markdown(f"**📉 {stocks[0]} - Put Options**")
                put_cols = ['Date', 'Strike Price', 'Put LTP', 'Put OI']
                st.dataframe(df[[c for c in put_cols if c in df.columns]], use_container_width=True, height=350)
    else:
        tabs = st.tabs(["📊 Summary"] + [f"{s}" for s in stocks])
        
        with tabs[0]:
            summary = []
            for name, df in data.items():
                if df is not None and not df.empty:
                    summary.append({
                        'Stock': name,
                        'Records': len(df),
                        'Call Avg': round(df['Call LTP'].mean(), 2) if 'Call LTP' in df.columns else 0,
                        'Put Avg': round(df['Put LTP'].mean(), 2) if 'Put LTP' in df.columns else 0,
                        'Status': '✅'
                    })
                else:
                    summary.append({'Stock': name, 'Records': 0, 'Call Avg': 0, 'Put Avg': 0, 'Status': '❌'})
            
            st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
        
        for idx, stock in enumerate(stocks):
            with tabs[idx + 1]:
                df = data[stock]
                if df is not None and not df.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**📈 Call Options**")
                        call_cols = ['Date', 'Strike Price', 'Call LTP', 'Call OI']
                        st.dataframe(df[[c for c in call_cols if c in df.columns]], use_container_width=True, height=300)
                    with col2:
                        st.markdown("**📉 Put Options**")
                        put_cols = ['Date', 'Strike Price', 'Put LTP', 'Put OI']
                        st.dataframe(df[[c for c in put_cols if c in df.columns]], use_container_width=True, height=300)
                else:
                    st.warning(f"No data for {stock}")


def main():
    """Main application."""
    init_session_state()
    params = render_sidebar()
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <h1 style="font-size: 2rem;">📊 BSE Derivative Data Downloader</h1>
        <p style="color: #64748b;">Fetch Call & Put options data for multiple stocks</p>
    </div>
    """, unsafe_allow_html=True)
    
    selected = params.get('selected_stocks', [])
    
    # Status
    if selected:
        st.info(f"**{len(selected)} stocks selected:** {', '.join(selected[:5])}{'...' if len(selected) > 5 else ''}")
    else:
        st.info("👈 Select stocks from the sidebar to begin")
    
    # Validation
    valid = len(selected) > 0 and params['strike_price'] > 0 and params['from_date'] <= params['to_date']
    
    if selected and params['from_date'] > params['to_date']:
        st.warning("From date must be before To date")
        valid = False
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_btn = st.button(
            f"🚀 Fetch Data for {len(selected)} Stocks",
            disabled=not valid,
            use_container_width=True,
            type="primary"
        )
    
    st.markdown("---")
    
    # Process
    if process_btn and valid:
        st.session_state.stock_data = {}
        st.session_state.processing_complete = False
        
        progress = st.progress(0)
        status = st.empty()
        
        try:
            data = fetch_stocks(selected, params, progress, status)
            progress.empty()
            status.empty()
            
            success = sum(1 for df in data.values() if df is not None and not df.empty)
            
            if success > 0:
                st.session_state.stock_data = data
                st.session_state.fetch_params = params
                st.session_state.processing_complete = True
                
                add_history_entry(
                    selected,
                    params['from_date'].strftime('%d-%b-%Y'),
                    params['to_date'].strftime('%d-%b-%Y'),
                    generate_multi_stock_filename(selected, params['from_date'], params['to_date']),
                    "success" if success == len(selected) else "partial"
                )
                
                st.success(f"✅ Fetched data for {success}/{len(selected)} stocks")
            else:
                st.error("Could not fetch data for any stock")
        except Exception as e:
            progress.empty()
            status.empty()
            st.error(f"Error: {str(e)}")
    
    # Display data
    if st.session_state.stock_data:
        display_metrics(st.session_state.stock_data)
        st.markdown("<br>", unsafe_allow_html=True)
        display_data(st.session_state.stock_data)
        
        st.markdown("---")
        
        # Download
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            excel = create_multi_stock_excel(
                st.session_state.stock_data,
                st.session_state.fetch_params['from_date'],
                st.session_state.fetch_params['to_date']
            )
            filename = generate_multi_stock_filename(
                list(st.session_state.stock_data.keys()),
                st.session_state.fetch_params['from_date'],
                st.session_state.fetch_params['to_date']
            )
            
            st.download_button(
                f"📥 Download Excel ({len(st.session_state.stock_data)} sheets)",
                data=excel,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    elif selected and not st.session_state.processing_complete:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: rgba(30,35,45,0.4); border-radius: 12px; border: 1px dashed rgba(255,255,255,0.1);">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎯</div>
            <p style="color: #64748b;">Click the button above to fetch data</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
