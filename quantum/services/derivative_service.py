"""
Quantum Market Suite - Derivative Service

Handles Options/Futures data retrieval including Open Interest.
"""

from datetime import date
from typing import Optional, Callable, Tuple, List
import pandas as pd

from quantum.models import DerivativeData, ValidationResult
from quantum.services.exchange_router import ExchangeRouter


class DerivativeService:
    """Service for derivative data operations."""
    
    REQUIRED_OPTIONS_COLUMNS = ["Strike", "Open", "High", "Low", "Close", "OI", "Volume"]
    
    def __init__(self, router: ExchangeRouter):
        """Initialize with exchange router."""
        self.router = router
    
    def fetch_options_chain(
        self,
        symbol: str,
        expiry: Optional[date] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> DerivativeData:
        """Fetch complete options chain for an expiry."""
        return self.router.get_derivative_data(symbol, expiry, progress_callback)
    
    def fetch_futures_data(
        self,
        symbol: str,
        expiry: Optional[date] = None
    ) -> pd.DataFrame:
        """Fetch futures contract data."""
        data = self.router.get_derivative_data(symbol, expiry)
        return data.futures
    
    def get_call_put_split(
        self, 
        options_data: DerivativeData
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split options data into Call and Put DataFrames."""
        return options_data.calls, options_data.puts
    
    def get_available_expiries(self, symbol: str) -> List[date]:
        """Get available expiry dates for a symbol."""
        return self.router.get_available_expiries(symbol)
    
    def validate_derivative_data(self, data: DerivativeData) -> ValidationResult:
        """Validate derivative data structure."""
        if data.is_empty:
            return ValidationResult.invalid("No derivative data available")
        
        # Check calls DataFrame
        if data.calls is not None and not data.calls.empty:
            missing = [c for c in self.REQUIRED_OPTIONS_COLUMNS if c not in data.calls.columns]
            if missing:
                return ValidationResult.invalid(f"Calls missing columns: {missing}")
        
        # Check puts DataFrame
        if data.puts is not None and not data.puts.empty:
            missing = [c for c in self.REQUIRED_OPTIONS_COLUMNS if c not in data.puts.columns]
            if missing:
                return ValidationResult.invalid(f"Puts missing columns: {missing}")
        
        return ValidationResult.valid()
    
    def filter_by_strike(
        self,
        data: DerivativeData,
        min_strike: Optional[float] = None,
        max_strike: Optional[float] = None
    ) -> DerivativeData:
        """Filter options data by strike price range."""
        calls = data.calls.copy() if data.calls is not None else pd.DataFrame()
        puts = data.puts.copy() if data.puts is not None else pd.DataFrame()
        
        if min_strike is not None:
            if not calls.empty:
                calls = calls[calls["Strike"] >= min_strike]
            if not puts.empty:
                puts = puts[puts["Strike"] >= min_strike]
        
        if max_strike is not None:
            if not calls.empty:
                calls = calls[calls["Strike"] <= max_strike]
            if not puts.empty:
                puts = puts[puts["Strike"] <= max_strike]
        
        return DerivativeData(
            symbol=data.symbol,
            exchange=data.exchange,
            expiry=data.expiry,
            calls=calls,
            puts=puts,
            futures=data.futures,
            fetch_timestamp=data.fetch_timestamp
        )
