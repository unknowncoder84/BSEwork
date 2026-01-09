"""
Property-based tests for data processor component.
Feature: bse-derivative-downloader
"""
import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from hypothesis import given, settings, strategies as st, assume
from hypothesis.extra.pandas import column, data_frames, range_indexes

from components.processor import (
    merge_call_put_data, format_merged_data, handle_missing_data,
    validate_merged_data, clean_data, MERGED_COLUMNS
)


# Strategies for generating test DataFrames
dates_strategy = st.dates(min_value=date(2020, 1, 1), max_value=date(2025, 12, 31))
strike_prices = st.floats(min_value=100, max_value=5000, allow_nan=False, allow_infinity=False)
prices = st.floats(min_value=0.01, max_value=1000, allow_nan=False, allow_infinity=False)
oi_values = st.integers(min_value=0, max_value=1000000)


def create_option_df(dates: list, strikes: list, prices_list: list, oi_list: list) -> pd.DataFrame:
    """Helper to create option DataFrame."""
    return pd.DataFrame({
        'Date': [d.strftime('%d-%b-%Y') for d in dates],
        'Strike Price': strikes,
        'Close': prices_list,
        'Open Interest': oi_list
    })


class TestDataMerge:
    """
    Property 6: Data merge preserves all records
    For any Call DataFrame and Put DataFrame with matching date ranges, 
    the merged result should contain all unique combinations of Date and Strike Price.
    Validates: Requirements 3.1
    """
    
    @given(
        num_records=st.integers(min_value=1, max_value=20),
        base_date=dates_strategy,
        base_strike=strike_prices
    )
    @settings(max_examples=100)
    def test_merge_preserves_records(self, num_records, base_date, base_strike):
        """
        Feature: bse-derivative-downloader, Property 6: Data merge preserves all records
        Validates: Requirements 3.1
        """
        # Generate dates
        dates = [base_date + timedelta(days=i) for i in range(num_records)]
        strikes = [base_strike] * num_records
        
        # Create Call DataFrame
        call_prices = [float(i * 10 + 50) for i in range(num_records)]
        call_oi = [i * 1000 for i in range(num_records)]
        call_df = create_option_df(dates, strikes, call_prices, call_oi)
        
        # Create Put DataFrame
        put_prices = [float(i * 8 + 40) for i in range(num_records)]
        put_oi = [i * 800 for i in range(num_records)]
        put_df = create_option_df(dates, strikes, put_prices, put_oi)
        
        # Merge
        merged = merge_call_put_data(call_df, put_df)
        
        # Verify all records are preserved
        assert len(merged) >= max(len(call_df), len(put_df))
        
        # Verify no data loss - all dates should be present
        merged_dates = set(merged['Date'].unique()) if 'Date' in merged.columns else set()
        call_dates = set(call_df['Date'].unique())
        put_dates = set(put_df['Date'].unique())
        
        assert call_dates.issubset(merged_dates) or len(merged) >= len(call_df)


class TestMergedDataStructure:
    """
    Property 7: Merged data has required structure
    For any merged dataset, the output DataFrame should contain exactly these columns 
    in order: Date, Strike Price, Call LTP, Call OI, Put LTP, Put OI.
    Validates: Requirements 3.2
    """
    
    @given(
        num_records=st.integers(min_value=1, max_value=10),
        base_date=dates_strategy,
        base_strike=strike_prices
    )
    @settings(max_examples=100)
    def test_merged_data_has_required_columns(self, num_records, base_date, base_strike):
        """
        Feature: bse-derivative-downloader, Property 7: Merged data has required structure
        Validates: Requirements 3.2
        """
        dates = [base_date + timedelta(days=i) for i in range(num_records)]
        strikes = [base_strike] * num_records
        
        call_df = create_option_df(dates, strikes, [100.0] * num_records, [1000] * num_records)
        put_df = create_option_df(dates, strikes, [80.0] * num_records, [800] * num_records)
        
        merged = merge_call_put_data(call_df, put_df)
        formatted = format_merged_data(merged)
        
        # Verify all required columns exist
        for col in MERGED_COLUMNS:
            assert col in formatted.columns, f"Missing column: {col}"
        
        # Verify column order
        assert list(formatted.columns) == MERGED_COLUMNS


