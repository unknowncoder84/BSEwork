"""
Quantum Market Suite - NSE Scraper

Scraper for National Stock Exchange (NSE) India equity and derivative data.
URLs:
- Equity: https://www.nseindia.com/report-detail/eq_security
- Derivatives: https://www.nseindia.com/report-detail/fo_eq_hist_contract_wise
"""

import pandas as pd
import time
import random
from datetime import date, datetime
from typing import List, Optional, Callable, Tuple
from bs4 import BeautifulSoup
import json
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from quantum.scrapers.base import ScraperBase, ScrapingError


class NSEScraper(ScraperBase):
    """Scraper for NSE India market data with Equity and Derivative support."""
    
    BASE_URL = "https://www.nseindia.com"
    EQUITY_URL = f"{BASE_URL}/report-detail/eq_security"
    DERIVATIVE_URL = f"{BASE_URL}/report-detail/fo_eq_hist_contract_wise"
    
    # Popular NSE stocks
    STOCK_LIST = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
        "HINDUNILVR", "SBIN", "BHARTIARTL", "KOTAKBANK", "ITC",
        "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN",
        "SUNPHARMA", "ULTRACEMCO", "NESTLEIND", "WIPRO", "BAJFINANCE",
        "HCLTECH", "POWERGRID", "NTPC", "ONGC", "TATAMOTORS",
        "JSWSTEEL", "TATASTEEL", "ADANIENT", "ADANIPORTS", "COALINDIA",
        "TECHM", "INDUSINDBK", "DRREDDY", "CIPLA", "GRASIM",
        "APOLLOHOSP", "EICHERMOT", "DIVISLAB", "BPCL", "BRITANNIA",
    ]
    
    def __init__(self, headless: bool = True):
        """Initialize NSE scraper."""
        super().__init__(headless=headless)
        self._session_initialized = False

    def get_exchange_name(self) -> str:
        """Return exchange name."""
        return "NSE"
    
    def _init_session(self) -> None:
        """Initialize session by visiting main page first to get cookies."""
        if self._session_initialized:
            return
        
        driver = self.init_driver()
        self.random_delay()
        
        # Visit main page first to establish session
        driver.get(self.BASE_URL)
        self.random_delay(3.0, 5.0)
        self._session_initialized = True
    
    def get_equity_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> pd.DataFrame:
        """
        Fetch historical equity OHLC data from NSE Security-wise Price Volume Archive.
        
        Returns DataFrame with columns: Date, Series, Open, High, Low, Close, Volume
        Series will be "EQ" for equity data.
        """
        self._init_session()
        
        if progress_callback:
            progress_callback(0.1)
        
        try:
            driver = self.driver
            
            # Navigate to equity page
            driver.get(self.EQUITY_URL)
            self.random_delay(3.0, 5.0)
            
            if progress_callback:
                progress_callback(0.3)
            
            # Wait for page to load
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Fill in the form
            self._fill_equity_form(symbol, start_date, end_date)
            
            if progress_callback:
                progress_callback(0.6)
            
            # Human delay before clicking filter
            self.random_delay(3.0, 6.0)
            
            # Click filter/download button
            self._click_filter_button()
            
            if progress_callback:
                progress_callback(0.8)
            
            # Extract table data
            df = self._extract_equity_table()
            
            # Add Series column
            df['Series'] = 'EQ'
            df['Open Interest'] = '-'
            
            if progress_callback:
                progress_callback(1.0)
            
            return df
            
        except Exception as e:
            raise ScrapingError(f"Failed to fetch equity data for {symbol}: {e}")
    
    def _fill_equity_form(self, symbol: str, start_date: date, end_date: date) -> None:
        """Fill the equity search form."""
        driver = self.driver
        
        try:
            # Find and fill symbol input
            symbol_input = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "symbol"))
            )
            symbol_input.clear()
            
            # Type symbol character by character (human-like)
            for char in symbol:
                symbol_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            self.random_delay(1.0, 2.0)
            
            # Wait for autocomplete and select
            try:
                autocomplete = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-autocomplete"))
                )
                suggestions = autocomplete.find_elements(By.TAG_NAME, "li")
                if suggestions:
                    suggestions[0].click()
                    self.random_delay(0.5, 1.0)
            except TimeoutException:
                pass
            
            # Set date range
            self._set_date_field("fromDate", start_date)
            self._set_date_field("toDate", end_date)
            
        except Exception as e:
            raise ScrapingError(f"Failed to fill equity form: {e}")
    
    def _set_date_field(self, field_id: str, date_value: date) -> None:
        """Set a date field value."""
        try:
            date_input = self.driver.find_element(By.ID, field_id)
            date_input.clear()
            date_str = date_value.strftime("%d-%m-%Y")
            date_input.send_keys(date_str)
            self.random_delay(0.3, 0.7)
        except NoSuchElementException:
            pass
    
    def _click_filter_button(self) -> None:
        """Click the filter/submit button."""
        try:
            # Try different button selectors
            button_selectors = [
                (By.ID, "submitBtn"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Filter')]"),
                (By.XPATH, "//button[contains(text(), 'Get Data')]"),
                (By.CSS_SELECTOR, ".btn-primary"),
            ]
            
            for by, selector in button_selectors:
                try:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    button.click()
                    self.random_delay(2.0, 4.0)
                    return
                except (TimeoutException, NoSuchElementException):
                    continue
            
            raise ScrapingError("Could not find filter button")
            
        except Exception as e:
            raise ScrapingError(f"Failed to click filter button: {e}")
    
    def _extract_equity_table(self) -> pd.DataFrame:
        """Extract equity data from the results table."""
        try:
            # Wait for table to load
            table = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
            )
            
            # Get table HTML and parse with pandas
            table_html = table.get_attribute('outerHTML')
            dfs = pd.read_html(table_html)
            
            if dfs and len(dfs) > 0:
                df = dfs[0]
                
                # Normalize column names
                df = self._normalize_equity_columns(df)
                
                return df
            
            return self._create_empty_equity_df()
            
        except TimeoutException:
            return self._create_empty_equity_df()
        except Exception:
            return self._create_empty_equity_df()
    
    def _normalize_equity_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize equity DataFrame columns to standard format."""
        column_map = {}
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            if 'date' in col_lower:
                column_map[col] = 'Date'
            elif col_lower == 'open' or 'open' in col_lower and 'interest' not in col_lower:
                column_map[col] = 'Open'
            elif col_lower == 'high' or 'high' in col_lower:
                column_map[col] = 'High'
            elif col_lower == 'low' or 'low' in col_lower:
                column_map[col] = 'Low'
            elif col_lower == 'close' or 'close' in col_lower or 'ltp' in col_lower:
                column_map[col] = 'Close'
            elif 'volume' in col_lower or 'qty' in col_lower:
                column_map[col] = 'Volume'
        
        df = df.rename(columns=column_map)
        
        # Ensure required columns exist
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0
        
        return df[required_cols]
    
    def _create_empty_equity_df(self) -> pd.DataFrame:
        """Create empty DataFrame with correct structure."""
        return pd.DataFrame(columns=['Date', 'Series', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest'])

    def get_derivative_data(
        self,
        symbol: str,
        expiry_date: date,
        strike_price: float,
        option_type: str = "CE",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> pd.DataFrame:
        """
        Fetch historical derivative data from NSE Contract-wise Price Volume Data.
        
        Args:
            symbol: Stock symbol
            expiry_date: Option expiry date
            strike_price: Strike price (NOT hardcoded - user input)
            option_type: "CE" for Call or "PE" for Put
            start_date: Start date for data
            end_date: End date for data
            progress_callback: Optional progress callback
            
        Returns:
            DataFrame with columns: Date, Series, Open, High, Low, Close, Volume, Open Interest
            Series will be "OPT" for derivative data.
        """
        self._init_session()
        
        if progress_callback:
            progress_callback(0.1)
        
        try:
            driver = self.driver
            
            # Navigate to derivative page
            driver.get(self.DERIVATIVE_URL)
            self.random_delay(3.0, 5.0)
            
            if progress_callback:
                progress_callback(0.3)
            
            # Wait for page to load
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Fill in the derivative form
            self._fill_derivative_form(
                symbol, expiry_date, strike_price, option_type, start_date, end_date
            )
            
            if progress_callback:
                progress_callback(0.6)
            
            # Human delay before clicking filter (3-6 seconds)
            self.random_delay(3.0, 6.0)
            
            # Click filter/download button
            self._click_filter_button()
            
            if progress_callback:
                progress_callback(0.8)
            
            # Extract table data
            df = self._extract_derivative_table()
            
            # Add Series column
            df['Series'] = 'OPT'
            
            if progress_callback:
                progress_callback(1.0)
            
            return df
            
        except Exception as e:
            raise ScrapingError(f"Failed to fetch derivative data for {symbol}: {e}")
    
    def _fill_derivative_form(
        self, 
        symbol: str, 
        expiry_date: date, 
        strike_price: float,
        option_type: str,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> None:
        """Fill the derivative search form with dynamic strike price selection."""
        driver = self.driver
        
        try:
            # Select instrument type (Stock Options)
            self._select_dropdown("instrumentType", "Stock Options")
            self.random_delay(1.0, 2.0)
            
            # Fill symbol
            symbol_input = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "symbol"))
            )
            symbol_input.clear()
            
            for char in symbol:
                symbol_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            self.random_delay(1.0, 2.0)
            
            # Wait for autocomplete
            try:
                autocomplete = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-autocomplete"))
                )
                suggestions = autocomplete.find_elements(By.TAG_NAME, "li")
                if suggestions:
                    suggestions[0].click()
                    self.random_delay(1.0, 2.0)
            except TimeoutException:
                pass
            
            # Select expiry date - WAIT for dropdown to populate
            self._wait_and_select_expiry(expiry_date)
            self.random_delay(1.0, 2.0)
            
            # Select option type (CE/PE)
            self._select_dropdown("optionType", option_type)
            self.random_delay(1.0, 2.0)
            
            # CRITICAL: Wait for strike price dropdown to populate after expiry selection
            # Then select user-provided strike price (NOT hardcoded)
            self._wait_and_select_strike_price(strike_price)
            
            # Set date range if provided
            if start_date:
                self._set_date_field("fromDate", start_date)
            if end_date:
                self._set_date_field("toDate", end_date)
            
        except Exception as e:
            raise ScrapingError(f"Failed to fill derivative form: {e}")
    
    def _select_dropdown(self, dropdown_id: str, value: str) -> None:
        """Select value from dropdown."""
        try:
            dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, dropdown_id))
            )
            select = Select(dropdown)
            select.select_by_visible_text(value)
        except Exception:
            pass
    
    def _wait_and_select_expiry(self, expiry_date: date) -> None:
        """Wait for expiry dropdown to populate and select the date."""
        try:
            # Wait for expiry dropdown to be populated
            expiry_dropdown = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, "expiryDate"))
            )
            
            # Wait a bit for options to load
            self.random_delay(1.0, 2.0)
            
            select = Select(expiry_dropdown)
            expiry_str = expiry_date.strftime("%d-%b-%Y")
            
            # Try to find matching expiry
            for option in select.options:
                if expiry_str.lower() in option.text.lower():
                    select.select_by_visible_text(option.text)
                    return
            
            # If exact match not found, select first available
            if len(select.options) > 1:
                select.select_by_index(1)
                
        except Exception as e:
            raise ScrapingError(f"Failed to select expiry date: {e}")
    
    def _wait_and_select_strike_price(self, strike_price: float) -> None:
        """
        Wait for strike price dropdown to populate after expiry selection,
        then select the user-provided strike price.
        
        CRITICAL: This is NOT hardcoded - uses user input.
        """
        try:
            # Wait for strike price dropdown to be populated
            strike_dropdown = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, "strikePrice"))
            )
            
            # Wait for options to load after expiry selection
            self.random_delay(2.0, 3.0)
            
            select = Select(strike_dropdown)
            
            # Format strike price for matching
            strike_str = str(int(strike_price)) if strike_price == int(strike_price) else str(strike_price)
            
            # Try to find matching strike price
            available_options = [opt.text.strip() for opt in select.options]
            
            strike_found = False
            for option_text in available_options:
                if strike_str in option_text or option_text == strike_str:
                    select.select_by_visible_text(option_text)
                    strike_found = True
                    break
            
            if not strike_found:
                raise ScrapingError(f"Strike price {strike_price} not available. Available: {available_options[:10]}")
                
        except TimeoutException:
            raise ScrapingError("Strike price dropdown did not load")
        except Exception as e:
            if "not available" in str(e):
                raise
            raise ScrapingError(f"Failed to select strike price: {e}")
    
    def _extract_derivative_table(self) -> pd.DataFrame:
        """Extract derivative data from the results table."""
        try:
            # Wait for table to load
            table = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
            )
            
            # Get table HTML and parse with pandas
            table_html = table.get_attribute('outerHTML')
            dfs = pd.read_html(table_html)
            
            if dfs and len(dfs) > 0:
                df = dfs[0]
                df = self._normalize_derivative_columns(df)
                return df
            
            return self._create_empty_derivative_df()
            
        except TimeoutException:
            return self._create_empty_derivative_df()
        except Exception:
            return self._create_empty_derivative_df()
    
    def _normalize_derivative_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize derivative DataFrame columns to standard format."""
        column_map = {}
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            if 'date' in col_lower:
                column_map[col] = 'Date'
            elif col_lower == 'open' or ('open' in col_lower and 'interest' not in col_lower):
                column_map[col] = 'Open'
            elif col_lower == 'high' or 'high' in col_lower:
                column_map[col] = 'High'
            elif col_lower == 'low' or 'low' in col_lower:
                column_map[col] = 'Low'
            elif col_lower == 'close' or 'close' in col_lower or 'ltp' in col_lower:
                column_map[col] = 'Close'
            elif 'volume' in col_lower or 'qty' in col_lower:
                column_map[col] = 'Volume'
            elif 'open interest' in col_lower or col_lower == 'oi':
                column_map[col] = 'Open Interest'
        
        df = df.rename(columns=column_map)
        
        # Ensure required columns exist
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0
        
        return df[required_cols]
    
    def _create_empty_derivative_df(self) -> pd.DataFrame:
        """Create empty DataFrame with correct structure."""
        return pd.DataFrame(columns=['Date', 'Series', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest'])
    
    def get_combined_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        expiry_date: Optional[date] = None,
        strike_price: Optional[float] = None,
        fetch_equity: bool = True,
        fetch_derivatives: bool = True,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> pd.DataFrame:
        """
        Fetch and combine both equity and derivative data for a symbol.
        
        Returns unified DataFrame with columns:
        Date, Series, Open, High, Low, Close, Volume, Open Interest
        
        Series = "EQ" for equity, "OPT" for derivatives
        Open Interest = "-" for equity rows
        """
        all_data = []
        
        # Fetch equity data
        if fetch_equity:
            try:
                equity_df = self.get_equity_data(
                    symbol, start_date, end_date,
                    progress_callback=lambda p: progress_callback(p * 0.4) if progress_callback else None
                )
                if not equity_df.empty:
                    all_data.append(equity_df)
            except Exception as e:
                print(f"Warning: Could not fetch equity data: {e}")
        
        # Fetch derivative data (Call and Put)
        if fetch_derivatives and expiry_date and strike_price:
            # Fetch Call data
            try:
                call_df = self.get_derivative_data(
                    symbol, expiry_date, strike_price, "CE", start_date, end_date,
                    progress_callback=lambda p: progress_callback(0.4 + p * 0.3) if progress_callback else None
                )
                if not call_df.empty:
                    call_df['Option_Type'] = 'CE'
                    all_data.append(call_df)
            except Exception as e:
                print(f"Warning: Could not fetch Call data: {e}")
            
            # Fetch Put data
            try:
                put_df = self.get_derivative_data(
                    symbol, expiry_date, strike_price, "PE", start_date, end_date,
                    progress_callback=lambda p: progress_callback(0.7 + p * 0.3) if progress_callback else None
                )
                if not put_df.empty:
                    put_df['Option_Type'] = 'PE'
                    all_data.append(put_df)
            except Exception as e:
                print(f"Warning: Could not fetch Put data: {e}")
        
        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        
        return self._create_empty_equity_df()
    
    @classmethod
    def get_stock_list(cls) -> List[str]:
        """Get list of available NSE stocks."""
        return cls.STOCK_LIST.copy()
