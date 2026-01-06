"""
Quantum Market Suite - Equity Service

Handles equity OHLC and volume data retrieval with validation.
"""

from datetime import date, datetime
from typing import Optional, Callable
import pandas as pd

from quantum.models import EquityData, ValidationResult
from quantum.services.exchange_router import ExchangeRouter


class EquityService:
    """Service for equity data operations."""
    
    REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]
    
    def __init__(self, router: ExchangeRouter):
        """Initialize with exchange router."""
        self.router = router
    
    def validate_date_range(self, start_date: date, end_date: date) -> ValidationResult:
        """Validate the date range is valid for trading data."""
        if end_date < start_date:
            return ValidationResult.invalid(
                f"End date ({end_date}) cannot be before start date ({start_date})"
            )
        
        if start_date > date.today():
            return ValidationResult.invalid(
                f"Start date ({start_date}) cannot be in the future"
            )
        
        # Check if range is too large (more than 2 years)
        days_diff = (end_date - start_date).days
        if days_diff > 730:
            return ValidationResult.invalid(
                "Date range cannot exceed 2 years"
            )
        
        return ValidationResult.valid()
    
    def fetch_historical_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> EquityData:
        """Fetch historical OHLC + Volume data with progress updates."""
        # Validate date range first
        validation = self.validate_date_range(start_date, end_date)
        if not validation.is_valid:
            raise ValueError(validation.error_message)
        
        return self.router.get_equity_data(
            symbol, start_date, end_date, progress_callback
        )
    
    def validate_equity_data(self, data: EquityData) -> ValidationResult:
        """Validate equity data has required columns and valid values."""
        if data.is_empty:
            return ValidationResult.invalid("No data available")
        
        df = data.data
        
        # Check required columns
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            return ValidationResult.invalid(
                f"Missing required columns: {missing_cols}"
            )
        
        # Check for valid numeric values in OHLC columns
        numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
        for col in numeric_cols:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    return ValidationResult.invalid(
                        f"Column {col} contains non-numeric values"
                    )
        
        return ValidationResult.valid()
