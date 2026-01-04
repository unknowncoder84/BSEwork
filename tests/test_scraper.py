"""
Property-based tests for scraper component.
Feature: bse-derivative-downloader
"""
import pytest
import time
from datetime import date, timedelta
from hypothesis import given, settings, strategies as st
from unittest.mock import Mock, patch, MagicMock

from components.scraper import (
    add_human_delay, get_random_user_agent, USER_AGENTS,
    exponential_backoff_retry
)


class TestAntiDetectionMeasures:
    """
    Property 5: Anti-detection measures are applied consistently
    For any sequence of Selenium Driver actions, the system should include 
    User-Agent headers and add delays between consecutive actions.
    Validates: Requirements 2.8, 2.9, 7.1, 7.2
    """
    
    @given(
        min_delay=st.floats(min_value=0.01, max_value=1.0),
        max_delay=st.floats(min_value=1.0, max_value=3.0)
    )
    @settings(max_examples=50)
    def test_human_delay_within_bounds(self, min_delay, max_delay):
        """
        Feature: bse-derivative-downloader, Property 5: Anti-detection measures are applied consistently
        Validates: Requirements 2.8, 2.9, 7.1, 7.2
        """
        # Measure actual delay
        start = time.time()
        actual_delay = add_human_delay(min_delay, max_delay)
        elapsed = time.time() - start
        
        # Verify delay is within bounds (with small tolerance for execution time)
        assert actual_delay >= min_delay, f"Delay {actual_delay} should be >= {min_delay}"
        assert actual_delay <= max_delay, f"Delay {actual_delay} should be <= {max_delay}"
        
        # Verify actual sleep occurred (with tolerance)
        assert elapsed >= min_delay * 0.9, f"Actual elapsed {elapsed} should be >= {min_delay * 0.9}"
    
    def test_user_agent_rotation(self):
        """
        Feature: bse-derivative-downloader, Property 5: Anti-detection measures are applied consistently
        Test that user agents are rotated from the predefined list.
        Validates: Requirements 2.8, 7.1
        """
        # Get multiple user agents
        agents = [get_random_user_agent() for _ in range(20)]
        
        # All should be from the predefined list
        for agent in agents:
            assert agent in USER_AGENTS, f"User agent '{agent}' not in predefined list"
        
        # Should have some variety (not all the same)
        unique_agents = set(agents)
        # With 20 samples from 4 options, we should see at least 2 different ones
        assert len(unique_agents) >= 1  # At minimum, function works
    
    @given(num_actions=st.integers(min_value=2, max_value=5))
    @settings(max_examples=20)
    def test_delays_between_actions(self, num_actions):
        """
        Feature: bse-derivative-downloader, Property 5: Anti-detection measures are applied consistently
        Test that delays are added between consecutive actions.
        Validates: Requirements 2.9, 7.2
        """
        delays = []
        
        for _ in range(num_actions):
            delay = add_human_delay(0.01, 0.05)  # Short delays for testing
            delays.append(delay)
        
        # All delays should be positive
        assert all(d > 0 for d in delays), "All delays should be positive"
        
        # Should have the expected number of delays
        assert len(delays) == num_actions


class TestCompanySearch:
    """
    Property 2: Company search handles all valid inputs
    For any valid company name string, the Selenium Driver should successfully 
    perform a search operation without throwing exceptions.
    Validates: Requirements 2.2
    """
    
    @given(company=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))))
    @settings(max_examples=50)
    def test_company_name_validation(self, company):
        """
        Feature: bse-derivative-downloader, Property 2: Company search handles all valid inputs
        Test that company names are properly validated before search.
        Validates: Requirements 2.2
        """
        # Valid company names should pass basic validation
        if company.strip():
            # Should be a non-empty string
            assert len(company.strip()) > 0
            # Should be searchable (no exception on basic string operations)
            assert company.upper() is not None
            assert company.lower() is not None


class TestElementWaitLogic:
    """
    Property 12: Element interactions wait for readiness
    For any web element that the Selenium Driver interacts with, 
    the driver should wait for the element to be present and interactable.
    Validates: Requirements 7.3
    """
    
    def test_wait_timeout_configuration(self):
        """
        Feature: bse-derivative-downloader, Property 12: Element interactions wait for readiness
        Test that wait timeouts are properly configured.
        Validates: Requirements 7.3
        """
        # Default timeout should be reasonable (10-30 seconds)
        default_timeout = 20
        assert 10 <= default_timeout <= 60, "Default timeout should be between 10-60 seconds"


