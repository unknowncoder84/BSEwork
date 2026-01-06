"""
Quantum Market Suite - Persistence Manager

Handles JSON-based local storage for user configuration, notepad,
search history, and theme preferences.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from quantum.models import Config, SearchHistoryEntry


class PersistenceManager:
    """Manages persistent storage using JSON files."""
    
    CONFIG_PATH = "config.json"  # Default to config.json for long-term persistence
    MAX_SEARCH_HISTORY = 10
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize persistence manager with optional custom config path."""
        self.config_path = config_path or self.CONFIG_PATH
        self._config: Optional[Config] = None
    
    def load_config(self) -> Config:
        """Load configuration from JSON file. Creates default if not exists."""
        if self._config is not None:
            return self._config
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._config = Config.from_dict(data)
            else:
                self._config = Config()
                self.save_config(self._config)
        except json.JSONDecodeError:
            self._backup_corrupt_config()
            self._config = Config()
            self.save_config(self._config)
        except Exception:
            self._config = Config()
        
        return self._config

    def save_config(self, config: Config) -> None:
        """Save configuration to JSON file."""
        self._config = config
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
        except PermissionError:
            pass  # Silently fail, use in-memory config
    
    def _backup_corrupt_config(self) -> None:
        """Backup corrupt config file before creating new one."""
        if os.path.exists(self.config_path):
            backup_path = f"{self.config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                shutil.copy2(self.config_path, backup_path)
            except Exception:
                pass
    
    def update_notepad(self, content: str) -> None:
        """Update notepad content and save immediately."""
        config = self.load_config()
        config.notepad_content = content
        self.save_config(config)
    
    def get_notepad(self) -> str:
        """Get current notepad content."""
        return self.load_config().notepad_content
    
    def add_search_history(self, entry: SearchHistoryEntry) -> None:
        """Add entry to search history, maintaining max 10 entries."""
        config = self.load_config()
        config.search_history.insert(0, entry)
        if len(config.search_history) > self.MAX_SEARCH_HISTORY:
            config.search_history = config.search_history[:self.MAX_SEARCH_HISTORY]
        self.save_config(config)
    
    def get_search_history(self) -> list:
        """Get search history entries."""
        return self.load_config().search_history
    
    def clear_search_history(self) -> None:
        """Clear all search history."""
        config = self.load_config()
        config.search_history = []
        self.save_config(config)

    def set_theme(self, theme: str) -> None:
        """Save theme preference ('light' or 'dark')."""
        if theme not in ('light', 'dark'):
            theme = 'dark'
        config = self.load_config()
        config.theme = theme
        self.save_config(config)
    
    def get_theme(self) -> str:
        """Get current theme preference."""
        return self.load_config().theme
    
    def set_exchange(self, exchange: str) -> None:
        """Save last used exchange ('NSE' or 'BSE')."""
        if exchange not in ('NSE', 'BSE'):
            exchange = 'NSE'
        config = self.load_config()
        config.last_exchange = exchange
        self.save_config(config)
    
    def get_exchange(self) -> str:
        """Get last used exchange."""
        return self.load_config().last_exchange
    
    def add_export_history(self, filename: str) -> None:
        """Record an export to history."""
        config = self.load_config()
        config.export_history.insert(0, {
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        })
        if len(config.export_history) > 20:
            config.export_history = config.export_history[:20]
        self.save_config(config)
    
    def get_export_history(self) -> list:
        """Get export history."""
        return self.load_config().export_history
    
    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        self._config = Config()
        self.save_config(self._config)
        
    def delete_config_file(self) -> None:
        """Delete the config file (for testing)."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        self._config = None
