"""
Quantum Market Suite - Services Tests

Property-based tests for exchange router and services.
"""

import pytest
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings
from datetime import date, datetime
import pandas as pd

from quantum.services.exchange_router import ExchangeRouter
from quantum.services.equity_service import EquityService
from quantum.services.derivative_service import DerivativeService
from quantum.models import EquityData, DerivativeData, ValidationResult


class TestExchangeRoutingConsistency:
    """
    **Feature: quantum-market-suite, Property 1: Exchange Routing Consistency**
    **Validates: Requirements 1.2**
    
    For any exchange selection (NSE or BSE), all subsequent data fetching
    operations SHALL use scrapers corresponding to that exchange, and the
    returned data SHALL include the correct exchange identifier.
    """
    
    @given(exchange=st.sampled_from(["NSE", "BSE"]))
    @settings(max_examples=100, deadline=None)
    def test_exchange_routing_uses_correct_scraper(self, exchange: str):
        """Test that router uses correct scraper for selected exchange."""
        router = ExchangeRouter(exchange=exchange)
        
        # Verify exchange is set correctly
        assert router.exchange == exchange
        
        # Get scraper and verify it's for correct exchange
        scraper = router._get_scraper()
        assert scraper.get_exchange_name() == exchange
    
    @given(exchange=st.sampled_from(["NSE", "BSE"]))
    @settings(max_examples=100, deadline=None)
    def test_fetched_data_has_correct_exchange(self, exchange: str):
        """Test that fetched data includes correct exchange identifier."""
        router = ExchangeRouter(exchange=exchange)
        
        # Mock the scraper's get_equity_data
        mock_data = EquityData(
            symbol="TEST",
            exchange=exchange,
            data=pd.DataFrame(),
            fetch_timestamp=datetime.now()
        )
        
        with patch.object(router, '_get_scraper') as mock_get_scraper:
            mock_scraper = MagicMock()
            mock_scraper.get_equity_data.return_value = mock_data
            mock_get_scraper.return_value = mock_scraper
            
            result = router.get_equity_data("TEST", date(2024, 1, 1), date(2024, 1, 31))
            
            assert result.exchange == exchange


class TestExchangeSwitchStateReset:
    """
    **Feature: quantum-market-suite, Property 2: Exchange Switch State Reset**
    **Validates: Requirements 1.3**
    
    For any exchange change event, the application state SHALL clear all
    previously loaded equity and derivative data, resulting in empty data
    containers.
    """
    
    @given(
        initial=st.sampled_from(["NSE", "BSE"]),
        new=st.sampled_from(["NSE", "BSE"])
    )
    @settings(max_examples=100, deadline=None)
    def test_exchange_switch_clears_data(self, initial: str, new: str):
        """Test that switching exchange clears cached data."""
        router = ExchangeRouter(exchange=initial)
        
        # Add some cached data
        router._cached_data["test_key"] = "test_value"
        assert len(router._cached_data) > 0
        
        # Switch exchange (only clears if different)
        if initial != new:
            router.exchange = new
            assert len(router._cached_data) == 0, "Data should be cleared on exchange switch"
        else:
            router.exchange = new
            # Same exchange, data should remain
            assert len(router._cached_data) > 0
    
    def test_exchange_switch_resets_scraper(self):
        """Test that switching exchange resets the scraper instance."""
        router = ExchangeRouter(exchange="NSE")
        
        # Initialize scraper
        scraper1 = router._get_scraper()
        assert scraper1.get_exchange_name() == "NSE"
        
        # Switch exchange
        router.exchange = "BSE"
        
        # Scraper should be reset
        assert router._scraper is None
        
        # New scraper should be for BSE
        scraper2 = router._get_scraper()
        assert scraper2.get_exchange_name() == "BSE"


class TestEquityDataCompleteness:
    """
    **Feature: quantum-market-suite, Property 3: Equity Data Completeness**
    **Validates: Requirements 2.1, 2.2**
    
    For any valid stock symbol and date range, the returned equity DataFrame
    SHALL contain columns for Date, Open, High, Low, Close, and Volume, with
    all numeric columns containing valid numerical values.
    """
    
    def test_equity_data_has_required_columns(self):
        """Test that equity data contains all required columns."""
        # Create mock equity data with required columns
        df = pd.DataFrame({
            "Date": ["2024-01-15", "2024-01-16"],
            "Open": [100.0, 103.0],
            "High": [105.0, 108.0],
            "Low": [98.0, 102.0],
            "Close": [103.0, 107.0],
            "Volume": [1000000, 1200000]
        })
        
        data = EquityData(
            symbol="TEST",
            exchange="NSE",
            data=df,
            fetch_timestamp=datetime.now()
        )
        
        router = ExchangeRouter(exchange="NSE")
        service = EquityService(router)
        
        validation = service.validate_equity_data(data)
        assert validation.is_valid
    
    @given(
        open_val=st.floats(min_value=0.01, max_value=10000),
        high_val=st.floats(min_value=0.01, max_value=10000),
        low_val=st.floats(min_value=0.01, max_value=10000),
        close_val=st.floats(min_value=0.01, max_value=10000),
        volume=st.integers(min_value=0, max_value=1000000000)
    )
    @settings(max_examples=100, deadline=None)
    def test_equity_numeric_values_valid(self, open_val, high_val, low_val, close_val, volume):
        """Test that numeric columns contain valid values."""
        df = pd.DataFrame({
            "Date": ["2024-01-15"],
            "Open": [open_val],
            "High": [high_val],
            "Low": [low_val],
            "Close": [close_val],
            "Volume": [volume]
        })
        
        data = EquityData(
            symbol="TEST",
            exchange="NSE",
            data=df,
            fetch_timestamp=datetime.now()
        )
        
        router = ExchangeRouter(exchange="NSE")
        service = EquityService(router)
        
        validation = service.validate_equity_data(data)
        assert validation.is_valid


