"""
Property-based tests for data models and validation.
Feature: bse-derivative-downloader
"""
import pytest
from datetime import date, timedelta
from hypothesis import given, settings, strategies as st

from utils.models import (
    FetchParameters, validate_inputs, all_inputs_provided
)


# Strategies for generating test data
valid_company_names = st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'Pd')))
instrument_types = st.sampled_from(["Equity Options", "Index Options"])
positive_floats = st.floats(min_value=0.01, max_value=100000, allow_nan=False, allow_infinity=False)
valid_dates = st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31))


class TestInputValidation:
    """
    Property 1: Input validation enables action button
    For any set of user inputs, the "Fetch & Merge Data" button should be enabled 
    if and only if all required fields contain valid values.
    Validates: Requirements 1.5
    """
    
    @given(
        company=valid_company_names,
        instrument=instrument_types,
        strike=positive_floats,
        from_date=valid_dates,
        to_date=valid_dates,
        expiry_date=valid_dates
    )
    @settings(max_examples=100)
    def test_valid_inputs_enable_button(self, company, instrument, strike, from_date, to_date, expiry_date):
        """
        Feature: bse-derivative-downloader, Property 1: Input validation enables action button
        Validates: Requirements 1.5
        """
        # Ensure from_date <= to_date
        if from_date > to_date:
            from_date, to_date = to_date, from_date
        
        # Ensure expiry_date >= from_date
        if expiry_date < from_date:
            expiry_date = from_date
        
        # All inputs provided should return True for valid inputs
        result = all_inputs_provided(
            company, instrument, expiry_date, strike, from_date, to_date
        )
        
        # If company is not empty and all other params are valid, should be True
        if company.strip():
            assert result is True
    
    @given(
        instrument=instrument_types,
        strike=positive_floats,
        from_date=valid_dates,
        to_date=valid_dates,
        expiry_date=valid_dates
    )
    @settings(max_examples=100)
    def test_empty_company_disables_button(self, instrument, strike, from_date, to_date, expiry_date):
        """
        Feature: bse-derivative-downloader, Property 1: Input validation enables action button
        Empty company name should disable the button.
        Validates: Requirements 1.5
        """
        # Empty company names
        for empty_company in ["", "   ", None]:
            result = all_inputs_provided(
                empty_company, instrument, expiry_date, strike, from_date, to_date
            )
            assert result is False
    
    @given(
        company=valid_company_names,
        instrument=instrument_types,
        from_date=valid_dates,
        to_date=valid_dates,
        expiry_date=valid_dates
    )
    @settings(max_examples=100)
    def test_invalid_strike_disables_button(self, company, instrument, from_date, to_date, expiry_date):
        """
        Feature: bse-derivative-downloader, Property 1: Input validation enables action button
        Invalid strike price should disable the button.
        Validates: Requirements 1.5
        """
        # Invalid strike prices
        for invalid_strike in [0, -1, -100, None]:
            result = all_inputs_provided(
                company, instrument, expiry_date, invalid_strike, from_date, to_date
            )
            assert result is False


class TestFetchParametersValidation:
    """Additional validation tests for FetchParameters."""
    
    @given(
        company=valid_company_names,
        instrument=instrument_types,
        strike=positive_floats,
        from_date=valid_dates,
        to_date=valid_dates
    )
    @settings(max_examples=100)
    def test_date_range_validation(self, company, instrument, strike, from_date, to_date):
        """
        Test that date range validation works correctly.
        """
        # Ensure company is not empty
        if not company.strip():
            company = "TEST"
        
        expiry_date = max(from_date, to_date)
        
        params = FetchParameters(
            company_name=company,
            instrument_type=instrument,
            expiry_date=expiry_date,
            strike_price=strike,
            from_date=from_date,
            to_date=to_date
        )
        
        is_valid, errors = params.is_valid()
        
        # If from_date > to_date, should be invalid
        if from_date > to_date:
            assert not is_valid
            assert any("From date" in e for e in errors)
        else:
            # Should be valid if all other conditions met
            if company.strip() and strike > 0:
                assert is_valid
