"""
Quantum Market Suite - BSE Scraper Tests

Unit tests for BSE scraper with mocked responses.
"""

import pytest
from unittest.mock import patch
from datetime import date
import pandas as pd

from quantum.scrapers.bse_scraper import BSEScraper


class TestBSEScraperEquityParsing:
    """Tests for BSE equity data parsing."""
    
    def test_parse_equity_response_html_table(self):
        """Test parsing HTML table equity response."""
        scraper = BSEScraper(headless=True)
        
        mock_html = """
        <html>
        <body>
        <table id="ContentPlaceHolder1_gvData">
            <tr><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th></tr>
            <tr><td>15-01-2024</td><td>100.00</td><td>105.00</td><td>98.00</td><td>103.00</td><td>1,000,000</td></tr>
            <tr><td>16-01-2024</td><td>103.00</td><td>108.00</td><td>102.00</td><td>107.00</td><td>1,200,000</td></tr>
        </table>
        </body>
        </html>
        """
        
        df = scraper._parse_equity_response(mock_html, "RELIANCE")
        
        assert len(df) == 2
        assert "Date" in df.columns
        assert "Open" in df.columns
        assert df.iloc[0]["Open"] == 100.0
    
    def test_parse_equity_response_empty(self):
        """Test parsing empty equity response."""
        scraper = BSEScraper(headless=True)
        
        df = scraper._parse_equity_response("<html><body></body></html>", "RELIANCE")
        
        assert len(df) == 0
        assert list(df.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]

    def test_build_equity_url(self):
        """Test equity URL building."""
        scraper = BSEScraper(headless=True)
        
        url = scraper._build_equity_url(
            "500325",
            date(2024, 1, 1),
            date(2024, 1, 31)
        )
        
        assert "scripcode=500325" in url
        assert "fromdate=01/01/2024" in url
        assert "todate=31/01/2024" in url
    
    def test_parse_number(self):
        """Test number parsing with commas."""
        scraper = BSEScraper(headless=True)
        
        assert scraper._parse_number("1,000,000") == 1000000.0
        assert scraper._parse_number("100.50") == 100.5
        assert scraper._parse_number("invalid") == 0.0


class TestBSEScraperDerivativeParsing:
    """Tests for BSE derivative data parsing."""
    
    def test_parse_derivative_response_empty(self):
        """Test parsing empty derivative response."""
        scraper = BSEScraper(headless=True)
        
        calls_df, puts_df, futures_df, expiry = scraper._parse_derivative_response(
            "<html><body></body></html>", "RELIANCE", None
        )
        
        assert len(calls_df) == 0
        assert len(puts_df) == 0
    
    def test_create_empty_options_df(self):
        """Test empty options DataFrame structure."""
        scraper = BSEScraper(headless=True)
        
        df = scraper._create_empty_options_df()
        
        expected_cols = ["Strike", "Open", "High", "Low", "Close", "OI", "Volume", "Expiry", "Type"]
        assert list(df.columns) == expected_cols


class TestBSEScraperErrorHandling:
    """Tests for BSE scraper error handling."""
    
    def test_get_equity_data_with_mock(self):
        """Test get_equity_data with mocked fetch."""
        scraper = BSEScraper(headless=True)
        
        mock_html = """
        <html>
        <body>
        <table id="ContentPlaceHolder1_gvData">
            <tr><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th></tr>
            <tr><td>15-01-2024</td><td>100.00</td><td>105.00</td><td>98.00</td><td>103.00</td><td>1000000</td></tr>
        </table>
        </body>
        </html>
        """
        
        with patch.object(scraper, '_init_session'):
            with patch.object(scraper, 'fetch_page', return_value=mock_html):
                result = scraper.get_equity_data(
                    "RELIANCE",
                    date(2024, 1, 1),
                    date(2024, 1, 31)
                )
        
        assert result.symbol == "RELIANCE"
        assert result.exchange == "BSE"
        assert len(result.data) == 1
    
    def test_get_derivative_data_with_mock(self):
        """Test get_derivative_data with mocked fetch."""
        scraper = BSEScraper(headless=True)
        
        with patch.object(scraper, '_init_session'):
            with patch.object(scraper, 'fetch_page', return_value="<html></html>"):
                result = scraper.get_derivative_data("RELIANCE")
        
        assert result.symbol == "RELIANCE"
        assert result.exchange == "BSE"


class TestBSEScraperStockList:
    """Tests for BSE stock list."""
    
    def test_get_stock_list(self):
        """Test getting stock list."""
        stocks = BSEScraper.get_stock_list()
        
        assert len(stocks) > 0
        assert "RELIANCE" in stocks
        assert "TCS" in stocks
    
    def test_get_scrip_code(self):
        """Test getting scrip code."""
        code = BSEScraper.get_scrip_code("RELIANCE")
        assert code == "500325"
        
        code = BSEScraper.get_scrip_code("UNKNOWN")
        assert code is None
    
    def test_exchange_name(self):
        """Test exchange name."""
        scraper = BSEScraper(headless=True)
        assert scraper.get_exchange_name() == "BSE"
