"""
Data models and validation for BSE Derivative Data Downloader.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Tuple


@dataclass
class FetchParameters:
    """Parameters for fetching derivative data from BSE."""
    company_name: str
    instrument_type: str  # "Equity Options" or "Index Options"
    expiry_date: date
    strike_price: float
    from_date: date
    to_date: date
    
    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate all parameters and return (is_valid, error_messages)."""
        errors = []
        
        if not self.company_name or not self.company_name.strip():
            errors.append("Company name cannot be empty")
        
        if self.instrument_type not in ["Equity Options", "Index Options"]:
            errors.append("Instrument type must be 'Equity Options' or 'Index Options'")
        
        if self.strike_price <= 0:
            errors.append("Strike price must be a positive number")
        
        if self.from_date > self.to_date:
            errors.append("From date must be before or equal to To date")
        
        if self.expiry_date < self.from_date:
            errors.append("Expiry date should be on or after From date")
        
        return len(errors) == 0, errors


# Custom Exception Classes
class BSEScraperError(Exception):
    """Base exception for BSE scraper errors."""
    pass


class ConnectivityError(BSEScraperError):
    """Raised when unable to connect to BSE website."""
    def __init__(self, message: str = "Unable to connect to BSE website. Please check your internet connection."):
        self.message = message
        super().__init__(self.message)


class CompanyNotFoundError(BSEScraperError):
    """Raised when company is not found on BSE."""
    def __init__(self, company_name: str):
        self.message = f"Company '{company_name}' not found on BSE. Please check the company name."
        super().__init__(self.message)


class NoDataError(BSEScraperError):
    """Raised when no data is available for the specified parameters."""
    def __init__(self, message: str = "No data available for the specified parameters."):
        self.message = message
        super().__init__(self.message)


class BotDetectionError(BSEScraperError):
    """Raised when bot detection is triggered."""
    def __init__(self, message: str = "Access blocked. Please try again later."):
        self.message = message
        super().__init__(self.message)


class DataValidationError(BSEScraperError):
    """Raised when fetched data fails validation."""
    def __init__(self, message: str = "Fetched data is invalid or corrupted."):
        self.message = message
        super().__init__(self.message)


class ElementNotFoundError(BSEScraperError):
    """Raised when expected element is not found on page."""
    def __init__(self, element_name: str):
        self.message = f"Expected element '{element_name}' not found on page. BSE website structure may have changed."
        super().__init__(self.message)


def validate_inputs(company_name: str, instrument_type: str, expiry_date: date,
                   strike_price: float, from_date: date, to_date: date) -> Tuple[bool, List[str]]:
    """
    Validate user inputs and return validation result.
    
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    params = FetchParameters(
        company_name=company_name,
        instrument_type=instrument_type,
        expiry_date=expiry_date,
        strike_price=strike_price,
        from_date=from_date,
        to_date=to_date
    )
    return params.is_valid()


def all_inputs_provided(company_name: Optional[str], instrument_type: Optional[str],
                        expiry_date: Optional[date], strike_price: Optional[float],
                        from_date: Optional[date], to_date: Optional[date]) -> bool:
    """Check if all required inputs are provided (not None/empty)."""
    if not company_name or not company_name.strip():
        return False
    if not instrument_type:
        return False
    if expiry_date is None:
        return False
    if strike_price is None or strike_price <= 0:
        return False
    if from_date is None or to_date is None:
        return False
    return True
