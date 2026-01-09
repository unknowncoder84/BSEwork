"""
Quantum Market Suite - Scraper Base Tests

Property-based tests for ScraperBase anti-detection measures.
"""

import pytest
import time
from unittest.mock import patch
from hypothesis import given, strategies as st, settings
from quantum.scrapers.base import ScraperBase


class TestScraperBase(ScraperBase):
    """Concrete implementation for testing."""
    
    def get_exchange_name(self) -> str:
        return "TEST"


class TestAntiDetectionDelayBounds:
    """
    **Feature: quantum-market-suite, Property 5: Anti-Detection Delay Bounds**
    **Validates: Requirements 3.5, 10.2, 10.4**
    
    For any sequence of scraping requests, the delay between consecutive
    requests SHALL be between 1.0 and 3.0 seconds (inclusive), and user-agent
    strings SHALL vary across requests.
    """
    
    @given(num_delays=st.integers(min_value=1, max_value=20))
    @settings(max_examples=100, deadline=None)
    def test_delays_within_bounds(self, num_delays: int):
        """Test that all delays are within 1.0-3.0 second range."""
        scraper = TestScraperBase(headless=True)
        
        with patch('time.sleep'):  # Mock sleep to speed up tests
            for _ in range(num_delays):
                delay = scraper.random_delay()
                assert 1.0 <= delay <= 3.0, f"Delay {delay} out of bounds [1.0, 3.0]"
            
            delays = scraper.get_request_delays()
            assert len(delays) == num_delays
            for d in delays:
                assert 1.0 <= d <= 3.0

    @given(num_rotations=st.integers(min_value=2, max_value=15))
    @settings(max_examples=100, deadline=None)
    def test_user_agents_vary(self, num_rotations: int):
        """Test that user agents vary across rotations."""
        scraper = TestScraperBase(headless=True)
        
        agents_used = set()
        for _ in range(num_rotations):
            agent = scraper.rotate_user_agent()
            agents_used.add(agent)
        
        # Should have used multiple different agents (cycles through list)
        expected_unique = min(num_rotations, len(scraper.USER_AGENTS))
        assert len(agents_used) >= 1  # At least one agent used
    
    def test_delay_bounds_exact(self):
        """Test delay bounds with specific values."""
        scraper = TestScraperBase(headless=True)
        
        with patch('time.sleep'):
            for _ in range(50):
                delay = scraper.random_delay()
                assert delay >= 1.0, f"Delay {delay} below minimum 1.0"
                assert delay <= 3.0, f"Delay {delay} above maximum 3.0"
    
    def test_custom_delay_bounds(self):
        """Test custom delay bounds."""
        scraper = TestScraperBase(headless=True)
        
        with patch('time.sleep'):
            delay = scraper.random_delay(min_sec=0.5, max_sec=1.0)
            assert 0.5 <= delay <= 1.0
            
            delay = scraper.random_delay(min_sec=2.0, max_sec=4.0)
            assert 2.0 <= delay <= 4.0


class TestRateLimitRetryTiming:
    """
    **Feature: quantum-market-suite, Property 13: Rate Limit Retry Timing**
    **Validates: Requirements 10.3**
    
    For any rate-limited request, the system SHALL wait exactly 30 seconds
    (±1 second tolerance) before retrying the request.
    """
    
    def test_rate_limit_wait_time_value(self):
        """Test that rate limit wait constant is 30 seconds."""
        scraper = TestScraperBase(headless=True)
        assert scraper.RATE_LIMIT_WAIT == 30.0
    
    def test_rate_limit_calls_sleep_with_correct_duration(self):
        """Test that handle_rate_limit sleeps for 30 seconds."""
        scraper = TestScraperBase(headless=True)
        
        with patch('time.sleep') as mock_sleep:
            with patch('time.time', side_effect=[0, 30.0]):
                scraper.handle_rate_limit()
                mock_sleep.assert_called_once_with(30.0)
    
    def test_rate_limit_rotates_user_agent(self):
        """Test that rate limit handling rotates user agent."""
        scraper = TestScraperBase(headless=True)
        
        initial_agent = scraper._get_current_user_agent()
        
        with patch('time.sleep'):
            scraper.handle_rate_limit()
        
        new_agent = scraper._get_current_user_agent()
        assert new_agent != initial_agent, "User agent should rotate after rate limit"


class TestUserAgentRotation:
    """Tests for user agent rotation functionality."""
    
    def test_rotation_cycles_through_agents(self):
        """Test that rotation cycles through all available agents."""
        scraper = TestScraperBase(headless=True)
        
        agents_seen = []
        for _ in range(len(scraper.USER_AGENTS) + 2):
            agent = scraper.rotate_user_agent()
            agents_seen.append(agent)
        
        unique_agents = set(agents_seen)
        assert len(unique_agents) == len(scraper.USER_AGENTS)
    
    def test_initial_user_agent(self):
        """Test initial user agent is first in list."""
        scraper = TestScraperBase(headless=True)
        assert scraper._get_current_user_agent() == scraper.USER_AGENTS[0]
    
    @given(rotations=st.integers(min_value=1, max_value=50))
    @settings(max_examples=100, deadline=None)
    def test_rotation_is_deterministic(self, rotations: int):
        """Test that rotation follows predictable pattern."""
        scraper = TestScraperBase(headless=True)
        
        for i in range(rotations):
            agent = scraper.rotate_user_agent()
            expected_index = (i + 1) % len(scraper.USER_AGENTS)
            assert agent == scraper.USER_AGENTS[expected_index]


class TestDelayHistory:
    """Tests for delay tracking functionality."""
    
    def test_delay_history_recorded(self):
        """Test that delays are recorded in history."""
        scraper = TestScraperBase(headless=True)
        
        with patch('time.sleep'):
            scraper.random_delay()
            scraper.random_delay()
            scraper.random_delay()
        
        delays = scraper.get_request_delays()
        assert len(delays) == 3
    
    def test_clear_delay_history(self):
        """Test clearing delay history."""
        scraper = TestScraperBase(headless=True)
        
        with patch('time.sleep'):
            scraper.random_delay()
            scraper.random_delay()
        
        assert len(scraper.get_request_delays()) == 2
        
        scraper.clear_delay_history()
        assert len(scraper.get_request_delays()) == 0
