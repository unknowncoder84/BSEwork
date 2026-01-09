"""
JSON-based persistence for BSE Quantum Management Suite.
Handles config, notepad, history, and preferences without a database.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "preferences": {
        "theme": "dark",
        "default_stocks": ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"],
        "auto_save": True
    },
    "notepad": {
        "content": "",
        "last_updated": None
    },
    "history": [],
    "calendar_events": [],
    "custom_tickers": [],
    "derivative_params": {
        "year": 2026,
        "expiry_month": "JAN"
    },
    "last_stock": "RELIANCE",
    "last_strike_price": 2500.0
}


def get_config_path() -> Path:
    """Get path to config file."""
    return Path(CONFIG_FILE)


def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    config_path = get_config_path()
    
    if not config_path.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys exist
            merged = DEFAULT_CONFIG.copy()
            for key, value in config.items():
                if isinstance(value, dict) and key in merged:
                    merged[key].update(value)
                else:
                    merged[key] = value
            return merged
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to JSON file."""
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, default=str)
        return True
    except IOError:
        return False


# Theme Management
def get_theme() -> str:
    """Get current theme preference."""
    config = load_config()
    return config.get("preferences", {}).get("theme", "dark")


def set_theme(theme: str) -> bool:
    """Set theme preference (dark/light)."""
    config = load_config()
    if "preferences" not in config:
        config["preferences"] = {}
    config["preferences"]["theme"] = theme
    return save_config(config)


# Notepad Management
def get_notepad() -> str:
    """Get notepad content."""
    config = load_config()
    return config.get("notepad", {}).get("content", "")


def save_notepad(content: str) -> bool:
    """Save notepad content."""
    config = load_config()
    if "notepad" not in config:
        config["notepad"] = {}
    config["notepad"]["content"] = content
    config["notepad"]["last_updated"] = datetime.now().isoformat()
    return save_config(config)


def get_notepad_last_updated() -> Optional[str]:
    """Get last updated timestamp for notepad."""
    config = load_config()
    return config.get("notepad", {}).get("last_updated")


# History Management
def get_history() -> List[Dict]:
    """Get download history."""
    config = load_config()
    return config.get("history", [])


def add_history_entry(stocks: List[str], from_date: str, to_date: str, 
                      filename: str, status: str = "success") -> bool:
    """Add entry to download history."""
    config = load_config()
    
    if "history" not in config:
        config["history"] = []
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "stocks": stocks,
        "stock_count": len(stocks),
        "from_date": from_date,
        "to_date": to_date,
        "filename": filename,
        "status": status
    }
    
    config["history"].insert(0, entry)
    # Keep only last 50 entries
    config["history"] = config["history"][:50]
    
    return save_config(config)


def clear_history() -> bool:
    """Clear all history."""
    config = load_config()
    config["history"] = []
    return save_config(config)


# Calendar Events Management
def get_calendar_events() -> List[Dict]:
    """Get calendar events."""
    config = load_config()
    return config.get("calendar_events", [])


def add_calendar_event(date: str, title: str, event_type: str = "reminder") -> bool:
    """Add calendar event."""
    config = load_config()
    
    if "calendar_events" not in config:
        config["calendar_events"] = []
    
    event = {
        "id": datetime.now().timestamp(),
        "date": date,
        "title": title,
        "type": event_type,
        "created": datetime.now().isoformat()
    }
    
    config["calendar_events"].append(event)
    return save_config(config)


def remove_calendar_event(event_id: float) -> bool:
    """Remove calendar event by ID."""
    config = load_config()
    config["calendar_events"] = [
        e for e in config.get("calendar_events", []) 
        if e.get("id") != event_id
    ]
    return save_config(config)


# Custom Tickers Management
def get_custom_tickers() -> List[str]:
    """Get custom tickers added by user."""
    config = load_config()
    return config.get("custom_tickers", [])


def add_custom_ticker(ticker: str) -> bool:
    """Add custom ticker."""
    config = load_config()
    
    if "custom_tickers" not in config:
        config["custom_tickers"] = []
    
    ticker = ticker.upper().strip()
    if ticker and ticker not in config["custom_tickers"]:
        config["custom_tickers"].append(ticker)
        return save_config(config)
    return False


def remove_custom_ticker(ticker: str) -> bool:
    """Remove custom ticker."""
    config = load_config()
    ticker = ticker.upper().strip()
    if ticker in config.get("custom_tickers", []):
        config["custom_tickers"].remove(ticker)
        return save_config(config)
    return False
