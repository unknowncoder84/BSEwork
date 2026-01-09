"""
Quantum Market Suite - Model Tests

Property-based tests for data models using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, date

from quantum.models import (
    Config,
    SearchHistoryEntry,
    ValidationResult,
)


# Custom strategies for generating test data
@st.composite
def search_history_entries(draw):
    """Generate random SearchHistoryEntry objects."""
    symbols = ["RELIANCE", "TCS", "INFY", "HDFC", "ICICI", "SBIN", "BHARTIARTL"]
    exchanges = ["NSE", "BSE"]
    data_types = ["equity", "derivative", "both"]
    
    # Generate valid date range
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


@st.composite
def config_objects(draw):
    """Generate random Config objects with various content."""
    # Generate notepad content with various formatting
    notepad = draw(st.text(
        alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'Z'),
            whitelist_characters='\n\t'
        ),
        min_size=0,
        max_size=1000
    ))
    
    # Generate search history (0-10 entries)
    history_count = draw(st.integers(min_value=0, max_value=10))
    history = [draw(search_history_entries()) for _ in range(history_count)]
    
    # Generate theme and exchange
    theme = draw(st.sampled_from(["dark", "light"]))
    exchange = draw(st.sampled_from(["NSE", "BSE"]))
    
    # Generate export history
    export_count = draw(st.integers(min_value=0, max_value=5))
    export_history = [
        {
            "filename": f"export_{i}.xlsx",
            "timestamp": datetime.now().isoformat()
        }
        for i in range(export_count)
    ]
    
    return Config(
        notepad_content=notepad,
        search_history=history,
        theme=theme,
        last_exchange=exchange,
        export_history=export_history
    )


class TestConfigRoundTrip:
    """
    **Feature: quantum-market-suite, Property 8: Config Persistence Round-Trip**
    **Validates: Requirements 5.2, 5.3, 7.3**
    
    For any Config object containing notepad content, search history, and theme
    preference, serializing to JSON and deserializing back SHALL produce an
    equivalent Config object with all text formatting preserved.
    """
    
    @given(config=config_objects())
    @settings(max_examples=100)
    def test_config_json_round_trip(self, config: Config):
        """Test that Config survives JSON serialization round-trip."""
        # Serialize to JSON
        json_str = config.to_json()
        
        # Deserialize back
        restored = Config.from_json(json_str)
        
        # Verify all fields match
        assert restored.notepad_content == config.notepad_content, \
            "Notepad content not preserved"
        assert restored.theme == config.theme, \
            "Theme not preserved"
        assert restored.last_exchange == config.last_exchange, \
            "Last exchange not preserved"
        assert len(restored.search_history) == len(config.search_history), \
            "Search history length changed"
        assert len(restored.export_history) == len(config.export_history), \
            "Export history length changed"
        
        # Verify search history entries
        for orig, rest in zip(config.search_history, restored.search_history):
            assert rest.symbol == orig.symbol
            assert rest.exchange == orig.exchange
            assert rest.start_date == orig.start_date
            assert rest.end_date == orig.end_date
            assert rest.data_type == orig.data_type
    
    @given(config=config_objects())
    @settings(max_examples=100)
    def test_config_dict_round_trip(self, config: Config):
        """Test that Config survives dict conversion round-trip."""
        # Convert to dict
        config_dict = config.to_dict()
        
        # Restore from dict
        restored = Config.from_dict(config_dict)
        
        # Verify notepad content with formatting preserved
        assert restored.notepad_content == config.notepad_content, \
            "Notepad content with formatting not preserved"
        assert restored.theme == config.theme
        assert restored.last_exchange == config.last_exchange
    
    @given(notepad_text=st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
        min_size=0,
        max_size=500
    ).filter(lambda x: '\n' in x or '\t' in x or len(x) > 10))
    @settings(max_examples=100)
    def test_notepad_formatting_preserved(self, notepad_text: str):
        """Test that notepad text formatting (newlines, tabs) is preserved."""
        config = Config(notepad_content=notepad_text)
        
        # Round-trip through JSON
        json_str = config.to_json()
        restored = Config.from_json(json_str)
        
        # Verify exact match including whitespace
        assert restored.notepad_content == notepad_text, \
            f"Formatting lost: expected {repr(notepad_text)}, got {repr(restored.notepad_content)}"


class TestSearchHistoryEntry:
    """Tests for SearchHistoryEntry model."""
    
    @given(entry=search_history_entries())
    @settings(max_examples=100)
    def test_entry_dict_round_trip(self, entry: SearchHistoryEntry):
        """Test SearchHistoryEntry survives dict round-trip."""
        entry_dict = entry.to_dict()
        restored = SearchHistoryEntry.from_dict(entry_dict)
        
        assert restored.symbol == entry.symbol
        assert restored.exchange == entry.exchange
        assert restored.start_date == entry.start_date
        assert restored.end_date == entry.end_date
        assert restored.data_type == entry.data_type


class TestValidationResult:
    """Tests for ValidationResult model."""
    
    def test_valid_result(self):
        """Test creating valid result."""
        result = ValidationResult.valid()
        assert result.is_valid is True
        assert result.error_message is None
    
    @given(message=st.text(min_size=1, max_size=200))
    @settings(max_examples=50)
    def test_invalid_result(self, message: str):
        """Test creating invalid result with message."""
        result = ValidationResult.invalid(message)
        assert result.is_valid is False
        assert result.error_message == message
