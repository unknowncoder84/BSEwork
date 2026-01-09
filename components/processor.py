"""
Data processor for merging and formatting BSE derivative data.
"""
import pandas as pd
from typing import List, Optional, Tuple

from utils.models import DataValidationError


# Expected columns in raw data
RAW_COLUMNS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest', 'Strike Price']

# Final merged columns
MERGED_COLUMNS = ['Date', 'Strike Price', 'Call LTP', 'Call OI', 'Put LTP', 'Put OI']


def validate_dataframe(df: pd.DataFrame, option_type: str) -> Tuple[bool, List[str]]:
    """
    Validate that DataFrame has required columns.
    
    Args:
        df: DataFrame to validate
        option_type: "CE" or "PE" for error messages
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if df is None or df.empty:
        errors.append(f"No {option_type} data available")
        return False, errors
    
    # Check for essential columns (flexible matching)
    required_cols = ['date', 'close', 'open interest']
    df_cols_lower = [col.lower().strip() for col in df.columns]
    
    for req_col in required_cols:
        found = any(req_col in col for col in df_cols_lower)
        if not found:
            errors.append(f"Missing required column containing '{req_col}' in {option_type} data")
    
    return len(errors) == 0, errors


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to standard format.
    """
    df = df.copy()
    
    # Create mapping for common column variations
    column_mapping = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        
        if 'date' in col_lower:
            column_mapping[col] = 'Date'
        elif 'strike' in col_lower and 'price' in col_lower:
            column_mapping[col] = 'Strike Price'
        elif col_lower == 'close' or 'ltp' in col_lower or 'last' in col_lower:
            column_mapping[col] = 'Close'
        elif 'open interest' in col_lower or col_lower == 'oi':
            column_mapping[col] = 'Open Interest'
        elif col_lower == 'open':
            column_mapping[col] = 'Open'
        elif col_lower == 'high':
            column_mapping[col] = 'High'
        elif col_lower == 'low':
            column_mapping[col] = 'Low'
        elif 'volume' in col_lower:
            column_mapping[col] = 'Volume'
    
    df = df.rename(columns=column_mapping)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean DataFrame by removing duplicates and invalid rows.
    """
    df = df.copy()
    
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    # Remove duplicate rows
    df = df.drop_duplicates()
    
    # Reset index
    df = df.reset_index(drop=True)
    
    return df


def merge_call_put_data(call_df: pd.DataFrame, put_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge Call and Put DataFrames on Date and Strike Price.
    
    Args:
        call_df: DataFrame with Call options data
        put_df: DataFrame with Put options data
        
    Returns:
        Merged DataFrame with both Call and Put data
    """
    # Normalize column names
    call_df = normalize_column_names(call_df)
    put_df = normalize_column_names(put_df)
    
    # Clean data
    call_df = clean_data(call_df)
    put_df = clean_data(put_df)
    
    # Prepare Call data
    call_cols = {'Date': 'Date'}
    if 'Strike Price' in call_df.columns:
        call_cols['Strike Price'] = 'Strike Price'
    if 'Close' in call_df.columns:
        call_cols['Close'] = 'Call LTP'
    if 'Open Interest' in call_df.columns:
        call_cols['Open Interest'] = 'Call OI'
    
    call_subset = call_df[[c for c in call_cols.keys() if c in call_df.columns]].copy()
    call_subset = call_subset.rename(columns={k: v for k, v in call_cols.items() if k in call_subset.columns})
    
    # Prepare Put data
    put_cols = {'Date': 'Date'}
    if 'Strike Price' in put_df.columns:
        put_cols['Strike Price'] = 'Strike Price'
    if 'Close' in put_df.columns:
        put_cols['Close'] = 'Put LTP'
    if 'Open Interest' in put_df.columns:
        put_cols['Open Interest'] = 'Put OI'
    
    put_subset = put_df[[c for c in put_cols.keys() if c in put_df.columns]].copy()
    put_subset = put_subset.rename(columns={k: v for k, v in put_cols.items() if k in put_subset.columns})
    
    # Determine merge keys
    merge_keys = ['Date']
    if 'Strike Price' in call_subset.columns and 'Strike Price' in put_subset.columns:
        merge_keys.append('Strike Price')
    
    # Merge dataframes
    if merge_keys:
        merged_df = pd.merge(
            call_subset, 
            put_subset, 
            on=merge_keys, 
            how='outer',
            suffixes=('', '_put')
        )
    else:
        # If no common keys, concatenate side by side
        merged_df = pd.concat([call_subset, put_subset], axis=1)
    
    return merged_df


def format_merged_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format merged data with proper column order and fill missing values.
    
    Args:
        df: Merged DataFrame
        
    Returns:
        Formatted DataFrame with columns: Date, Strike Price, Call LTP, Call OI, Put LTP, Put OI
    """
    df = df.copy()
    
    # Ensure all required columns exist
    for col in MERGED_COLUMNS:
        if col not in df.columns:
            df[col] = None
    
    # Reorder columns
    df = df[MERGED_COLUMNS]
    
    # Fill missing values with "N/A"
    df = df.fillna("N/A")
    
    # Convert "N/A" strings for numeric columns where appropriate
    for col in ['Call LTP', 'Call OI', 'Put LTP', 'Put OI']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x if x == "N/A" else x)
    
    return df


def handle_missing_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing data by replacing NaN/None with "N/A".
    
    Args:
        df: DataFrame with potential missing values
        
    Returns:
        DataFrame with missing values replaced by "N/A"
    """
    df = df.copy()
    df = df.fillna("N/A")
    df = df.replace([None, '', 'nan', 'NaN', 'None'], "N/A")
    return df


def validate_merged_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate merged data for referential integrity.
    
    Args:
        df: Merged DataFrame
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if df is None or df.empty:
        errors.append("Merged data is empty")
        return False, errors
    
    # Check that Date column has valid values
    if 'Date' in df.columns:
        invalid_dates = df[df['Date'].isin(["N/A", None, ""])].shape[0]
        if invalid_dates == len(df):
            errors.append("All date values are missing or invalid")
    else:
        errors.append("Date column is missing")
    
    # Check that Strike Price column has valid values
    if 'Strike Price' in df.columns:
        invalid_strikes = df[df['Strike Price'].isin(["N/A", None, ""])].shape[0]
        if invalid_strikes == len(df):
            errors.append("All strike price values are missing or invalid")
    
    return len(errors) == 0, errors


def process_derivative_data(call_df: pd.DataFrame, put_df: pd.DataFrame) -> pd.DataFrame:
    """
    Main function to process and merge derivative data.
    
    Args:
        call_df: Raw Call options DataFrame
        put_df: Raw Put options DataFrame
        
    Returns:
        Processed and merged DataFrame
    """
    # Validate input data
    call_valid, call_errors = validate_dataframe(call_df, "Call")
    put_valid, put_errors = validate_dataframe(put_df, "Put")
    
    # If both are invalid, raise error
    if not call_valid and not put_valid:
        raise DataValidationError(f"Invalid data: {'; '.join(call_errors + put_errors)}")
    
    # Merge data
    merged_df = merge_call_put_data(call_df, put_df)
    
    # Format merged data
    formatted_df = format_merged_data(merged_df)
    
    # Handle missing data
    final_df = handle_missing_data(formatted_df)
    
    # Validate final result
    is_valid, errors = validate_merged_data(final_df)
    if not is_valid:
        # Log warnings but don't fail
        print(f"Data validation warnings: {errors}")
    
    return final_df
