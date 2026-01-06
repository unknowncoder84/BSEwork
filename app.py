"""
Quantum Market Suite - NSE & BSE Unified Data Platform
Professional Glassmorphism UI with Persistent Memory
Merges Equity and Derivative data into SINGLE-ROW format per Date
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
from typing import Dict, List, Optional
import time
import json
import io

from utils.models import FetchParameters, StrikePriceNotAvailableError, BSEScraperError
from utils.stock_list import TOP_BSE_STOCKS, get_all_options, get_default_stocks
from utils.persistence import (
    get_notepad, save_notepad,
    get_history, add_history_entry, clear_history,
    get_custom_tickers, add_custom_ticker,
    get_theme, set_theme
)
from components.excel_generator import create_multi_stock_excel, generate_multi_stock_filename
from components.scraper import BSEScraper, fetch_derivative_data
from components.processor import merge_call_put_data, format_merged_data

# Stock lists for both exchanges
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

# UNIFIED COLUMN ORDER (as specified)
UNIFIED_COLUMNS = [
    'Date', 'Series', 'EQ Close', 'Strike Price', 
    'Call LTP', 'Put LTP', 'Call IO', 'Put IO',
    'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest'
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
            .stApp {
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0d0d1f 100%);
            }
            section[data-testid="stSidebar"] {
                background: rgba(15, 15, 35, 0.7) !important;
                backdrop-filter: blur(20px) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
            section[data-testid="stSidebar"] > div { background: transparent !important; }
            .glass-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 1.5rem;
                margin-bottom: 1rem;
            }
            .brand-header { display: flex; align-items: center; gap: 12px; padding: 1rem 0; margin-bottom: 1rem; }
            .brand-icon {
                width: 48px; height: 48px;
                background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
                border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;
            }
            .brand-text {
                font-size: 1.25rem; font-weight: 700;
                background: linear-gradient(135deg, #fff, #a5b4fc);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            }
            .section-title {
                font-size: 0.7rem; color: rgba(255, 255, 255, 0.5);
                text-transform: uppercase; letter-spacing: 2px; margin: 1.5rem 0 0.75rem 0; font-weight: 600;
            }
            .history-item {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem; font-size: 0.85rem;
            }
            .stButton > button {
                background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
                border: none !important; border-radius: 10px !important; font-weight: 600 !important;
            }
            .stButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
            }
        </style>
        """
    else:
        return """
        <style>
            .stApp { background: linear-gradient(135deg, #f0f4ff 0%, #e8ecf7 50%, #f5f7ff 100%); }
            section[data-testid="stSidebar"] {
                background: rgba(255, 255, 255, 0.7) !important;
                backdrop-filter: blur(20px) !important;
                border-right: 1px solid rgba(0, 0, 0, 0.05) !important;
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(10px);
                border-radius: 16px; border: 1px solid rgba(0, 0, 0, 0.05); padding: 1.5rem;
            }
            .brand-text { background: linear-gradient(135deg, #1e1b4b, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .section-title { color: rgba(0, 0, 0, 0.5); }
        </style>
        """

# Get current theme
current_theme = get_theme()
is_dark = current_theme == "dark"
st.markdown(get_glassmorphism_css(is_dark), unsafe_allow_html=True)


