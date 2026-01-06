"""
Quantum Market Suite - Bulk Processor Tests

Property-based tests for bulk processing functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings
from datetime import date, datetime
import pandas as pd

from quantum.services.bulk_processor import BulkProcessor
from quantum.services.exchange_router import ExchangeRouter
from quantum.models import FetchParams, EquityData, DerivativeData, MergedStockData


class TestBulkProcessingCompleteness:
    """
    **Feature: quantum-market-suite, Property 6: Bulk Processing Completeness**
    **Validates: Requirements 4.1, 4.3**
    
    For any list of N stocks submitted for bulk processing, the result SHALL
    contain exactly N entries split between successful and failed categories,
    with no stock missing or duplicated.
    """
    
    @given(num_stocks=st.integers(min_value=1, max_value=20))
    @settings(max_examples=100, deadline=None)
    def test_result_contains_all_stocks(self, num_stocks: int):
        """Test that result contains exactly N entries for N stocks."""
        symbols = [f"STOCK{i}" for i in range(num_stocks)]
        
        router = ExchangeRouter(exchange="NSE")
        processor = BulkProcessor(router)
        
        # Mock the fetch to always succeed
        mock_merged = MergedStockData(
            symbol="TEST",
            equity_data=pd.DataFrame(),
            call_data=pd.DataFrame(),
            put_data=pd.DataFrame()
        )
        
        with patch.object(processor, '_fetch_stock_data', return_value=mock_merged):
            params = FetchParams(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31)
            )
            result = processor.process_stocks(symbols, params)
        
        total_processed = result.success_count + result.failure_count
        assert total_processed == num_stocks, f"Expected {num_stocks}, got {total_processed}"

    @given(symbols=st.lists(
        st.sampled_from(["RELIANCE", "TCS", "INFY", "HDFC", "ICICI"]),
        min_size=1,
        max_size=10,
        unique=True
    ))
    @settings(max_examples=100, deadline=None)
    def test_no_stock_missing_or_duplicated(self, symbols):
        """Test that no stock is missing or duplicated in results."""
        router = ExchangeRouter(exchange="NSE")
        processor = BulkProcessor(router)
        
        mock_merged = MergedStockData(
            symbol="TEST",
            equity_data=pd.DataFrame(),
            call_data=pd.DataFrame(),
            put_data=pd.DataFrame()
        )
        
        with patch.object(processor, '_fetch_stock_data', return_value=mock_merged):
            params = FetchParams(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31)
            )
            result = processor.process_stocks(symbols, params)
        
        # All symbols should appear exactly once
        all_symbols = list(result.successful.keys()) + list(result.failed.keys())
        assert len(all_symbols) == len(symbols)
        assert set(all_symbols) == set(symbols)


class TestBulkProcessingFaultTolerance:
    """
    **Feature: quantum-market-suite, Property 7: Bulk Processing Fault Tolerance**
    **Validates: Requirements 4.4**
    
    For any bulk processing operation where one stock fails, the remaining
    stocks SHALL still be processed, and the final result SHALL contain data
    for all successfully processed stocks.
    """
    
    @given(
        num_stocks=st.integers(min_value=2, max_value=10),
        fail_index=st.integers(min_value=0, max_value=9)
    )
    @settings(max_examples=100, deadline=None)
    def test_continues_after_failure(self, num_stocks: int, fail_index: int):
        """Test that processing continues after a single stock fails."""
        fail_index = fail_index % num_stocks  # Ensure valid index
        symbols = [f"STOCK{i}" for i in range(num_stocks)]
        
        router = ExchangeRouter(exchange="NSE")
        processor = BulkProcessor(router)
        
        def mock_fetch(symbol, params):
            if symbol == symbols[fail_index]:
                raise Exception("Simulated failure")
            return MergedStockData(
                symbol=symbol,
                equity_data=pd.DataFrame(),
                call_data=pd.DataFrame(),
                put_data=pd.DataFrame()
            )
        
        with patch.object(processor, '_fetch_stock_data', side_effect=mock_fetch):
            params = FetchParams(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31)
            )
            result = processor.process_stocks(symbols, params)
        
        # Should have processed all stocks
        assert result.total_count == num_stocks
        
        # Exactly one should have failed
        assert result.failure_count == 1
        assert symbols[fail_index] in result.failed
        
        # Rest should have succeeded
        assert result.success_count == num_stocks - 1

    @given(
        num_stocks=st.integers(min_value=3, max_value=10),
        num_failures=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100, deadline=None)
    def test_multiple_failures_handled(self, num_stocks: int, num_failures: int):
        """Test that multiple failures are handled correctly."""
        num_failures = min(num_failures, num_stocks - 1)  # At least one success
        symbols = [f"STOCK{i}" for i in range(num_stocks)]
        fail_symbols = set(symbols[:num_failures])
        
        router = ExchangeRouter(exchange="NSE")
        processor = BulkProcessor(router)
        
        def mock_fetch(symbol, params):
            if symbol in fail_symbols:
                raise Exception(f"Simulated failure for {symbol}")
            return MergedStockData(
                symbol=symbol,
                equity_data=pd.DataFrame(),
                call_data=pd.DataFrame(),
                put_data=pd.DataFrame()
            )
        
        with patch.object(processor, '_fetch_stock_data', side_effect=mock_fetch):
            params = FetchParams(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31)
            )
            result = processor.process_stocks(symbols, params)
        
        # All stocks should be accounted for
        assert result.total_count == num_stocks
        assert result.failure_count == num_failures
        assert result.success_count == num_stocks - num_failures


class TestBulkProcessorProgressTracking:
    """Tests for progress tracking functionality."""
    
    def test_progress_callback_called(self):
        """Test that progress callback is called for each stock."""
        symbols = ["STOCK1", "STOCK2", "STOCK3"]
        progress_calls = []
        
        def track_progress(symbol, progress):
            progress_calls.append((symbol, progress))
        
        router = ExchangeRouter(exchange="NSE")
        processor = BulkProcessor(router)
        
        mock_merged = MergedStockData(
            symbol="TEST",
            equity_data=pd.DataFrame(),
            call_data=pd.DataFrame(),
            put_data=pd.DataFrame()
        )
        
        with patch.object(processor, '_fetch_stock_data', return_value=mock_merged):
            params = FetchParams(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31)
            )
            processor.process_stocks(symbols, params, progress_callback=track_progress)
        
        # Should have progress calls for each stock plus final
        assert len(progress_calls) >= len(symbols)
        
        # Final call should be 100%
        assert progress_calls[-1][1] == 100.0


class TestBulkProcessorSummary:
    """Tests for processing summary generation."""
    
    def test_summary_generation(self):
        """Test that summary is generated correctly."""
        router = ExchangeRouter(exchange="NSE")
        processor = BulkProcessor(router)
        
        mock_merged = MergedStockData(
            symbol="TEST",
            equity_data=pd.DataFrame(),
            call_data=pd.DataFrame(),
            put_data=pd.DataFrame()
        )
        
        with patch.object(processor, '_fetch_stock_data', return_value=mock_merged):
            params = FetchParams(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31)
            )
            result = processor.process_stocks(["STOCK1", "STOCK2"], params)
        
        summary = processor.get_processing_summary(result)
        
        assert summary.total_stocks == 2
        assert len(summary.successful_stocks) == 2
        assert summary.total_time_seconds >= 0
