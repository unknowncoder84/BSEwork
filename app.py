"""
BSE Derivative Data Downloader
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
from components.excel_generator import create_multi_stock_excel, generate_multi_stock_filename

st.set_page_config(
    page_title="BSE Derivatives",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        * { font-family: 'Inter', sans-serif; }
        
        .stApp { background: #0f1419; }
        #MainMenu, footer, header { display: none; }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: #1a1f26 !important;
            border-right: 1px solid #2d3748;
        }
        [data-testid="stSidebar"] > div { background: transparent !important; }
        
        /* Hide sidebar collapse button */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        button[kind="header"] {
            display: none !important;
        }
        
        /* Typography */
        h1, h2, h3 { color: #f7fafc !important; }
        p, label, span { color: #a0aec0 !important; }
        
        /* Inputs */
        .stTextInput input, .stNumberInput input, .stTextArea textarea {
            background: #1a202c !important;
            border: 1px solid #2d3748 !important;
            border-radius: 6px !important;
            color: #f7fafc !important;
        }
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #ed8936 !important;
            box-shadow: 0 0 0 1px #ed8936 !important;
        }
        
        .stDateInput input {
            background: #1a202c !important;
            border: 1px solid #2d3748 !important;
            border-radius: 6px !important;
            color: #f7fafc !important;
        }
        
        .stSelectbox > div > div {
            background: #1a202c !important;
            border: 1px solid #2d3748 !important;
            border-radius: 6px !important;
        }
        
        .stMultiSelect > div > div {
            background: #1a202c !important;
            border: 1px solid #2d3748 !important;
            border-radius: 6px !important;
        }
        .stMultiSelect [data-baseweb="tag"] {
            background: #ed8936 !important;
            color: white !important;
            border-radius: 4px !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: #ed8936 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            padding: 0.5rem 1rem !important;
        }
        .stButton > button:hover {
            background: #dd6b20 !important;
        }
        
        .stDownloadButton > button {
            background: #48bb78 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
        }
        
        /* Progress */
        .stProgress > div > div > div { background: #ed8936 !important; }
        .stProgress > div > div { background: #2d3748 !important; }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: #1a1f26 !important;
            border-radius: 8px !important;
            padding: 4px !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            color: #718096 !important;
            border-radius: 4px !important;
        }
        .stTabs [aria-selected="true"] {
            background: #ed8936 !important;
            color: white !important;
        }
        
        /* Cards */
        .metric-card {
            background: #1a1f26;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 1rem;
            border-left: 3px solid #ed8936;
        }
        .metric-label {
            font-size: 0.75rem;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 1.75rem;
            font-weight: 600;
            color: #f7fafc;
            margin-top: 0.25rem;
        }
        
        .brand { 
            display: flex; 
            align-items: center; 
            gap: 0.75rem; 
            padding: 1rem 0; 
            border-bottom: 1px solid #2d3748;
            margin-bottom: 1rem;
        }
        .brand-icon {
            width: 32px;
            height: 32px;
            background: #ed8936;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .brand-text { font-size: 1rem; font-weight: 600; color: #f7fafc; }
        
        .section-title {
            font-size: 0.7rem;
            color: #4a5568;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 1.25rem 0 0.5rem 0;
            font-weight: 600;
        }
        
        .page-title { font-size: 1.5rem; font-weight: 600; color: #f7fafc; margin-bottom: 0.5rem; }
        .page-subtitle { font-size: 0.875rem; color: #718096; }
        
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0f1419; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 3px; }
    </style>
    """

