"""
Quantum Market Suite - Exchange Router

Routes data requests to the appropriate exchange scraper (NSE or BSE).
"""

from datetime import date
from typing import List, Optional, Callable
import pandas as pd

from quantum.scrapers.nse_scraper import NSEScraper
from quantum.scrapers.bse_scraper import BSEScraper
from quantum.models import EquityData, DerivativeData


class ExchangeRouter:
    """Routes data requests to appropriate exchange scraper."""
    
    VALID_EXCHANGES = ("NSE", "BSE")
    
    def __init__(self, exchange: str = "NSE", headless: bool = True):
        """Initialize router with selected exchange."""
        self._exchange = self._validate_exchange(exchange)
        self._headless = headless
        self._scraper = None
        self._cached_data: dict = {}
    
    def _validate_exchange(self, exchange: str) -> str:
        """Validate and normalize exchange name."""
        exchange = exchange.upper()
        if exchange not in self.VALID_EXCHANGES:
            raise ValueError(f"Invalid exchange: {exchange}. Must be one of {self.VALID_EXCHANGES}")
        return exchange
    
    @property
    def exchange(self) -> str:
        """Get current exchange."""
        return self._exchange
    
    @exchange.setter
    def exchange(self, value: str) -> None:
        """Set exchange and clear cached data."""
        new_exchange = self._validate_exchange(value)
        if new_exchange != self._exchange:
            self._exchange = new_exchange
            self._scraper = None
            self.clear_data()

    def _get_scraper(self):
        """Get or create scraper for current exchange."""
        if self._scraper is None:
            if self._exchange == "NSE":
                self._scraper = NSEScraper(headless=self._headless)
            else:
                self._scraper = BSEScraper(headless=self._headless)
        return self._scraper
    
    def clear_data(self) -> None:
        """Clear all cached data."""
        self._cached_data = {}
    
    def get_cached_data(self) -> dict:
        """Get cached data (for testing)."""
        return self._cached_data.copy()
    
    def get_equity_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> EquityData:
        """Fetch equity OHLC data from selected exchange."""
        scraper = self._get_scraper()
        result = scraper.get_equity_data(symbol, start_date, end_date, progress_callback)
        
        # Cache the result
        cache_key = f"equity_{symbol}_{start_date}_{end_date}"
        self._cached_data[cache_key] = result
        
        return result
    
    def get_derivative_data(
        self,
        symbol: str,
        expiry: Optional[date] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> DerivativeData:
        """Fetch derivative data from selected exchange."""
        scraper = self._get_scraper()
        result = scraper.get_derivative_data(symbol, expiry, progress_callback)
        
        # Cache the result
        cache_key = f"derivative_{symbol}_{expiry}"
        self._cached_data[cache_key] = result
        
        return result
    
    def get_available_expiries(self, symbol: str) -> List[date]:
        """Get available expiry dates for a symbol."""
        scraper = self._get_scraper()
        return scraper.get_available_expiries(symbol)
    
    def get_stock_list(self) -> List[str]:
        """Get list of available stocks for current exchange."""
        if self._exchange == "NSE":
            return NSEScraper.get_stock_list()
        else:
            return BSEScraper.get_stock_list()
    
    def close(self) -> None:
        """Close scraper connection."""
        if self._scraper:
            self._scraper.close_driver()
            self._scraper = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
