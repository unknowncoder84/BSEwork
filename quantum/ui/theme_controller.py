"""
Quantum Market Suite - Theme Controller

Manages theme switching and CSS injection for glassmorphism effects.
"""

import streamlit as st
from typing import Optional
from quantum.persistence import PersistenceManager


class ThemeController:
    """Controls theme switching and glassmorphism CSS."""
    
    THEMES = ("dark", "light")
    
    def __init__(self, persistence: Optional[PersistenceManager] = None):
        """Initialize theme controller."""
        self.persistence = persistence or PersistenceManager()
        self._current_theme: Optional[str] = None
    
    def get_current_theme(self) -> str:
        """Get current theme from persistence or session."""
        if self._current_theme:
            return self._current_theme
        
        # Try session state first
        if "theme" in st.session_state:
            return st.session_state.theme
        
        # Fall back to persistence
        return self.persistence.get_theme()
    
    def apply_theme(self, theme: str) -> None:
        """Apply light or dark theme CSS."""
        if theme not in self.THEMES:
            theme = "dark"
        
        self._current_theme = theme
        st.session_state.theme = theme
        self.persistence.set_theme(theme)
        
        css = self.get_glassmorphism_css(theme)
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    def toggle_theme(self) -> str:
        """Toggle between light and dark, return new theme."""
        current = self.get_current_theme()
        new_theme = "light" if current == "dark" else "dark"
        self.apply_theme(new_theme)
        return new_theme

    def get_glassmorphism_css(self, theme: str) -> str:
        """Generate glassmorphism CSS for the specified theme."""
        if theme == "dark":
            return self._get_dark_theme_css()
        else:
            return self._get_light_theme_css()
    
    def _get_dark_theme_css(self) -> str:
        """Get dark theme glassmorphism CSS."""
        return """
        /* Quantum Market Suite - Dark Theme */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --bg-primary: #030303;
            --bg-secondary: #0a0a0f;
            --bg-glass: rgba(15, 15, 25, 0.7);
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent: #818cf8;
            --accent-glow: rgba(129, 140, 248, 0.3);
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --border: rgba(255, 255, 255, 0.1);
        }
        
        .stApp {
            background: linear-gradient(135deg, var(--bg-primary) 0%, #0f0f1a 50%, var(--bg-primary) 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* Glassmorphism panels */
        .stMarkdown, .stDataFrame, .stMetric {
            background: var(--bg-glass) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--bg-secondary) 0%, #05050a 100%);
            border-right: 1px solid var(--border);
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            background: transparent !important;
            border: none;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: var(--text-primary) !important;
            font-weight: 600;
        }
        
        /* Text */
        p, span, label {
            color: var(--text-secondary) !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, var(--accent) 0%, #6366f1 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px var(--accent-glow);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px var(--accent-glow);
        }
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stMultiSelect > div > div {
            background: var(--bg-glass) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
        }
        
        /* DataFrames */
        .dataframe {
            background: transparent !important;
        }
        
        .dataframe th {
            background: var(--accent) !important;
            color: white !important;
        }
        
        .dataframe td {
            background: var(--bg-glass) !important;
            color: var(--text-primary) !important;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: var(--accent) !important;
            font-size: 2rem !important;
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background: var(--accent) !important;
        }
        """

    def _get_light_theme_css(self) -> str:
        """Get light theme glassmorphism CSS."""
        return """
        /* Quantum Market Suite - Light Theme */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --bg-glass: rgba(255, 255, 255, 0.7);
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.2);
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --border: rgba(0, 0, 0, 0.1);
        }
        
        .stApp {
            background: linear-gradient(135deg, var(--bg-primary) 0%, #e2e8f0 50%, var(--bg-primary) 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* Glassmorphism panels */
        .stMarkdown, .stDataFrame, .stMetric {
            background: var(--bg-glass) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--bg-secondary) 0%, #f1f5f9 100%);
            border-right: 1px solid var(--border);
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            background: transparent !important;
            border: none;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: var(--text-primary) !important;
            font-weight: 600;
        }
        
        /* Text */
        p, span, label {
            color: var(--text-secondary) !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, var(--accent) 0%, #4f46e5 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px var(--accent-glow);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px var(--accent-glow);
        }
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stMultiSelect > div > div {
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
        }
        
        /* DataFrames */
        .dataframe th {
            background: var(--accent) !important;
            color: white !important;
        }
        
        .dataframe td {
            background: var(--bg-glass) !important;
            color: var(--text-primary) !important;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: var(--accent) !important;
            font-size: 2rem !important;
        }
        """
