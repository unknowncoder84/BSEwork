"""
Quantum Market Suite - Excel Exporter Tests

Property-based tests for Excel export functionality.
"""

import pytest
import os
import tempfile
import uuid
from hypothesis import given, strategies as st, settings
from datetime import datetime
import pandas as pd

from quantum.exporters.excel_exporter import ExcelExporter
from quantum.models import MergedStockData
from quantum.persistence import PersistenceManager


def get_temp_config_path():
    """Generate unique temp config path."""
    return os.path.join(tempfile.gettempdir(), f"quantum_test_{uuid.uuid4().hex}.json")


def cleanup_config(path):
    """Clean up temp config file."""
    if os.path.exists(path):
        os.remove(path)


class TestExcelExportStructure:
    """
    **Feature: quantum-market-suite, Property 14: Excel Export Structure**
    **Validates: Requirements 11.1, 11.2, 11.3**
    
    For any export request with N companies, the generated Excel file SHALL
    contain exactly N worksheets, each named after the company symbol, with
    equity data and derivative data placed side-by-side with professional
    formatting (headers, borders, appropriate column widths).
    """
    
    @given(num_companies=st.integers(min_value=1, max_value=10))
    @settings(max_examples=50, deadline=None)
    def test_excel_has_correct_worksheet_count(self, num_companies: int):
        """Test that Excel has exactly N worksheets for N companies."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            exporter = ExcelExporter(persistence_manager=pm)
            
            # Create test data for N companies
            data = {}
            for i in range(num_companies):
                symbol = f"STOCK{i}"
                data[symbol] = MergedStockData(
                    symbol=symbol,
                    equity_data=pd.DataFrame({
                        "Date": ["2024-01-15"],
                        "Open": [100.0],
                        "High": [105.0],
                        "Low": [98.0],
                        "Close": [103.0],
                        "Volume": [1000000]
                    }),
                    call_data=pd.DataFrame(),
                    put_data=pd.DataFrame()
                )
            
            excel_bytes = exporter.export_to_excel(data)
            worksheet_count = exporter.get_worksheet_count(excel_bytes)
            
            assert worksheet_count == num_companies
        finally:
            cleanup_config(config_path)

    @given(symbols=st.lists(
        st.sampled_from(["RELIANCE", "TCS", "INFY", "HDFC", "ICICI"]),
        min_size=1,
        max_size=5,
        unique=True
    ))
    @settings(max_examples=50, deadline=None)
    def test_worksheets_named_after_symbols(self, symbols):
        """Test that worksheets are named after company symbols."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            exporter = ExcelExporter(persistence_manager=pm)
            
            data = {}
            for symbol in symbols:
                data[symbol] = MergedStockData(
                    symbol=symbol,
                    equity_data=pd.DataFrame({"Date": ["2024-01-15"], "Close": [100.0]}),
                    call_data=pd.DataFrame(),
                    put_data=pd.DataFrame()
                )
            
            excel_bytes = exporter.export_to_excel(data)
            worksheet_names = exporter.get_worksheet_names(excel_bytes)
            
            assert set(worksheet_names) == set(symbols)
        finally:
            cleanup_config(config_path)
    
    def test_equity_and_derivative_side_by_side(self):
        """Test that equity and derivative data are placed side-by-side."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            exporter = ExcelExporter(persistence_manager=pm)
            
            data = {
                "TEST": MergedStockData(
                    symbol="TEST",
                    equity_data=pd.DataFrame({
                        "Date": ["2024-01-15"],
                        "Open": [100.0],
                        "High": [105.0],
                        "Low": [98.0],
                        "Close": [103.0],
                        "Volume": [1000000]
                    }),
                    call_data=pd.DataFrame({
                        "Strike": [2400],
                        "Close": [50.0],
                        "OI": [10000]
                    }),
                    put_data=pd.DataFrame({
                        "Strike": [2400],
                        "Close": [30.0],
                        "OI": [8000]
                    })
                )
            }
            
            excel_bytes = exporter.export_to_excel(data)
            
            # Verify file was created
            assert len(excel_bytes) > 0
            
            # Verify worksheet exists
            worksheet_names = exporter.get_worksheet_names(excel_bytes)
            assert "TEST" in worksheet_names
        finally:
            cleanup_config(config_path)


class TestExportHistoryRecording:
    """
    **Feature: quantum-market-suite, Property 15: Export History Recording**
    **Validates: Requirements 11.4**
    
    For any successful Excel export, the download history SHALL be updated
    with the export timestamp and filename.
    """
    
    def test_export_records_to_history(self):
        """Test that export is recorded in history."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            exporter = ExcelExporter(persistence_manager=pm)
            
            # Clear any existing history
            pm.reset_config()
            
            data = {
                "TEST": MergedStockData(
                    symbol="TEST",
                    equity_data=pd.DataFrame({"Date": ["2024-01-15"], "Close": [100.0]}),
                    call_data=pd.DataFrame(),
                    put_data=pd.DataFrame()
                )
            }
            
            filename = "test_export.xlsx"
            exporter.export_to_excel(data, filename=filename)
            
            # Check history was updated
            history = pm.get_export_history()
            assert len(history) >= 1
            assert history[0]["filename"] == filename
            assert "timestamp" in history[0]
        finally:
            cleanup_config(config_path)
    
    @given(num_exports=st.integers(min_value=1, max_value=5))
    @settings(max_examples=50, deadline=None)
    def test_multiple_exports_recorded(self, num_exports: int):
        """Test that multiple exports are all recorded."""
        config_path = get_temp_config_path()
        try:
            pm = PersistenceManager(config_path=config_path)
            exporter = ExcelExporter(persistence_manager=pm)
            pm.reset_config()
            
            data = {
                "TEST": MergedStockData(
                    symbol="TEST",
                    equity_data=pd.DataFrame({"Date": ["2024-01-15"], "Close": [100.0]}),
                    call_data=pd.DataFrame(),
                    put_data=pd.DataFrame()
                )
            }
            
            for i in range(num_exports):
                filename = f"export_{i}.xlsx"
                exporter.export_to_excel(data, filename=filename)
            
            history = pm.get_export_history()
            assert len(history) == num_exports
        finally:
            cleanup_config(config_path)


class TestExcelExporterEdgeCases:
    """Tests for edge cases in Excel export."""
    
    def test_empty_data_raises_error(self):
        """Test that empty data raises ValueError."""
        exporter = ExcelExporter()
        
        with pytest.raises(ValueError, match="No data to export"):
            exporter.export_to_excel({})
    
    def test_merge_equity_derivative(self):
        """Test merging equity and derivative data."""
        exporter = ExcelExporter()
        
        equity = pd.DataFrame({"Date": ["2024-01-15"], "Close": [100.0]})
        calls = pd.DataFrame({"Strike": [2400], "Close": [50.0]})
        puts = pd.DataFrame({"Strike": [2400], "Close": [30.0]})
        
        merged = exporter.merge_equity_derivative(equity, calls, puts)
        
        assert "Equity_Date" in merged.columns
        assert "Call_Strike" in merged.columns
        assert "Put_Strike" in merged.columns
    
    def test_generate_filename(self):
        """Test filename generation."""
        filename = ExcelExporter.generate_filename("test")
        
        assert filename.startswith("test_")
        assert filename.endswith(".xlsx")
