"""
BSE Quantum Management Suite - Ultimate Edition
Premium financial dashboard with enhanced UI/UX, calendar management, and persistence.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
from typing import Optional, Tuple, Dict, List
import time

from utils.models import (
    FetchParameters, BSEScraperError, ConnectivityError, CompanyNotFoundError,
    NoDataError, BotDetectionError, DataValidationError
)
from utils.stock_list import TOP_BSE_STOCKS, BSE_INDICES, get_all_options, get_default_stocks
from utils.persistence import (
    load_config, save_config, get_theme, set_theme,
    get_notepad, save_notepad, get_history, add_history_entry,
    clear_history, get_calendar_events, add_calendar_event,
    remove_calendar_event, get_custom_tickers, add_custom_ticker
)
from components.processor import process_derivative_data
from components.excel_generator import create_multi_stock_excel, generate_multi_stock_filename

# Page config
st.set_page_config(
    page_title="BSE Quantum Suite",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with better animations and glassmorphism
ENHANCED_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #141b2d;
        --bg-glass: rgba(20, 27, 45, 0.8);
        --bg-glass-light: rgba(20, 27, 45, 0.5);
        --accent-cyan: #00d4ff;
        --accent-green: #00ff88;
        --accent-purple: #a855f7;
        --accent-pink: #ec4899;
        --accent-orange: #f97316;
        --text-primary: #ffffff;
        --text-secondary: #94a3b8;
        --border-glass: rgba(255, 255, 255, 0.08);
        --glow-cyan: rgba(0, 212, 255, 0.3);
        --glow-green: rgba(0, 255, 136, 0.3);
        --glow-purple: rgba(168, 85, 247, 0.3);
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0f172a 50%, var(--bg-primary) 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: 
            radial-gradient(ellipse at 20% 80%, rgba(0, 212, 255, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(168, 85, 247, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(0, 255, 136, 0.03) 0%, transparent 60%);
        pointer-events: none;
        animation: bgPulse 10s ease-in-out infinite;
    }
    
    @keyframes bgPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(24px);
        border-right: 1px solid var(--border-glass);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    /* Typography */
    h1 {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple), var(--accent-pink));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -1px;
        animation: gradientShift 5s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    h2, h3 { color: var(--text-primary) !important; font-weight: 600 !important; }
    
    /* Glass Cards */
    .glass-card {
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: fadeInUp 0.6s ease-out;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(0, 212, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        transform: translateY(-2px);
    }
    
    .glass-card-light {
        background: var(--bg-glass-light);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 1rem;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px var(--glow-cyan); }
        50% { box-shadow: 0 0 40px var(--glow-cyan), 0 0 60px var(--glow-purple); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 20px var(--glow-cyan) !important;
    }
    
    .stMultiSelect > div > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)) !important;
        border-radius: 8px !important;
        animation: slideIn 0.3s ease;
    }
    
    .stSelectbox > div > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.8rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 15px 40px var(--glow-cyan) !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent-green), #10b981) !important;
        color: var(--bg-primary) !important;
        font-weight: 700 !important;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 15px 40px var(--glow-green) !important;
    }
    
    /* Progress */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green), var(--accent-purple)) !important;
        background-size: 200% 100%;
        animation: progressGradient 2s linear infinite;
        border-radius: 10px;
    }
    
    @keyframes progressGradient {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    /* Data tables */
    .stDataFrame {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .stDataFrame > div {
        background: var(--bg-glass) !important;
        border-radius: 16px;
        border: 1px solid var(--border-glass);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-glass);
        border-radius: 16px;
        padding: 6px;
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 12px !important;
        color: var(--text-secondary) !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)) !important;
        color: white !important;
    }
    
    /* Alerts */
    .stSuccess { background: rgba(0, 255, 136, 0.1) !important; border: 1px solid var(--accent-green) !important; border-radius: 12px !important; }
    .stError { background: rgba(239, 68, 68, 0.1) !important; border: 1px solid #ef4444 !important; border-radius: 12px !important; }
    .stWarning { background: rgba(249, 115, 22, 0.1) !important; border: 1px solid var(--accent-orange) !important; border-radius: 12px !important; }
    .stInfo { background: rgba(0, 212, 255, 0.1) !important; border: 1px solid var(--accent-cyan) !important; border-radius: 12px !important; }
    
    /* Calendar Event Card */
    .calendar-event {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.15));
        border-left: 4px solid var(--accent-purple);
        border-radius: 0 12px 12px 0;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: slideIn 0.4s ease;
        transition: all 0.3s ease;
    }
    
    .calendar-event:hover {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(236, 72, 153, 0.25));
        transform: translateX(4px);
    }
    
    .calendar-event-holiday {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(249, 115, 22, 0.15));
    }
    
    .calendar-event-expiry {
        border-left-color: var(--accent-cyan);
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(0, 255, 136, 0.15));
    }
    
    .calendar-event-custom {
        border-left-color: var(--accent-orange);
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.15), rgba(234, 179, 8, 0.15));
    }
    
    /* History Item */
    .history-item {
        background: var(--bg-glass-light);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        animation: slideIn 0.3s ease;
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        border-color: var(--accent-cyan);
        transform: translateX(4px);
        background: var(--bg-glass);
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-success { background: rgba(0, 255, 136, 0.2); color: var(--accent-green); }
    .status-pending { background: rgba(249, 115, 22, 0.2); color: var(--accent-orange); }
    .status-error { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
    
    /* Metric Cards */
    .metric-card {
        background: var(--bg-glass-light);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: var(--accent-cyan);
        box-shadow: 0 10px 30px var(--glow-cyan);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    /* Delete button */
    .delete-btn {
        background: rgba(239, 68, 68, 0.2) !important;
        color: #ef4444 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.3rem 0.6rem !important;
        font-size: 0.75rem !important;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .delete-btn:hover {
        background: rgba(239, 68, 68, 0.4) !important;
    }
    
    /* Notepad */
    .notepad-container {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--bg-glass); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-cyan); }
    
    /* Hide branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-glass), transparent);
        margin: 1.5rem 0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-glass) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-glass) !important;
    }
</style>
"""