def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div class="brand">
                <div class="brand-icon">📊</div>
                <div class="brand-text">BSE Terminal</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Stocks</div>', unsafe_allow_html=True)
        
        all_stocks = get_all_options() + get_custom_tickers()
        selected = st.multiselect(
            "Select",
            options=all_stocks,
            default=st.session_state.get('selected_stocks', []),
            label_visibility="collapsed"
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
        
        new_stock = st.text_input("Add custom", placeholder="e.g. WIPRO", label_visibility="collapsed")
        if st.button("Add", use_container_width=True):
            if new_stock:
                ticker = new_stock.upper().strip()
                if add_custom_ticker(ticker):
                    st.session_state.selected_stocks = list(st.session_state.get('selected_stocks', [])) + [ticker]
                    st.success(f"Added {ticker}")
                    st.rerun()
        
        st.markdown('<div class="section-title">Parameters</div>', unsafe_allow_html=True)
        
        instrument = st.selectbox("Type", ["Equity Options", "Index Options"], label_visibility="collapsed")
        
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input("From", value=date.today() - timedelta(days=30))
        with col2:
            to_date = st.date_input("To", value=date.today())
        
        expiry = st.date_input("Expiry", value=date.today() + timedelta(days=30))
        strike = st.number_input("Strike", min_value=0.0, value=1000.0, step=50.0)
        
        return {
            'selected_stocks': selected,
            'instrument_type': instrument,
            'from_date': from_date,
            'to_date': to_date,
            'expiry_date': expiry,
            'strike_price': strike
        }

def render_metrics(data):
    total = len(data) if data else 0
    processed = sum(1 for df in data.values() if df is not None and not df.empty) if data else 0
    records = sum(len(df) for df in data.values() if df is not None) if data else 0
    rate = int((processed / total * 100)) if total > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total</div>
                <div class="metric-value">{total}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Processed</div>
                <div class="metric-value">{processed}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Records</div>
                <div class="metric-value">{records:,}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Success</div>
                <div class="metric-value">{rate}%</div>
            </div>
        """, unsafe_allow_html=True)

def generate_demo_data(stock, from_date, to_date):
    import random
    dates = pd.date_range(start=from_date, end=to_date, freq='B')
    base = random.uniform(100, 500)
    
    return pd.DataFrame({
        'Date': [d.strftime('%Y-%m-%d') for d in dates],
        'Strike': [1000] * len(dates),
        'Call LTP': [round(base + random.uniform(-20, 20), 2) for _ in dates],
        'Call OI': [random.randint(10000, 100000) for _ in dates],
        'Put LTP': [round(base + random.uniform(-20, 20), 2) for _ in dates],
        'Put OI': [random.randint(10000, 100000) for _ in dates]
    })

def process_stocks(params, progress, status):
    data = {}
    stocks = params['selected_stocks']
    total = len(stocks)
    
    for i, stock in enumerate(stocks):
        progress.progress((i + 1) / total)
        status.text(f"Processing {stock}...")
        
        try:
            df = generate_demo_data(stock, params['from_date'], params['to_date'])
            data[stock] = df
        except:
            data[stock] = pd.DataFrame()
        
        time.sleep(0.1)
    
    return data

def main():
    st.markdown(get_css(), unsafe_allow_html=True)
    
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = {}
    if 'selected_stocks' not in st.session_state:
        st.session_state.selected_stocks = []
    
    params = render_sidebar()
    
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">BSE derivative data analytics</div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
    
    render_metrics(st.session_state.stock_data)
    
    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        fetch_btn = st.button("Fetch Data", use_container_width=True, disabled=len(params['selected_stocks']) == 0)
    
    with col2:
        if st.session_state.stock_data:
            excel = create_multi_stock_excel(st.session_state.stock_data, params['from_date'], params['to_date'])
            filename = generate_multi_stock_filename(list(st.session_state.stock_data.keys()), params['from_date'], params['to_date'])
            st.download_button("Download Excel", excel, filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.button("Download Excel", use_container_width=True, disabled=True)
    
    with col3:
        if st.button("Reset", use_container_width=True):
            st.session_state.stock_data = {}
            st.rerun()
    
    if fetch_btn and params['selected_stocks']:
        progress = st.progress(0)
        status = st.empty()
        
        data = process_stocks(params, progress, status)
        st.session_state.stock_data = data
        
        progress.empty()
        status.empty()
        
        add_history_entry(
            params['selected_stocks'],
            params['from_date'].strftime('%Y-%m-%d'),
            params['to_date'].strftime('%Y-%m-%d'),
            generate_multi_stock_filename(params['selected_stocks'], params['from_date'], params['to_date']),
            "success"
        )
        
        st.success(f"Processed {len(data)} stocks")
        st.rerun()
    
    if st.session_state.stock_data:
        st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
        st.subheader("Data Preview")
        
        tabs = st.tabs(list(st.session_state.stock_data.keys())[:10])
        for tab, (name, df) in zip(tabs, list(st.session_state.stock_data.items())[:10]):
            with tab:
                if df is not None and not df.empty:
                    st.dataframe(df, use_container_width=True, height=300)
                else:
                    st.info(f"No data for {name}")

if __name__ == "__main__":
    main()
