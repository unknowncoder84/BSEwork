"""
Download history management for BSE Derivative Data Downloader.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

HISTORY_FILE = ".download_history.json"
MAX_HISTORY_ITEMS = 5


def get_history_path() -> Path:
    """Get path to history file."""
    return Path(HISTORY_FILE)


def load_history() -> List[Dict]:
    """Load download history from file."""
    history_path = get_history_path()
    
    if not history_path.exists():
        return []
    
    try:
        with open(history_path, 'r') as f:
            history = json.load(f)
            return history[-MAX_HISTORY_ITEMS:]  # Keep only last N items
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history: List[Dict]) -> None:
    """Save download history to file."""
    history_path = get_history_path()
    
    # Keep only last N items
    history = history[-MAX_HISTORY_ITEMS:]
    
    try:
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2, default=str)
    except IOError:
        pass  # Silently fail if can't write


def add_to_history(stocks: List[str], from_date: str, to_date: str, 
                   filename: str, success: bool = True) -> None:
    """Add a download record to history."""
    history = load_history()
    
    record = {
        'timestamp': datetime.now().isoformat(),
        'stocks': stocks,
        'stock_count': len(stocks),
        'from_date': from_date,
        'to_date': to_date,
        'filename': filename,
        'success': success
    }
    
    history.append(record)
    save_history(history)


def get_recent_downloads() -> List[Dict]:
    """Get recent successful downloads."""
    history = load_history()
    return [h for h in history if h.get('success', True)][-MAX_HISTORY_ITEMS:]


def format_history_item(item: Dict) -> str:
    """Format a history item for display."""
    timestamp = datetime.fromisoformat(item['timestamp'])
    time_str = timestamp.strftime("%d %b %Y, %H:%M")
    stocks = item.get('stocks', [])
    stock_count = item.get('stock_count', len(stocks))
    
    if stock_count <= 3:
        stock_str = ", ".join(stocks)
    else:
        stock_str = f"{stocks[0]}, {stocks[1]} +{stock_count - 2} more"
    
    return f"📁 {stock_str} ({time_str})"


def clear_history() -> None:
    """Clear all download history."""
    history_path = get_history_path()
    if history_path.exists():
        os.remove(history_path)