class TestDerivativeDataStructure:
    """
    **Feature: quantum-market-suite, Property 4: Derivative Data Structure**
    **Validates: Requirements 3.1, 3.2, 3.3**
    
    For any valid derivative data request, the returned data SHALL contain
    separate Call and Put DataFrames, each with columns for Strike, Open,
    High, Low, Close, Open Interest, and Volume, plus expiry date and
    contract type metadata.
    """
    
    def test_derivative_data_has_separate_call_put(self):
        """Test that derivative data has separate Call and Put DataFrames."""
        calls_df = pd.DataFrame({
            "Strike": [2400, 2450],
            "Open": [50.0, 45.0],
            "High": [55.0, 50.0],
            "Low": [48.0, 43.0],
            "Close": [52.0, 47.0],
            "OI": [10000, 8000],
            "Volume": [5000, 4000],
            "Expiry": ["25-Jan-2024", "25-Jan-2024"],
            "Type": ["CE", "CE"]
        })
        
        puts_df = pd.DataFrame({
            "Strike": [2400, 2450],
            "Open": [30.0, 35.0],
            "High": [35.0, 40.0],
            "Low": [28.0, 33.0],
            "Close": [32.0, 37.0],
            "OI": [8000, 9000],
            "Volume": [4000, 4500],
            "Expiry": ["25-Jan-2024", "25-Jan-2024"],
            "Type": ["PE", "PE"]
        })
        
        data = DerivativeData(
            symbol="TEST",
            exchange="NSE",
            expiry=date(2024, 1, 25),
            calls=calls_df,
            puts=puts_df,
            futures=pd.DataFrame(),
            fetch_timestamp=datetime.now()
        )
        
        router = ExchangeRouter(exchange="NSE")
        service = DerivativeService(router)
        
        calls, puts = service.get_call_put_split(data)
        
        assert len(calls) == 2
        assert len(puts) == 2
        assert all(calls["Type"] == "CE")
        assert all(puts["Type"] == "PE")
    
    def test_derivative_data_has_required_columns(self):
        """Test that derivative data has required columns."""
        calls_df = pd.DataFrame({
            "Strike": [2400],
            "Open": [50.0],
            "High": [55.0],
            "Low": [48.0],
            "Close": [52.0],
            "OI": [10000],
            "Volume": [5000],
            "Expiry": ["25-Jan-2024"],
            "Type": ["CE"]
        })
        
        data = DerivativeData(
            symbol="TEST",
            exchange="NSE",
            expiry=date(2024, 1, 25),
            calls=calls_df,
            puts=pd.DataFrame(),
            futures=pd.DataFrame(),
            fetch_timestamp=datetime.now()
        )
        
        router = ExchangeRouter(exchange="NSE")
        service = DerivativeService(router)
        
        validation = service.validate_derivative_data(data)
        assert validation.is_valid


class TestDateRangeValidation:
    """
    **Feature: quantum-market-suite, Property 12: Date Range Validation**
    **Validates: Requirements 9.4**
    
    For any date range where end_date is before start_date, the validation
    function SHALL return an invalid result with an appropriate error message.
    """
    
    @given(
        start=st.dates(min_value=date(2020, 1, 1), max_value=date(2025, 12, 31)),
        days_before=st.integers(min_value=1, max_value=365)
    )
    @settings(max_examples=100, deadline=None)
    def test_end_before_start_is_invalid(self, start: date, days_before: int):
        """Test that end date before start date is invalid."""
        from datetime import timedelta
        end = start - timedelta(days=days_before)
        
        router = ExchangeRouter(exchange="NSE")
        service = EquityService(router)
        
        result = service.validate_date_range(start, end)
        
        assert not result.is_valid
        assert result.error_message is not None
        assert "before" in result.error_message.lower() or "cannot" in result.error_message.lower()
    
    @given(
        start=st.dates(min_value=date(2020, 1, 1), max_value=date(2024, 12, 31)),
        days_after=st.integers(min_value=0, max_value=365)
    )
    @settings(max_examples=100, deadline=None)
    def test_valid_date_range(self, start: date, days_after: int):
        """Test that valid date ranges pass validation."""
        from datetime import timedelta
        end = start + timedelta(days=days_after)
        
        # Skip if end is in future or range too large
        if end > date.today() or days_after > 730:
            return
        
        router = ExchangeRouter(exchange="NSE")
        service = EquityService(router)
        
        result = service.validate_date_range(start, end)
        
        assert result.is_valid
