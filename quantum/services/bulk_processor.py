"""
Quantum Market Suite - Bulk Processor

Orchestrates multi-stock data fetching with sequential processing and fault tolerance.
"""

import time
from datetime import date
from typing import List, Optional, Callable, Dict
import pandas as pd

from quantum.models import (
    BulkResult, MergedStockData, FetchParams, ProcessingSummary,
    EquityData, DerivativeData
)
from quantum.services.exchange_router import ExchangeRouter
from quantum.services.equity_service import EquityService
from quantum.services.derivative_service import DerivativeService


class BulkProcessor:
    """Processes multiple stocks sequentially with fault tolerance."""
    
    def __init__(self, router: ExchangeRouter):
        """Initialize with exchange router."""
        self.router = router
        self.equity_service = EquityService(router)
        self.derivative_service = DerivativeService(router)
    
    def process_stocks(
        self,
        symbols: List[str],
        params: FetchParams,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> BulkResult:
        """Process multiple stocks sequentially with progress tracking."""
        start_time = time.time()
        result = BulkResult()
        
        total = len(symbols)
        
        for i, symbol in enumerate(symbols):
            try:
                # Report progress
                if progress_callback:
                    progress = (i / total) * 100
                    progress_callback(symbol, progress)
                
                # Fetch data for this stock
                merged_data = self._fetch_stock_data(symbol, params)
                result.successful[symbol] = merged_data
                
            except Exception as e:
                # Log failure but continue processing
                result.failed[symbol] = str(e)
        
        # Final progress update
        if progress_callback:
            progress_callback("Complete", 100.0)
        
        result.total_time = time.time() - start_time
        return result

    def _fetch_stock_data(self, symbol: str, params: FetchParams) -> MergedStockData:
        """Fetch equity and derivative data for a single stock."""
        equity_df = None
        call_df = None
        put_df = None
        
        # Fetch equity data if requested
        if params.fetch_equity:
            equity_data = self.equity_service.fetch_historical_data(
                symbol, params.start_date, params.end_date
            )
            equity_df = equity_data.data
        
        # Fetch derivative data if requested
        if params.fetch_derivatives:
            derivative_data = self.derivative_service.fetch_options_chain(
                symbol, params.expiry_date
            )
            call_df = derivative_data.calls
            put_df = derivative_data.puts
        
        # Create merged view
        merged_view = self._merge_data(equity_df, call_df, put_df)
        
        return MergedStockData(
            symbol=symbol,
            equity_data=equity_df,
            call_data=call_df,
            put_data=put_df,
            merged_view=merged_view
        )
    
    def _merge_data(
        self,
        equity: Optional[pd.DataFrame],
        calls: Optional[pd.DataFrame],
        puts: Optional[pd.DataFrame]
    ) -> pd.DataFrame:
        """Merge equity and derivative data side-by-side."""
        dfs = []
        
        if equity is not None and not equity.empty:
            equity_copy = equity.copy()
            equity_copy.columns = [f"Equity_{col}" for col in equity_copy.columns]
            dfs.append(equity_copy.reset_index(drop=True))
        
        if calls is not None and not calls.empty:
            calls_copy = calls.copy()
            calls_copy.columns = [f"Call_{col}" for col in calls_copy.columns]
            dfs.append(calls_copy.reset_index(drop=True))
        
        if puts is not None and not puts.empty:
            puts_copy = puts.copy()
            puts_copy.columns = [f"Put_{col}" for col in puts_copy.columns]
            dfs.append(puts_copy.reset_index(drop=True))
        
        if not dfs:
            return pd.DataFrame()
        
        return pd.concat(dfs, axis=1)
    
    def get_processing_summary(self, result: BulkResult) -> ProcessingSummary:
        """Generate summary of successful/failed retrievals."""
        return ProcessingSummary.from_bulk_result(result)
    
    @staticmethod
    def create_fetch_params(
        start_date: date,
        end_date: date,
        fetch_equity: bool = True,
        fetch_derivatives: bool = True,
        expiry_date: Optional[date] = None
    ) -> FetchParams:
        """Helper to create FetchParams."""
        return FetchParams(
            start_date=start_date,
            end_date=end_date,
            fetch_equity=fetch_equity,
            fetch_derivatives=fetch_derivatives,
            expiry_date=expiry_date
        )