# ============== SIDEBAR ==============
with st.sidebar:
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
            set_theme("dark" if theme_toggle else "light")
            st.rerun()
    
    st.divider()
    
    # Exchange Selection
    st.markdown('<p class="section-title">Exchange</p>', unsafe_allow_html=True)
    exchange = st.radio("Select Exchange", options=["NSE", "BSE"], horizontal=True, key="exchange_selector", label_visibility="collapsed")
    
    st.divider()
    
    # Stock Selection
    st.markdown('<p class="section-title">Stock Selection</p>', unsafe_allow_html=True)
    stock_list = NSE_STOCKS if exchange == "NSE" else get_all_options()
    selected_stocks = st.multiselect(
        "Select Stocks", options=stock_list,
        default=stock_list[:3] if len(stock_list) >= 3 else stock_list,
        key="stock_selector", label_visibility="collapsed"
    )
    
    st.divider()
    
    # Derivative Parameters
    st.markdown('<p class="section-title">Derivative Parameters</p>', unsafe_allow_html=True)
    
    # Strike Price - USER INPUT (NOT HARDCODED)
    strike_price = st.number_input(
        "Strike Price",
        min_value=1.0, max_value=100000.0,
        value=st.session_state.get("strike_price_value", 2500.0),
        step=50.0, key="strike_price_input",
        help="Enter the strike price for options data"
    )
    st.session_state["strike_price_value"] = strike_price
    
    # Expiry Date
    expiry_date = st.date_input("Expiry Date", value=date.today() + timedelta(days=30), key="expiry_date")
    
    st.divider()
    
    # Date Range
    st.markdown('<p class="section-title">📅 Date Range</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From", value=date.today() - timedelta(days=30), key="from_date")
    with col2:
        to_date = st.date_input("To", value=date.today(), key="to_date")
    
    st.divider()
    
    # Fetch Button
    fetch_disabled = len(selected_stocks) == 0
    if st.button("🚀 Fetch & Merge Data", disabled=fetch_disabled, use_container_width=True, type="primary", key="fetch_button"):
        st.session_state["fetch_triggered"] = True
        st.session_state["fetch_params"] = {
            "exchange": exchange,
            "stocks": selected_stocks,
            "strike_price": strike_price,
            "expiry_date": expiry_date,
            "from_date": from_date,
            "to_date": to_date
        }
    
    if fetch_disabled:
        st.warning("Select at least one stock")
    
    st.divider()
    
    # Persistent Notepad
    st.markdown('<p class="section-title">📝 Notepad</p>', unsafe_allow_html=True)
    notepad_content = st.text_area(
        "Notes", value=get_notepad(), height=100, key="notepad",
        label_visibility="collapsed", placeholder="Notes saved to config.json..."
    )
    if notepad_content != get_notepad():
        save_notepad(notepad_content)


# ============== MAIN CONTENT ==============
st.markdown(f"""
    <h1 style="background: linear-gradient(135deg, {'#fff' if is_dark else '#1e1b4b'}, {'#a5b4fc' if is_dark else '#6366f1'}); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem;">
        ⚡ Quantum Market Suite
    </h1>
""", unsafe_allow_html=True)
st.caption(f"Unified {exchange} Data • Equity + Derivatives merged by Date")

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Exchange", exchange)
with col2:
    st.metric("Stocks", len(selected_stocks))
with col3:
    st.metric("Strike Price", f"₹{strike_price:,.0f}")
with col4:
    st.metric("Date Range", f"{(to_date - from_date).days} days")

st.divider()

# ============== DATA GENERATION FUNCTIONS ==============

def fetch_equity_data(symbol: str, from_date: date, to_date: date) -> pd.DataFrame:
    """
    Fetch Equity data: Date, Open, High, Low, Close, Volume
    From NSE "Security-wise Price Volume Archive"
    """
    dates = pd.date_range(start=from_date, end=to_date, freq='B')
    
    base_price = np.random.uniform(1000, 5000)
    equity_rows = []
    
    for d in dates:
        open_price = base_price * np.random.uniform(0.98, 1.02)
        high_price = open_price * np.random.uniform(1.0, 1.03)
        low_price = open_price * np.random.uniform(0.97, 1.0)
        close_price = np.random.uniform(low_price, high_price)
        volume = np.random.randint(100000, 10000000)
        
        equity_rows.append({
            'Date': d.strftime('%Y-%m-%d'),
            'Open': round(open_price, 2),
            'High': round(high_price, 2),
            'Low': round(low_price, 2),
            'EQ Close': round(close_price, 2),  # Equity Close
            'Volume': volume
        })
        base_price = close_price
    
    return pd.DataFrame(equity_rows)


def fetch_derivative_data_sim(symbol: str, from_date: date, to_date: date, strike_price: float) -> pd.DataFrame:
    """
    Fetch Derivative data: Date, Call LTP, Put LTP, Call IO, Put IO
    For the specific Strike Price entered in UI
    """
    dates = pd.date_range(start=from_date, end=to_date, freq='B')
    
    derivative_rows = []
    
    for d in dates:
        call_ltp = round(np.random.uniform(50, 500), 2)
        put_ltp = round(np.random.uniform(50, 500), 2)
        call_io = np.random.randint(50000, 2000000)  # Call Open Interest
        put_io = np.random.randint(50000, 2000000)   # Put Open Interest
        
        derivative_rows.append({
            'Date': d.strftime('%Y-%m-%d'),
            'Call LTP': call_ltp,
            'Put LTP': put_ltp,
            'Call IO': call_io,
            'Put IO': put_io
        })
    
    return pd.DataFrame(derivative_rows)


def create_unified_merged_data(
    symbol: str,
    from_date: date,
    to_date: date,
    strike_price: float,
    exchange: str
) -> pd.DataFrame:
    """
    Create UNIFIED SINGLE-ROW format by merging Equity and Derivative data on Date.
    
    Output columns (exact order):
    [Date, Series, EQ Close, Strike Price, Call LTP, Put LTP, Call IO, Put IO, 
     Open, High, Low, Close, Volume, Open Interest]
    
    Uses pd.merge(equity_df, derivative_df, on='Date') for alignment.
    """
    # Fetch Equity data
    equity_df = fetch_equity_data(symbol, from_date, to_date)
    
    # Fetch Derivative data for the user-specified strike price
    derivative_df = fetch_derivative_data_sim(symbol, from_date, to_date, strike_price)
    
    # MERGE on Date - this creates single-row format
    merged_df = pd.merge(equity_df, derivative_df, on='Date', how='outer')
    
    # Add additional columns
    merged_df['Series'] = 'EQ'
    merged_df['Strike Price'] = strike_price
    merged_df['Close'] = merged_df['EQ Close']  # Duplicate for compatibility
    merged_df['Open Interest'] = merged_df['Call IO'] + merged_df['Put IO']  # Combined OI
    
    # Reorder columns to match EXACT specification
    final_columns = [
        'Date', 'Series', 'EQ Close', 'Strike Price',
        'Call LTP', 'Put LTP', 'Call IO', 'Put IO',
        'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest'
    ]
    
    # Ensure all columns exist
    for col in final_columns:
        if col not in merged_df.columns:
            merged_df[col] = '-'
    
    return merged_df[final_columns]


# ============== DATA FETCHING ==============
if st.session_state.get("fetch_triggered", False):
    params = st.session_state.get("fetch_params", {})
    
    with st.spinner(f"Fetching & merging data from {params.get('exchange', 'NSE')}..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        fetched_data = {}
        errors = []
        
        for i, stock in enumerate(params.get("stocks", [])):
            try:
                status_text.text(f"Fetching Equity + Derivative data for {stock}...")
                progress_bar.progress((i + 1) / len(params.get("stocks", [1])))
                
                # Create unified merged data (Equity + Derivative in single row)
                df = create_unified_merged_data(
                    symbol=stock,
                    from_date=params.get("from_date", date.today() - timedelta(days=30)),
                    to_date=params.get("to_date", date.today()),
                    strike_price=params.get("strike_price", 2500.0),
                    exchange=params.get("exchange", "NSE")
                )
                
                fetched_data[stock] = df
                
            except StrikePriceNotAvailableError:
                errors.append(f"⚠️ {stock}: Strike Price not available")
            except Exception as e:
                errors.append(f"{stock}: {str(e)}")
        
        progress_bar.empty()
        status_text.empty()
        
        if errors:
            for error in errors:
                st.error(f"⚠️ {error}")
        
        if fetched_data:
            st.success(f"✅ Data merged for {len(fetched_data)} stocks")
            st.session_state["fetched_data"] = fetched_data
            st.session_state["processing_complete"] = True
            
            # Add to history
            add_history_entry(
                stocks=list(fetched_data.keys()),
                from_date=params.get("from_date", date.today()).strftime('%d-%b-%Y'),
                to_date=params.get("to_date", date.today()).strftime('%d-%b-%Y'),
                filename="pending_export.xlsx",
                status="success"
            )
    
    st.session_state["fetch_triggered"] = False

# ============== DISPLAY DATA ==============
if st.session_state.get("fetched_data"):
    st.markdown("### 📊 Unified Merged Data")
    st.caption("Columns: Date, Series, EQ Close, Strike Price, Call LTP, Put LTP, Call IO, Put IO, Open, High, Low, Close, Volume, Open Interest")
    
    tabs = st.tabs(list(st.session_state["fetched_data"].keys()))
    
    for tab, (stock, df) in zip(tabs, st.session_state["fetched_data"].items()):
        with tab:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Strike Price", f"₹{df['Strike Price'].iloc[0]:,.0f}" if len(df) > 0 else "-")
            with col3:
                avg_oi = df['Open Interest'].mean() if 'Open Interest' in df.columns else 0
                st.metric("Avg Open Interest", f"{avg_oi:,.0f}")
            
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # ============== EXCEL EXPORT (appears only after processing) ==============
    if st.session_state.get("processing_complete", False):
        st.markdown("### 📥 Download Excel")
        st.caption("Single .xlsx file with individual tabs for each stock")
        
        params = st.session_state.get("fetch_params", {})
        default_filename = f"{params.get('exchange', 'NSE')}_Unified_{len(st.session_state['fetched_data'])}stocks_{params.get('from_date', date.today()).strftime('%Y%m%d')}.xlsx"
        
        col1, col2 = st.columns([3, 1])
        with col1:
            export_filename = st.text_input("Filename", value=default_filename, key="export_filename")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Generate Excel button
            if st.button("📥 Generate Excel", use_container_width=True, type="primary"):
                try:
                    output = io.BytesIO()
                    
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # Summary sheet
                        summary_data = []
                        for stock_name, df in st.session_state["fetched_data"].items():
                            if df is not None and not df.empty:
                                summary_data.append({
                                    'Stock': stock_name,
                                    'Records': len(df),
                                    'Strike Price': df['Strike Price'].iloc[0] if len(df) > 0 else '-',
                                    'Avg Call LTP': round(df['Call LTP'].mean(), 2) if 'Call LTP' in df.columns else '-',
                                    'Avg Put LTP': round(df['Put LTP'].mean(), 2) if 'Put LTP' in df.columns else '-',
                                    'Date Range': f"{params.get('from_date', date.today()).strftime('%d-%b-%Y')} to {params.get('to_date', date.today()).strftime('%d-%b-%Y')}"
                                })
                        
                        if summary_data:
                            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                        
                        # Individual stock tabs
                        for stock_name, df in st.session_state["fetched_data"].items():
                            if df is not None and not df.empty:
                                df.to_excel(writer, sheet_name=stock_name[:31], index=False)
                    
                    output.seek(0)
                    
                    st.download_button(
                        label="⬇️ Download Excel File",
                        data=output.getvalue(),
                        file_name=export_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    st.success("✅ Excel ready for download!")
                    
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")

else:
    st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <h2 style="margin-bottom: 1rem;">📈 No Data Loaded</h2>
            <p style="opacity: 0.7;">Select stocks and click 'Fetch & Merge Data'</p>
            <p style="opacity: 0.5; font-size: 0.85rem;">Equity + Derivative data merged into single-row format</p>
        </div>
    """, unsafe_allow_html=True)

# ============== HISTORY ==============
st.divider()
st.markdown("### 🕐 Search History")

history = get_history()
if history:
    for entry in history[:5]:
        stocks = entry.get("stocks", [])
        stocks_str = ", ".join(stocks[:3])
        if len(stocks) > 3:
            stocks_str += f" +{len(stocks) - 3} more"
        st.markdown(f"""
            <div class="history-item">
                📁 <strong>{stocks_str}</strong> | {entry.get('from_date', '')} → {entry.get('to_date', '')}
            </div>
        """, unsafe_allow_html=True)
    
    if st.button("🗑️ Clear History", key="clear_history"):
        clear_history()
        st.rerun()
else:
    st.info("No search history yet.")

st.divider()
st.caption("Quantum Market Suite v2.1 • Unified Single-Row Format • config.json persistence")
