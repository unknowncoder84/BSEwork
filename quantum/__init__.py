"""
Quantum Market Suite - Futuristic NSE & BSE Market Data Dashboard

A comprehensive financial dashboard for dual-exchange market data analysis
with glassmorphism UI, persistent storage, and professional Excel exports.
"""

__version__ = "1.0.0"
__author__ = "Quantum Market Suite"

from quantum.models import (
    Config,
    SearchHistoryEntry,
    EquityData,
    DerivativeData,
    MergedStockData,
    BulkResult,
    ValidationResult,
)

__all__ = [
    "Config",
    "SearchHistoryEntry",
    "EquityData",
    "DerivativeData",
    "MergedStockData",
    "BulkResult",
    "ValidationResult",
]