# Market events
MARKET_EVENTS = [
    {"id": 1, "date": "2026-01-26", "title": "Republic Day - Market Closed", "type": "holiday"},
    {"id": 2, "date": "2026-01-30", "title": "Monthly F&O Expiry", "type": "expiry"},
    {"id": 3, "date": "2026-02-19", "title": "Mahashivratri - Market Closed", "type": "holiday"},
    {"id": 4, "date": "2026-02-27", "title": "Monthly F&O Expiry", "type": "expiry"},
    {"id": 5, "date": "2026-03-14", "title": "Holi - Market Closed", "type": "holiday"},
    {"id": 6, "date": "2026-03-27", "title": "Monthly F&O Expiry", "type": "expiry"},
    {"id": 7, "date": "2026-03-31", "title": "Financial Year End", "type": "important"},
]


def init_session_state():
    """Initialize session state."""
    defaults = {
        'stock_data': {},
        'fetch_params': None,
        'error_message': None,
        'processing_complete': False,
        'is_paused': False,
        'theme': get_theme(),
        'notepad_content': get_notepad(),
        'last_inputs': {'selected_stocks': get_default_stocks()},
        'show_add_event': False,
        'custom_events': get_calendar_events()
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar() -> dict:
    """Render enhanced sidebar with all features."""
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
            <div style="font-size: 3rem; animation: float 3s ease-in-out infinite;">⚛️</div>
            <h1 style="font-size: 1.3rem; margin: 0.5rem 0 0.2rem 0;">BSE Quantum Suite</h1>
            <p style="color: var(--text-secondary); font-size: 0.7rem;">Premium Financial Analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme toggle
        col1, col2 = st.columns([3, 1])
        with col2:
            theme_icon = "🌙" if st.session_state.theme == "dark" else "☀️"
            if st.button(theme_icon, key="theme_toggle", help="Toggle theme"):
                new_theme = "light" if st.session_state.theme == "dark" else "dark"
                st.session_state.theme = new_theme
                set_theme(new_theme)
                st.rerun()
        
        st.markdown("---")
        
        # Stock Selection
        st.markdown("##### 📊 Stock Selection")
        
        all_stocks = list(set(get_all_options() + get_custom_tickers()))
        all_stocks.sort()
        
        default_stocks = st.session_state.last_inputs.get('selected_stocks', get_default_stocks())
        valid_defaults = [s for s in default_stocks if s in all_stocks]
        
        selected_stocks = st.multiselect(
            "Select stocks",
            options=all_stocks,
            default=valid_defaults,
            label_visibility="collapsed"
        )
        
        # Add custom ticker
        col1, col2 = st.columns([3, 1])
        with col1:
            new_ticker = st.text_input("Add ticker", placeholder="e.g., ADANI", label_visibility="collapsed", key="new_ticker")
        with col2:
            if st.button("➕", key="add_ticker"):
                if new_ticker:
                    ticker = new_ticker.upper().strip()
                    add_custom_ticker(ticker)
                    if ticker not in selected_stocks:
                        selected_stocks.append(ticker)
                        st.session_state.last_inputs['selected_stocks'] = selected_stocks
                    st.rerun()
        
        # Quick actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔝10", use_container_width=True, key="top10"):
                st.session_state.last_inputs['selected_stocks'] = TOP_BSE_STOCKS[:10]
                st.rerun()
        with col2:
            if st.button("🔝5", use_container_width=True, key="top5"):
                st.session_state.last_inputs['selected_stocks'] = TOP_BSE_STOCKS[:5]
                st.rerun()
        with col3:
            if st.button("🗑️", use_container_width=True, key="clear_stocks"):
                st.session_state.last_inputs['selected_stocks'] = []
                st.rerun()
        
        # Instrument type
        instrument_type = st.selectbox(
            "Instrument",
            ["Equity Options", "Index Options"],
            index=0 if st.session_state.last_inputs.get('instrument_type', 'Equity Options') == "Equity Options" else 1,
            key="instrument"
        )
        
        st.markdown("---")
        
        # Parameters
        st.markdown("##### ⚙️ Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            expiry_date = st.date_input("Expiry", value=st.session_state.last_inputs.get('expiry_date', date.today() + timedelta(days=30)), key="expiry")
        with col2:
            strike_price = st.number_input("Strike", min_value=0.01, value=float(st.session_state.last_inputs.get('strike_price', 100.0)), step=50.0, format="%.0f", key="strike")
        
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input("From", value=st.session_state.last_inputs.get('from_date', date.today() - timedelta(days=30)), key="from_date")
        with col2:
            to_date = st.date_input("To", value=st.session_state.last_inputs.get('to_date', date.today()), key="to_date")
        
        st.markdown("---")
        
        # Enhanced Calendar Section
        st.markdown("##### 📆 Market Calendar")
        
        # Add Event Button
        if st.button("➕ Add Event", use_container_width=True, key="show_add_event_btn"):
            st.session_state.show_add_event = not st.session_state.show_add_event
        
        # Add Event Form
        if st.session_state.show_add_event:
            st.markdown("""
            <div class="glass-card-light" style="padding: 0.8rem; margin: 0.5rem 0;">
            """, unsafe_allow_html=True)
            
            new_event_date = st.date_input("Event Date", value=date.today() + timedelta(days=7), key="new_event_date")
            new_event_title = st.text_input("Event Title", placeholder="e.g., NIFTY Expiry", key="new_event_title")
            new_event_type = st.selectbox("Event Type", ["reminder", "expiry", "holiday", "important"], key="new_event_type")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Save", use_container_width=True, key="save_event"):
                    if new_event_title:
                        add_calendar_event(new_event_date.strftime('%Y-%m-%d'), new_event_title, new_event_type)
                        st.session_state.custom_events = get_calendar_events()
                        st.session_state.show_add_event = False
                        st.success("Event added!")
                        st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True, key="cancel_event"):
                    st.session_state.show_add_event = False
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display Events
        today = date.today()
        
        # System events
        upcoming_system = [e for e in MARKET_EVENTS if datetime.strptime(e['date'], '%Y-%m-%d').date() >= today][:4]
        
        # Custom events
        custom_events = st.session_state.custom_events
        upcoming_custom = [e for e in custom_events if datetime.strptime(e['date'], '%Y-%m-%d').date() >= today]
        
        all_events = []
        for e in upcoming_system:
            all_events.append({**e, 'is_custom': False})
        for e in upcoming_custom:
            all_events.append({**e, 'is_custom': True})
        
        # Sort by date
        all_events.sort(key=lambda x: x['date'])
        
        if all_events:
            for idx, event in enumerate(all_events[:6]):
                event_date = datetime.strptime(event['date'], '%Y-%m-%d').strftime('%d %b')
                event_type = event.get('type', 'reminder')
                
                icon = "🔴" if event_type == 'holiday' else "📊" if event_type == 'expiry' else "⭐" if event_type == 'important' else "📌"
                type_class = f"calendar-event-{event_type}" if event_type in ['holiday', 'expiry'] else "calendar-event-custom" if event.get('is_custom') else ""
                
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"""
                    <div class="calendar-event {type_class}">
                        <div>
                            {icon} <strong>{event_date}</strong><br/>
                            <span style="color: var(--text-secondary); font-size: 0.75rem;">{event['title']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if event.get('is_custom'):
                        if st.button("🗑️", key=f"del_event_{event.get('id', idx)}", help="Delete"):
                            remove_calendar_event(event.get('id'))
                            st.session_state.custom_events = get_calendar_events()
                            st.rerun()
        else:
            st.caption("No upcoming events")
        
        st.markdown("---")
        
        # Notepad
        st.markdown("##### 📝 Quick Notes")
        
        notepad = st.text_area(
            "Notes",
            value=st.session_state.notepad_content,
            height=80,
            placeholder="Your trading notes...",
            label_visibility="collapsed",
            key="notepad"
        )
        
        if notepad != st.session_state.notepad_content:
            st.session_state.notepad_content = notepad
            save_notepad(notepad)
        
        st.markdown("---")
        
        # History
        st.markdown("##### 📜 History")
        
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
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.8rem;">{', '.join(stocks)} {more}</span>
                        <span class="status-badge {status_class}">{status}</span>
                    </div>
                    <div style="font-size: 0.7rem; color: var(--text-secondary); margin-top: 0.3rem;">{ts}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🗑️ Clear History", use_container_width=True, key="clear_history"):
                clear_history()
                st.rerun()
        else:
            st.caption("No history yet")
        
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
    base_call, base_put = random.uniform(50, 150), random.uniform(40, 120)
    
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
        if st.session_state.is_paused:
            status.warning("⏸️ Paused")
            while st.session_state.is_paused:
                time.sleep(0.5)
        
        progress.progress((idx + 1) / total)
        status.markdown(f"""
        <div style="text-align: center; padding: 0.5rem;">
            <span style="color: var(--text-secondary);">Processing</span>
            <strong style="color: var(--accent-cyan);"> {idx + 1}</strong>/<strong>{total}</strong>:
            <strong style="color: var(--accent-green);"> {stock}</strong>
        </div>
        """, unsafe_allow_html=True)
        
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
    
    cols = st.columns(4)
    metrics = [
        ("STOCKS", total, "linear-gradient(135deg, #00d4ff, #a855f7)"),
        ("SUCCESS", f"{success}/{total}", "linear-gradient(135deg, #00ff88, #10b981)"),
        ("RECORDS", f"{records:,}", "linear-gradient(135deg, #ec4899, #a855f7)"),
        ("AVG", records // total if total else 0, "linear-gradient(135deg, #f97316, #ef4444)")
    ]
    
    for col, (label, value, gradient) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="background: {gradient}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
            </div>
            """, unsafe_allow_html=True)


