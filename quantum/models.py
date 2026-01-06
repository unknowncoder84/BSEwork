"""
Quantum Market Suite - Data Models

Core dataclasses for configuration, market data, and processing results.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import pandas as pd
import json


@dataclass
class SearchHistoryEntry:
    """Represents a single search history entry."""
    symbol: str
    exchange: str
    start_date: str  # ISO format YYYY-MM-DD
    end_date: str    # ISO format YYYY-MM-DD
    timestamp: str   # ISO format datetime
    data_type: str   # 'equity', 'derivative', or 'both'
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "SearchHistoryEntry":
        """Create from dictionary."""
        return cls(**data)
    
    @classmethod
    def create(
        cls,
        symbol: str,
        exchange: str,
        start_date: date,
        end_date: date,
        data_type: str = "both"
    ) -> "SearchHistoryEntry":
        """Factory method to create entry with current timestamp."""
        return cls(
            symbol=symbol,
            exchange=exchange,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            timestamp=datetime.now().isoformat(),
            data_type=data_type
        )


@dataclass
class Config:
    """Application configuration stored in config.json."""
    notepad_content: str = ""
    search_history: List[SearchHistoryEntry] = field(default_factory=list)
    theme: str = "dark"
    last_exchange: str = "NSE"
    export_history: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "notepad_content": self.notepad_content,
            "search_history": [entry.to_dict() for entry in self.search_history],
            "theme": self.theme,
            "last_exchange": self.last_exchange,
            "export_history": self.export_history,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create from dictionary."""
        search_history = [
            SearchHistoryEntry.from_dict(entry) 
            for entry in data.get("search_history", [])
        ]
        return cls(
            notepad_content=data.get("notepad_content", ""),
            search_history=search_history,
            theme=data.get("theme", "dark"),
            last_exchange=data.get("last_exchange", "NSE"),
            export_history=data.get("export_history", []),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "Config":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class EquityData:
    """Container for equity OHLC and volume data."""
    symbol: str
    exchange: str
    data: pd.DataFrame  # Columns: Date, Open, High, Low, Close, Volume
    fetch_timestamp: datetime
    
    @property
    def is_empty(self) -> bool:
        """Check if data is empty."""
        return self.data is None or self.data.empty
    
    @property
    def row_count(self) -> int:
        """Get number of data rows."""
        return 0 if self.is_empty else len(self.data)


@dataclass
class DerivativeData:
    """Container for options and futures data."""
    symbol: str
    exchange: str
    expiry: date
    calls: pd.DataFrame   # Columns: Strike, Open, High, Low, Close, OI, Volume
    puts: pd.DataFrame    # Columns: Strike, Open, High, Low, Close, OI, Volume
    futures: pd.DataFrame # Columns: Expiry, Open, High, Low, Close, OI, Volume
    fetch_timestamp: datetime
    
    @property
    def is_empty(self) -> bool:
        """Check if all data is empty."""
        return (
            (self.calls is None or self.calls.empty) and
            (self.puts is None or self.puts.empty) and
            (self.futures is None or self.futures.empty)
        )


@dataclass
class MergedStockData:
    """Container for merged equity and derivative data for a single stock."""
    symbol: str
    equity_data: Optional[pd.DataFrame] = None
    call_data: Optional[pd.DataFrame] = None
    put_data: Optional[pd.DataFrame] = None
    merged_view: Optional[pd.DataFrame] = None  # Side-by-side merged data
    
    @property
    def has_equity(self) -> bool:
        """Check if equity data exists."""
        return self.equity_data is not None and not self.equity_data.empty
    
    @property
    def has_derivatives(self) -> bool:
        """Check if derivative data exists."""
        return (
            (self.call_data is not None and not self.call_data.empty) or
            (self.put_data is not None and not self.put_data.empty)
        )


@dataclass
class BulkResult:
    """Result of bulk stock processing operation."""
    successful: Dict[str, MergedStockData] = field(default_factory=dict)
    failed: Dict[str, str] = field(default_factory=dict)  # symbol -> error message
    total_time: float = 0.0
    
    @property
    def total_count(self) -> int:
        """Total number of stocks processed."""
        return len(self.successful) + len(self.failed)
    
    @property
    def success_count(self) -> int:
        """Number of successfully processed stocks."""
        return len(self.successful)
    
    @property
    def failure_count(self) -> int:
        """Number of failed stocks."""
        return len(self.failed)
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total_count == 0:
            return 0.0
        return (self.success_count / self.total_count) * 100


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    error_message: Optional[str] = None
    
    @classmethod
    def valid(cls) -> "ValidationResult":
        """Create a valid result."""
        return cls(is_valid=True)
    
    @classmethod
    def invalid(cls, message: str) -> "ValidationResult":
        """Create an invalid result with error message."""
        return cls(is_valid=False, error_message=message)


@dataclass
class FetchParams:
    """Parameters for data fetching operations."""
    start_date: date
    end_date: date
    fetch_equity: bool = True
    fetch_derivatives: bool = True
    expiry_date: Optional[date] = None
    strike_price: Optional[float] = None
    option_type: Optional[str] = None  # 'CE' or 'PE'


@dataclass
class ProcessingSummary:
    """Summary of bulk processing results."""
    total_stocks: int
    successful_stocks: List[str]
    failed_stocks: Dict[str, str]  # symbol -> error
    total_time_seconds: float
    average_time_per_stock: float
    
    @classmethod
    def from_bulk_result(cls, result: BulkResult) -> "ProcessingSummary":
        """Create summary from BulkResult."""
        avg_time = result.total_time / result.total_count if result.total_count > 0 else 0
        return cls(
            total_stocks=result.total_count,
            successful_stocks=list(result.successful.keys()),
            failed_stocks=result.failed,
            total_time_seconds=result.total_time,
            average_time_per_stock=avg_time
        )