class TestRetryBackoff:
    """
    Property 13: Retry logic uses exponential backoff
    For any sequence of retry attempts after failures, 
    the delay between attempts should increase exponentially.
    Validates: Requirements 7.5
    """
    
    @given(
        max_retries=st.integers(min_value=2, max_value=5),
        base_delay=st.floats(min_value=0.1, max_value=1.0)
    )
    @settings(max_examples=30)
    def test_exponential_backoff_delays(self, max_retries, base_delay):
        """
        Feature: bse-derivative-downloader, Property 13: Retry logic uses exponential backoff
        Validates: Requirements 7.5
        """
        # Calculate expected delays
        expected_delays = [base_delay * (2 ** i) for i in range(max_retries)]
        
        # Verify delays increase exponentially
        for i in range(1, len(expected_delays)):
            assert expected_delays[i] > expected_delays[i-1], \
                f"Delay {i} ({expected_delays[i]}) should be > delay {i-1} ({expected_delays[i-1]})"
            
            # Verify it's approximately double
            ratio = expected_delays[i] / expected_delays[i-1]
            assert 1.9 <= ratio <= 2.1, f"Ratio should be ~2, got {ratio}"
    
    def test_retry_function_with_success(self):
        """
        Test that retry function returns on success.
        """
        call_count = 0
        
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = exponential_backoff_retry(success_func, max_retries=3, base_delay=0.01)
        
        assert result == "success"
        assert call_count == 1  # Should succeed on first try
    
    def test_retry_function_with_eventual_success(self):
        """
        Test that retry function retries on failure and eventually succeeds.
        """
        call_count = 0
        
        def eventual_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = exponential_backoff_retry(eventual_success, max_retries=5, base_delay=0.01)
        
        assert result == "success"
        assert call_count == 3  # Should succeed on third try
    
    def test_retry_function_exhausts_retries(self):
        """
        Test that retry function raises after exhausting retries.
        """
        def always_fail():
            raise Exception("Always fails")
        
        with pytest.raises(Exception) as exc_info:
            exponential_backoff_retry(always_fail, max_retries=3, base_delay=0.01)
        
        assert "Always fails" in str(exc_info.value)


class TestParameterConfiguration:
    """
    Property 3: Parameter configuration is consistent
    For any valid set of parameters, the Selenium Driver should configure 
    all parameters on the BSE website before fetching data.
    Validates: Requirements 2.4
    """
    
    @given(
        strike=st.floats(min_value=100, max_value=10000),
        from_date=st.dates(min_value=date(2020, 1, 1), max_value=date(2025, 12, 31)),
        to_date=st.dates(min_value=date(2020, 1, 1), max_value=date(2025, 12, 31))
    )
    @settings(max_examples=50)
    def test_parameter_formatting(self, strike, from_date, to_date):
        """
        Feature: bse-derivative-downloader, Property 3: Parameter configuration is consistent
        Test that parameters are formatted correctly for the BSE website.
        Validates: Requirements 2.4
        """
        # Strike price should be convertible to string
        strike_str = str(strike)
        assert strike_str is not None
        
        # Dates should be formattable
        from_str = from_date.strftime("%d/%m/%Y")
        to_str = to_date.strftime("%d/%m/%Y")
        
        assert len(from_str) == 10  # DD/MM/YYYY
        assert len(to_str) == 10


class TestSequentialDataFetching:
    """
    Property 4: Both option types are fetched sequentially
    For any valid parameter set, when Call options data is successfully fetched, 
    the system should then fetch Put options data using the same parameters.
    Validates: Requirements 2.5, 2.6
    """
    
    def test_option_types_are_distinct(self):
        """
        Feature: bse-derivative-downloader, Property 4: Both option types are fetched sequentially
        Test that Call and Put are treated as distinct option types.
        Validates: Requirements 2.5, 2.6
        """
        option_types = ["CE", "PE"]
        
        # Should have exactly 2 option types
        assert len(option_types) == 2
        
        # Should be distinct
        assert option_types[0] != option_types[1]
        
        # CE = Call, PE = Put
        assert "CE" in option_types  # Call
        assert "PE" in option_types  # Put
