"""
Quantum Market Suite - NSE Scraper Tests

Unit tests for NSE scraper with mocked responses.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import date, datetime
import pandas as pd

from quantum.scrapers.nse_scraper import NSEScraper
from quantum.scrapers.base import ScrapingError


class TestNSEScraperEquityParsing:
    """Tests for NSE equity data parsing."""
    
    def test_parse_equity_response_valid_data(self):
        """Test parsing valid equity response."""
        scraper = NSEScraper(headless=True)
        
        mock_response = json.dumps({
            "data": [
                {
                    "CH_TIMESTAMP": "2024-01-15",
                    "CH_OPENING_PRICE": 100.0,
                    "CH_TRADE_HIGH_PRICE": 105.0,
                    "CH_TRADE_LOW_PRICE": 98.0,
                    "CH_CLOSING_PRICE": 103.0,
                    "CH_TOT_TRADED_QTY": 1000000
                },
                {
                    "CH_TIMESTAMP": "2024-01-16",
                    "CH_OPENING_PRICE": 103.0,
                    "CH_TRADE_HIGH_PRICE": 108.0,
                    "CH_TRADE_LOW_PRICE": 102.0,
                    "CH_CLOSING_PRICE": 107.0,
                    "CH_TOT_TRADED_QTY": 1200000
                }
            ]
        })
        
        df = scraper._parse_equity_response(mock_response, "RELIANCE")
        
        assert len(df) == 2
        assert list(df.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
        assert df.iloc[0]["Open"] == 100.0
        assert df.iloc[0]["Close"] == 103.0

    def test_parse_equity_response_empty_data(self):
        """Test parsing empty equity response."""
        scraper = NSEScraper(headless=True)
        
        mock_response = json.dumps({"data": []})
        df = scraper._parse_equity_response(mock_response, "RELIANCE")
        
        assert len(df) == 0
        assert list(df.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    
    def test_parse_equity_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        scraper = NSEScraper(headless=True)
        
        df = scraper._parse_equity_response("invalid json", "RELIANCE")
        
        assert len(df) == 0
        assert list(df.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    
    def test_build_equity_url(self):
        """Test equity URL building."""
        scraper = NSEScraper(headless=True)
        
        url = scraper._build_equity_url(
            "RELIANCE",
            date(2024, 1, 1),
            date(2024, 1, 31)
        )
        
        assert "symbol=RELIANCE" in url
        assert "from=01-01-2024" in url
        assert "to=31-01-2024" in url


class TestNSEScraperDerivativeParsing:
    """Tests for NSE derivative data parsing."""
    
    def test_parse_derivative_response_valid_data(self):
        """Test parsing valid derivative response."""
        scraper = NSEScraper(headless=True)
        
        mock_response = json.dumps({
            "records": {
                "expiryDates": ["25-Jan-2024", "29-Feb-2024"],
                "data": [
                    {
                        "CE": {
                            "strikePrice": 2400,
                            "openPrice": 50.0,
                            "highPrice": 55.0,
                            "lowPrice": 48.0,
                            "lastPrice": 52.0,
                            "openInterest": 10000,
                            "totalTradedVolume": 5000,
                            "expiryDate": "25-Jan-2024"
                        },
                        "PE": {
                            "strikePrice": 2400,
                            "openPrice": 30.0,
                            "highPrice": 35.0,
                            "lowPrice": 28.0,
                            "lastPrice": 32.0,
                            "openInterest": 8000,
                            "totalTradedVolume": 4000,
                            "expiryDate": "25-Jan-2024"
                        }
                    }
                ]
            }
        })
        
        calls_df, puts_df, futures_df, expiry = scraper._parse_derivative_response(
            mock_response, "RELIANCE", None
        )
        
        assert len(calls_df) == 1
        assert len(puts_df) == 1
        assert calls_df.iloc[0]["Strike"] == 2400
        assert puts_df.iloc[0]["OI"] == 8000

    def test_parse_derivative_response_empty_data(self):
        """Test parsing empty derivative response."""
        scraper = NSEScraper(headless=True)
        
        mock_response = json.dumps({"records": {"expiryDates": [], "data": []}})
        calls_df, puts_df, futures_df, expiry = scraper._parse_derivative_response(
            mock_response, "RELIANCE", None
        )
        
        assert len(calls_df) == 0
        assert len(puts_df) == 0
    
    def test_parse_derivative_response_invalid_json(self):
        """Test parsing invalid derivative response."""
        scraper = NSEScraper(headless=True)
        
        calls_df, puts_df, futures_df, expiry = scraper._parse_derivative_response(
            "invalid json", "RELIANCE", None
        )
        
        assert len(calls_df) == 0
        assert len(puts_df) == 0


class TestNSEScraperErrorHandling:
    """Tests for NSE scraper error handling."""
    
    def test_get_equity_data_with_mock(self):
        """Test get_equity_data with mocked fetch."""
        scraper = NSEScraper(headless=True)
        
        mock_response = json.dumps({
            "data": [{
                "CH_TIMESTAMP": "2024-01-15",
                "CH_OPENING_PRICE": 100.0,
                "CH_TRADE_HIGH_PRICE": 105.0,
                "CH_TRADE_LOW_PRICE": 98.0,
                "CH_CLOSING_PRICE": 103.0,
                "CH_TOT_TRADED_QTY": 1000000
            }]
        })
        
        with patch.object(scraper, '_init_session'):
            with patch.object(scraper, 'fetch_page', return_value=mock_response):
                result = scraper.get_equity_data(
                    "RELIANCE",
                    date(2024, 1, 1),
                    date(2024, 1, 31)
                )
        
        assert result.symbol == "RELIANCE"
        assert result.exchange == "NSE"
        assert len(result.data) == 1
    
    def test_get_derivative_data_with_mock(self):
        """Test get_derivative_data with mocked fetch."""
        scraper = NSEScraper(headless=True)
        
        mock_response = json.dumps({
            "records": {
                "expiryDates": ["25-Jan-2024"],
                "data": [{
                    "CE": {
                        "strikePrice": 2400,
                        "openPrice": 50.0,
                        "highPrice": 55.0,
                        "lowPrice": 48.0,
                        "lastPrice": 52.0,
                        "openInterest": 10000,
                        "totalTradedVolume": 5000,
                        "expiryDate": "25-Jan-2024"
                    }
                }]
            }
        })
        
        with patch.object(scraper, '_init_session'):
            with patch.object(scraper, 'fetch_page', return_value=mock_response):
                result = scraper.get_derivative_data("RELIANCE")
        
        assert result.symbol == "RELIANCE"
        assert result.exchange == "NSE"
        assert len(result.calls) == 1


class TestNSEScraperStockList:
    """Tests for NSE stock list."""
    
    def test_get_stock_list(self):
        """Test getting stock list."""
        stocks = NSEScraper.get_stock_list()
        
        assert len(stocks) > 0
        assert "RELIANCE" in stocks
        assert "TCS" in stocks
        assert "INFY" in stocks
    
    def test_exchange_name(self):
        """Test exchange name."""
        scraper = NSEScraper(headless=True)
        assert scraper.get_exchange_name() == "NSE"