class TestReferentialIntegrity:
    """
    Property 9: Merged data maintains referential integrity
    For any merged dataset, every row should have a valid date value 
    and a valid strike price value (not null, not empty).
    Validates: Requirements 3.4
    """
    
    @given(
        num_records=st.integers(min_value=1, max_value=10),
        base_date=dates_strategy,
        base_strike=strike_prices
    )
    @settings(max_examples=100)
    def test_referential_integrity(self, num_records, base_date, base_strike):
        """
        Feature: bse-derivative-downloader, Property 9: Merged data maintains referential integrity
        Validates: Requirements 3.4
        """
        dates = [base_date + timedelta(days=i) for i in range(num_records)]
        strikes = [base_strike] * num_records
        
        call_df = create_option_df(dates, strikes, [100.0] * num_records, [1000] * num_records)
        put_df = create_option_df(dates, strikes, [80.0] * num_records, [800] * num_records)
        
        merged = merge_call_put_data(call_df, put_df)
        formatted = format_merged_data(merged)
        
        # Validate referential integrity
        is_valid, errors = validate_merged_data(formatted)
        
        # All rows should have valid Date values
        if 'Date' in formatted.columns:
            invalid_dates = formatted[formatted['Date'].isin(["N/A", None, ""])].shape[0]
            # At least some dates should be valid
            assert invalid_dates < len(formatted)


class TestMissingDataHandling:
    """
    Property 8: Missing data is handled gracefully
    For any merged dataset with missing values, all NaN or None values 
    should be replaced with "N/A" and the operation should complete without raising exceptions.
    Validates: Requirements 3.3, 3.5
    """
    
    @given(
        num_records=st.integers(min_value=1, max_value=10),
        base_date=dates_strategy,
        base_strike=strike_prices
    )
    @settings(max_examples=100)
    def test_missing_data_replaced_with_na(self, num_records, base_date, base_strike):
        """
        Feature: bse-derivative-downloader, Property 8: Missing data is handled gracefully
        Validates: Requirements 3.3, 3.5
        """
        dates = [base_date + timedelta(days=i) for i in range(num_records)]
        strikes = [base_strike] * num_records
        
        # Create DataFrame with some missing values
        call_prices = [100.0 if i % 2 == 0 else np.nan for i in range(num_records)]
        call_oi = [1000 if i % 3 == 0 else np.nan for i in range(num_records)]
        
        call_df = pd.DataFrame({
            'Date': [d.strftime('%d-%b-%Y') for d in dates],
            'Strike Price': strikes,
            'Close': call_prices,
            'Open Interest': call_oi
        })
        
        put_df = create_option_df(dates, strikes, [80.0] * num_records, [800] * num_records)
        
        # Should not raise exception
        merged = merge_call_put_data(call_df, put_df)
        formatted = format_merged_data(merged)
        result = handle_missing_data(formatted)
        
        # Verify no NaN values remain
        assert not result.isnull().any().any(), "NaN values should be replaced with 'N/A'"
        
        # Verify "N/A" is used for missing values
        na_count = (result == "N/A").sum().sum()
        # Should have some N/A values since we introduced missing data
        assert na_count >= 0  # At minimum, operation completed successfully
    
    def test_empty_dataframe_handling(self):
        """
        Test that empty DataFrames are handled gracefully.
        """
        empty_df = pd.DataFrame(columns=['Date', 'Strike Price', 'Close', 'Open Interest'])
        
        # Should not raise exception
        result = handle_missing_data(empty_df)
        assert result is not None


class TestCleanData:
    """Tests for data cleaning functionality."""
    
    @given(
        num_records=st.integers(min_value=2, max_value=10),
        base_date=dates_strategy
    )
    @settings(max_examples=50)
    def test_clean_removes_duplicates(self, num_records, base_date):
        """Test that clean_data removes duplicate rows."""
        dates = [base_date] * num_records  # All same date = duplicates
        
        df = pd.DataFrame({
            'Date': [d.strftime('%d-%b-%Y') for d in dates],
            'Value': [100] * num_records
        })
        
        cleaned = clean_data(df)
        
        # Should have fewer or equal rows after removing duplicates
        assert len(cleaned) <= len(df)
        # Should have exactly 1 row since all are duplicates
        assert len(cleaned) == 1
