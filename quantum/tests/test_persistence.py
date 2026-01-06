"""
Quantum Market Suite - Persistence Tests

Property-based tests for PersistenceManager using Hypothesis.
"""

import pytest
import os
import tempfile
import uuid
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime, date

from quantum.persistence import PersistenceManager
from quantum.models import Config, SearchHistoryEntry


def get_temp_config_path():
    """Generate a unique temporary config path."""
    return os.path.join(tempfile.gettempdir(), f"quantum_test_{uuid.uuid4().hex}.json")


def cleanup_config(path):
    """Clean up temporary config file."""
    if os.path.exists(path):
        os.remove(path)


# Custom strategies
@st.composite
def search_history_entries(draw):
    """Generate random SearchHistoryEntry objects."""
    symbols = ["RELIANCE", "TCS", "INFY", "HDFC", "ICICI", "SBIN", "BHARTIARTL"]
    exchanges = ["NSE", "BSE"]
    data_types = ["equity", "derivative", "both"]
    
    start = draw(st.dates(min_value=date(2020, 1, 1), max_value=date(2025, 12, 31)))
    end = draw(st.dates(min_value=start, max_value=date(2025, 12, 31)))
    
    return SearchHistoryEntry(
        symbol=draw(st.sampled_from(symbols)),
        exchange=draw(st.sampled_from(exchanges)),
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        timestamp=datetime.now().isoformat(),
        data_type=draw(st.sampled_from(data_types))
    )


class TestSearchHistorySizeInvariant:
    """
    **Feature: quantum-market-suite, Property 9: Search History Size Invariant**
    **Validates: Requirements 6.2**
    
    For any sequence of search history additions, the stored history list
    SHALL never exceed 10 entries, with the most recent entries preserved
    and oldest entries removed.
    """
    
    @given(num_entries=st.integers(min_value=1, max_value=25))
    @settings(max_examples=100)
    def test_history_never_exceeds_max(self, num_entries: int):
        """Test that history never exceeds 10 entries regardless of additions."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            
            for i in range(num_entries):
                entry = SearchHistoryEntry(
                    symbol=f"STOCK{i}",
                    exchange="NSE",
                    start_date="2024-01-01",
                    end_date="2024-01-31",
                    timestamp=datetime.now().isoformat(),
                    data_type="both"
                )
                pm.add_search_history(entry)
            
            history = pm.get_search_history()
            assert len(history) <= 10, f"History exceeded max: {len(history)} entries"
        finally:
            cleanup_config(config_path)
    
    @given(entries=st.lists(search_history_entries(), min_size=1, max_size=20))
    @settings(max_examples=100, deadline=None)
    def test_most_recent_preserved(self, entries):
        """Test that most recent entries are preserved when limit exceeded."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            
            for entry in entries:
                pm.add_search_history(entry)
            
            history = pm.get_search_history()
            
            if len(entries) > 0:
                assert history[0].symbol == entries[-1].symbol
            
            assert len(history) <= 10
        finally:
            cleanup_config(config_path)


class TestSearchHistoryEntryCompleteness:
    """
    **Feature: quantum-market-suite, Property 10: Search History Entry Completeness**
    **Validates: Requirements 6.1**
    
    For any completed data fetch operation, the recorded search history entry
    SHALL contain the symbol, exchange, start date, end date, timestamp, and
    data type fields.
    """
    
    @given(entry=search_history_entries())
    @settings(max_examples=100, deadline=None)
    def test_entry_has_all_required_fields(self, entry: SearchHistoryEntry):
        """Test that saved entries contain all required fields."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            pm.add_search_history(entry)
            history = pm.get_search_history()
            
            assert len(history) >= 1
            saved_entry = history[0]
            
            assert saved_entry.symbol, "Symbol is missing or empty"
            assert saved_entry.exchange in ("NSE", "BSE"), "Exchange is invalid"
            assert saved_entry.start_date, "Start date is missing"
            assert saved_entry.end_date, "End date is missing"
            assert saved_entry.timestamp, "Timestamp is missing"
            assert saved_entry.data_type in ("equity", "derivative", "both")
        finally:
            cleanup_config(config_path)
    
    @given(
        symbol=st.sampled_from(["RELIANCE", "TCS", "INFY"]),
        exchange=st.sampled_from(["NSE", "BSE"]),
        data_type=st.sampled_from(["equity", "derivative", "both"])
    )
    @settings(max_examples=100)
    def test_entry_values_preserved(self, symbol, exchange, data_type):
        """Test that entry values are preserved exactly."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            
            entry = SearchHistoryEntry.create(
                symbol=symbol,
                exchange=exchange,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                data_type=data_type
            )
            
            pm.add_search_history(entry)
            saved = pm.get_search_history()[0]
            
            assert saved.symbol == symbol
            assert saved.exchange == exchange
            assert saved.data_type == data_type
        finally:
            cleanup_config(config_path)


class TestThemePersistence:
    """
    **Feature: quantum-market-suite, Property 11: Theme Persistence**
    **Validates: Requirements 7.2, 7.3**
    
    For any theme change operation, the config.json file SHALL immediately
    reflect the new theme value, and subsequent application loads SHALL
    restore that theme.
    """
    
    @given(theme=st.sampled_from(["light", "dark"]))
    @settings(max_examples=100)
    def test_theme_persists_across_reload(self, theme: str):
        """Test that theme preference survives reload."""
        config_path = get_temp_config_path()
        try:
            pm1 = PersistenceManager(config_path=config_path)
            pm1.set_theme(theme)
            
            pm2 = PersistenceManager(config_path=config_path)
            restored_theme = pm2.get_theme()
            
            assert restored_theme == theme
        finally:
            cleanup_config(config_path)
    
    @given(themes=st.lists(st.sampled_from(["light", "dark"]), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_theme_changes_saved_immediately(self, themes):
        """Test that each theme change is saved immediately."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            
            for theme in themes:
                pm.set_theme(theme)
                pm_check = PersistenceManager(config_path=config_path)
                assert pm_check.get_theme() == theme
        finally:
            cleanup_config(config_path)
    
    def test_default_theme_is_dark(self):
        """Test that default theme is dark when no preference exists."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            assert pm.get_theme() == "dark"
        finally:
            cleanup_config(config_path)
    
    @given(invalid_theme=st.text(min_size=1, max_size=20).filter(lambda x: x not in ("light", "dark")))
    @settings(max_examples=50, deadline=None)
    def test_invalid_theme_defaults_to_dark(self, invalid_theme):
        """Test that invalid theme values default to dark."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            pm.set_theme(invalid_theme)
            assert pm.get_theme() == "dark"
        finally:
            cleanup_config(config_path)
