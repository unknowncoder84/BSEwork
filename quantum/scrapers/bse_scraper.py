"""
Quantum Market Suite - BSE Scraper

Scraper for Bombay Stock Exchange (BSE) India equity and derivative data.
"""

import pandas as pd
from datetime import date, datetime
from typing import List, Optional, Callable
from bs4 import BeautifulSoup
import json
import re

from quantum.scrapers.base import ScraperBase, ScrapingError
from quantum.models import EquityData, DerivativeData


class BSEScraper(ScraperBase):
    """Scraper for BSE India market data."""
    
    BASE_URL = "https://www.bseindia.com"
    EQUITY_URL = f"{BASE_URL}/markets/equity/EQReports/StockPrcHistori.html"
    DERIVATIVE_URL = f"{BASE_URL}/markets/Derivatives/DeriReports/Option_Chain.html"
    
    # Popular BSE stocks with scrip codes
    STOCK_LIST = {
        "RELIANCE": "500325",
        "TCS": "532540",
        "HDFCBANK": "500180",
        "INFY": "500209",
        "ICICIBANK": "532174",
        "HINDUNILVR": "500696",
        "SBIN": "500112",
        "BHARTIARTL": "532454",
        "KOTAKBANK": "500247",
        "ITC": "500875",
        "LT": "500510",
        "AXISBANK": "532215",
        "ASIANPAINT": "500820",
        "MARUTI": "532500",
        "TITAN": "500114",
        "SUNPHARMA": "524715",
        "ULTRACEMCO": "532538",
        "NESTLEIND": "500790",
        "WIPRO": "507685",
        "BAJFINANCE": "500034",
    }
    
    def __init__(self, headless: bool = True):
        """Initialize BSE scraper."""
        super().__init__(headless=headless)
        self._session_initialized = False

    def get_exchange_name(self) -> str:
        """Return exchange name."""
        return "BSE"
    
    def _init_session(self) -> None:
        """Initialize session by visiting main page first."""
        if self._session_initialized:
            return
        
        driver = self.init_driver()
        self.random_delay()
        driver.get(self.BASE_URL)
        self.random_delay(2.0, 4.0)
        self._session_initialized = True
    
    def _get_scrip_code(self, symbol: str) -> Optional[str]:
        """Get BSE scrip code for a symbol."""
        return self.STOCK_LIST.get(symbol.upper())
    
    def get_equity_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> EquityData:
        """Fetch historical equity OHLC data from BSE."""
        self._init_session()
        
        if progress_callback:
            progress_callback(0.1)
        
        scrip_code = self._get_scrip_code(symbol)
        if not scrip_code:
            scrip_code = symbol  # Assume it's already a scrip code
        
        try:
            url = self._build_equity_url(scrip_code, start_date, end_date)
            
            if progress_callback:
                progress_callback(0.3)
            
            page_source = self.fetch_page(url)
            
            if progress_callback:
                progress_callback(0.7)
            
            df = self._parse_equity_response(page_source, symbol)
            
            if progress_callback:
                progress_callback(1.0)
            
            return EquityData(
                symbol=symbol,
                exchange="BSE",
                data=df,
                fetch_timestamp=datetime.now()
            )
        except Exception as e:
            raise ScrapingError(f"Failed to fetch BSE equity data for {symbol}: {e}")

    def _build_equity_url(self, scrip_code: str, start_date: date, end_date: date) -> str:
        """Build URL for BSE equity historical data."""
        from_date = start_date.strftime("%d/%m/%Y")
        to_date = end_date.strftime("%d/%m/%Y")
        return f"{self.EQUITY_URL}?scripcode={scrip_code}&fromdate={from_date}&todate={to_date}"
    
    def _parse_equity_response(self, page_source: str, symbol: str) -> pd.DataFrame:
        """Parse equity data from BSE response."""
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Try to find data table
            table = soup.find('table', {'id': 'ContentPlaceHolder1_gvData'})
            if not table:
                table = soup.find('table', class_='mktdet_table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                data = []
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        data.append({
                            "Date": cols[0].text.strip(),
                            "Open": self._parse_number(cols[1].text),
                            "High": self._parse_number(cols[2].text),
                            "Low": self._parse_number(cols[3].text),
                            "Close": self._parse_number(cols[4].text),
                            "Volume": self._parse_number(cols[5].text),
                        })
                
                if data:
                    return pd.DataFrame(data)
            
            # Try JSON response
            data = self._extract_json(page_source)
            if data and isinstance(data, list):
                df = pd.DataFrame(data)
                return self._standardize_equity_columns(df)
            
            return self._create_empty_equity_df()
            
        except Exception:
            return self._create_empty_equity_df()
    
    def _parse_number(self, text: str) -> float:
        """Parse number from text, handling commas."""
        try:
            return float(text.replace(',', '').strip())
        except (ValueError, AttributeError):
            return 0.0
    
    def _standardize_equity_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names for equity data."""
        column_map = {
            "date": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
            "tottrdqty": "Volume",
        }
        
        df.columns = df.columns.str.lower()
        df = df.rename(columns=column_map)
        
        required_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0
        
        return df[required_cols]
    
    def _create_empty_equity_df(self) -> pd.DataFrame:
        """Create empty DataFrame with correct structure."""
        return pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])

    def get_derivative_data(
        self,
        symbol: str,
        expiry: Optional[date] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> DerivativeData:
        """Fetch options chain data from BSE."""
        self._init_session()
        
        if progress_callback:
            progress_callback(0.1)
        
        scrip_code = self._get_scrip_code(symbol)
        if not scrip_code:
            scrip_code = symbol
        
        try:
            url = f"{self.DERIVATIVE_URL}?scripcode={scrip_code}"
            
            if progress_callback:
                progress_callback(0.3)
            
            page_source = self.fetch_page(url)
            
            if progress_callback:
                progress_callback(0.7)
            
            calls_df, puts_df, futures_df, actual_expiry = self._parse_derivative_response(
                page_source, symbol, expiry
            )
            
            if progress_callback:
                progress_callback(1.0)
            
            return DerivativeData(
                symbol=symbol,
                exchange="BSE",
                expiry=actual_expiry or expiry or date.today(),
                calls=calls_df,
                puts=puts_df,
                futures=futures_df,
                fetch_timestamp=datetime.now()
            )
        except Exception as e:
            raise ScrapingError(f"Failed to fetch BSE derivative data for {symbol}: {e}")
    
    def _parse_derivative_response(
        self, page_source: str, symbol: str, target_expiry: Optional[date]
    ) -> tuple:
        """Parse derivative data from BSE response."""
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            
            calls_data = []
            puts_data = []
            actual_expiry = target_expiry
            
            # Try to find options table
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cols = row.find_all('td')
                    if len(cols) >= 8:
                        strike = self._parse_number(cols[0].text)
                        
                        # Call data
                        calls_data.append({
                            "Strike": strike,
                            "Open": self._parse_number(cols[1].text),
                            "High": self._parse_number(cols[2].text),
                            "Low": self._parse_number(cols[3].text),
                            "Close": self._parse_number(cols[4].text),
                            "OI": self._parse_number(cols[5].text),
                            "Volume": self._parse_number(cols[6].text),
                            "Expiry": "",
                            "Type": "CE"
                        })
                        
                        # Put data (if available in same row)
                        if len(cols) >= 14:
                            puts_data.append({
                                "Strike": strike,
                                "Open": self._parse_number(cols[8].text),
                                "High": self._parse_number(cols[9].text),
                                "Low": self._parse_number(cols[10].text),
                                "Close": self._parse_number(cols[11].text),
                                "OI": self._parse_number(cols[12].text),
                                "Volume": self._parse_number(cols[13].text),
                                "Expiry": "",
                                "Type": "PE"
                            })
            
            calls_df = pd.DataFrame(calls_data) if calls_data else self._create_empty_options_df()
            puts_df = pd.DataFrame(puts_data) if puts_data else self._create_empty_options_df()
            futures_df = self._create_empty_futures_df()
            
            return calls_df, puts_df, futures_df, actual_expiry
            
        except Exception:
            return self._create_empty_derivative_dfs()

    def _create_empty_derivative_dfs(self) -> tuple:
        """Create empty derivative DataFrames."""
        return (
            self._create_empty_options_df(),
            self._create_empty_options_df(),
            self._create_empty_futures_df(),
            None
        )
    
    def _create_empty_options_df(self) -> pd.DataFrame:
        """Create empty options DataFrame."""
        return pd.DataFrame(columns=[
            "Strike", "Open", "High", "Low", "Close", "OI", "Volume", "Expiry", "Type"
        ])
    
    def _create_empty_futures_df(self) -> pd.DataFrame:
        """Create empty futures DataFrame."""
        return pd.DataFrame(columns=[
            "Expiry", "Open", "High", "Low", "Close", "OI", "Volume"
        ])
    
    def get_available_expiries(self, symbol: str) -> List[date]:
        """Get available expiry dates for a symbol."""
        # BSE expiry dates are typically monthly
        # Return empty list as BSE derivative data is limited
        return []
    
    def _extract_json(self, page_source: str) -> Optional[dict]:
        """Extract JSON data from page source."""
        try:
            return json.loads(page_source)
        except json.JSONDecodeError:
            pass
        
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            pre_tag = soup.find('pre')
            if pre_tag:
                return json.loads(pre_tag.text)
        except Exception:
            pass
        
        try:
            match = re.search(r'\{.*\}', page_source, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        
        return None
    
    @classmethod
    def get_stock_list(cls) -> List[str]:
        """Get list of available BSE stocks."""
        return list(cls.STOCK_LIST.keys())
    
    @classmethod
    def get_scrip_code(cls, symbol: str) -> Optional[str]:
        """Get scrip code for a symbol."""
        return cls.STOCK_LIST.get(symbol.upper())