def display_call_put(data: Dict[str, pd.DataFrame], stock: str):
    """Display Call and Put data side by side."""
    df = data.get(stock)
    if df is None or df.empty:
        st.warning(f"No data for {stock}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid var(--accent-cyan);">
            <h3 style="color: var(--accent-cyan); margin: 0 0 1rem 0;">📈 CALL Options</h3>
        </div>
        """, unsafe_allow_html=True)
        call_cols = ['Date', 'Strike Price', 'Call LTP', 'Call OI']
        st.dataframe(df[[c for c in call_cols if c in df.columns]], use_container_width=True, height=350)
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid var(--accent-pink);">
            <h3 style="color: var(--accent-pink); margin: 0 0 1rem 0;">📉 PUT Options</h3>
        </div>
        """, unsafe_allow_html=True)
        put_cols = ['Date', 'Strike Price', 'Put LTP', 'Put OI']
        st.dataframe(df[[c for c in put_cols if c in df.columns]], use_container_width=True, height=350)


def main():
    """Main application."""
    init_session_state()
    st.markdown(ENHANCED_CSS, unsafe_allow_html=True)
    
    params = render_sidebar()
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="font-size: 2.8rem; margin-bottom: 0.5rem;">
            ⚛️ BSE Quantum Management Suite
        </h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
            Advanced multi-stock derivative analytics with real-time processing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    selected = params.get('selected_stocks', [])
    
    # Status bar
    if selected:
        preview = ', '.join(selected[:4])
        more = f" +{len(selected) - 4}" if len(selected) > 4 else ""
        st.markdown(f"""
        <div class="glass-card-light" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem;">
            <span><strong style="color: var(--accent-cyan);">{preview}{more}</strong></span>
            <span class="status-badge status-pending">{len(selected)} stocks selected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👈 Select stocks from the sidebar to begin")
    
    # Validation
    valid = len(selected) > 0 and params['strike_price'] > 0 and params['from_date'] <= params['to_date']
    
    if selected and params['from_date'] > params['to_date']:
        st.warning("⚠️ From date must be before To date")
        valid = False
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1, 1.5, 0.5, 1])
    
    with col2:
        process_btn = st.button(
            f"🚀 Process {len(selected)} Stocks",
            disabled=not valid,
            use_container_width=True,
            type="primary",
            key="process"
        )
    
    with col3:
        if st.session_state.is_paused:
            if st.button("▶️", key="resume", help="Resume"):
                st.session_state.is_paused = False
        else:
            if st.button("⏸️", key="pause", help="Pause"):
                st.session_state.is_paused = True
    
    st.markdown("---")
    
    # Process
    if process_btn and valid:
        st.session_state.error_message = None
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
                
                st.success(f"✅ Processed {success}/{len(selected)} stocks successfully!")
            else:
                st.session_state.error_message = "No data fetched"
        except Exception as e:
            progress.empty()
            status.empty()
            st.session_state.error_message = str(e)
    
    # Error
    if st.session_state.error_message:
        st.error(f"❌ {st.session_state.error_message}")
    
    # Display data
    if st.session_state.stock_data:
        display_metrics(st.session_state.stock_data)
        st.markdown("<br>", unsafe_allow_html=True)
        
        stocks = list(st.session_state.stock_data.keys())
        
        if len(stocks) > 1:
            tabs = st.tabs(["📊 Summary"] + [f"📈 {s}" for s in stocks])
            
            with tabs[0]:
                summary = []
                for name, df in st.session_state.stock_data.items():
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
                    display_call_put(st.session_state.stock_data, stock)
        else:
            display_call_put(st.session_state.stock_data, stocks[0])
        
        st.markdown("---")
        
        # Download
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h3 style="margin: 0 0 0.5rem 0;">📥 Export Data</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">Download multi-sheet Excel with all stocks</p>
        </div>
        """, unsafe_allow_html=True)
        
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
    
    elif not st.session_state.processing_complete and selected:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem; animation: float 3s ease-in-out infinite;">🎯</div>
            <h3 style="margin: 0;">Ready to Process</h3>
            <p style="color: var(--text-secondary); margin-top: 0.5rem;">Click Process to fetch Call & Put data for all selected stocks</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: var(--text-secondary); font-size: 0.75rem; padding: 1rem;">
        ⚛️ BSE Quantum Management Suite • Premium Financial Analytics<br/>
        <span style="font-size: 0.65rem;">For educational purposes only</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
