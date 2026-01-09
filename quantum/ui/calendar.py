"""
Quantum Market Suite - Quantum Calendar

Date picker component with expiry date highlighting and validation.
"""

import streamlit as st
from datetime import date, timedelta
from typing import Optional, List, Tuple

from quantum.models import ValidationResult


class QuantumCalendar:
    """Date picker with expiry highlighting and validation."""
    
    def __init__(self, key_prefix: str = "quantum_cal"):
        """Initialize calendar component."""
        self.key_prefix = key_prefix
        self._expiry_dates: List[date] = []
    
    def set_expiry_dates(self, expiries: List[date]) -> None:
        """Set known derivative expiry dates for highlighting."""
        self._expiry_dates = expiries
    
    def render_date_range_picker(
        self,
        label: str = "Select Date Range",
        default_start: Optional[date] = None,
        default_end: Optional[date] = None,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None
    ) -> Tuple[date, date]:
        """Render date range picker with validation."""
        # Set defaults
        if default_start is None:
            default_start = date.today() - timedelta(days=30)
        if default_end is None:
            default_end = date.today()
        if min_date is None:
            min_date = date(2010, 1, 1)
        if max_date is None:
            max_date = date.today()
        
        st.markdown(f"**{label}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=default_start,
                min_value=min_date,
                max_value=max_date,
                key=f"{self.key_prefix}_start"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=default_end,
                min_value=min_date,
                max_value=max_date,
                key=f"{self.key_prefix}_end"
            )
        
        # Validate and show error if invalid
        validation = self.validate_date_range(start_date, end_date)
        if not validation.is_valid:
            st.error(validation.error_message)
        
        return start_date, end_date

    def render_expiry_picker(
        self,
        label: str = "Select Expiry Date",
        expiry_dates: Optional[List[date]] = None
    ) -> Optional[date]:
        """Render expiry date picker with highlighting."""
        dates = expiry_dates or self._expiry_dates
        
        if not dates:
            st.info("No expiry dates available")
            return None
        
        # Format dates for display
        date_options = {d.strftime("%d %b %Y"): d for d in sorted(dates)}
        
        selected = st.selectbox(
            label,
            options=list(date_options.keys()),
            key=f"{self.key_prefix}_expiry"
        )
        
        return date_options.get(selected)
    
    def validate_date_range(self, start_date: date, end_date: date) -> ValidationResult:
        """Validate date range selection."""
        if end_date < start_date:
            return ValidationResult.invalid(
                "End date cannot be before start date"
            )
        
        if start_date > date.today():
            return ValidationResult.invalid(
                "Start date cannot be in the future"
            )
        
        # Check if range is reasonable (max 2 years)
        days_diff = (end_date - start_date).days
        if days_diff > 730:
            return ValidationResult.invalid(
                "Date range cannot exceed 2 years"
            )
        
        return ValidationResult.valid()
    
    def is_expiry_date(self, check_date: date) -> bool:
        """Check if a date is a known expiry date."""
        return check_date in self._expiry_dates
    
    def get_next_expiry(self, from_date: Optional[date] = None) -> Optional[date]:
        """Get the next expiry date from a given date."""
        from_date = from_date or date.today()
        
        future_expiries = [d for d in self._expiry_dates if d >= from_date]
        
        if future_expiries:
            return min(future_expiries)
        return None
    
    def render_quick_select(self) -> Tuple[date, date]:
        """Render quick date range selection buttons."""
        st.markdown("**Quick Select**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        today = date.today()
        
        with col1:
            if st.button("1 Week", key=f"{self.key_prefix}_1w"):
                return today - timedelta(days=7), today
        
        with col2:
            if st.button("1 Month", key=f"{self.key_prefix}_1m"):
                return today - timedelta(days=30), today
        
        with col3:
            if st.button("3 Months", key=f"{self.key_prefix}_3m"):
                return today - timedelta(days=90), today
        
        with col4:
            if st.button("1 Year", key=f"{self.key_prefix}_1y"):
                return today - timedelta(days=365), today
        
        # Default return
        return today - timedelta(days=30), today
