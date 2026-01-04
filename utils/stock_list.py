"""
List of top BSE stocks for multi-select dropdown.
"""

# Top BSE Stocks for Options Trading
TOP_BSE_STOCKS = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "INFY",
    "ICICIBANK",
    "HINDUNILVR",
    "SBIN",
    "BHARTIARTL",
    "KOTAKBANK",
    "ITC",
    "LT",
    "AXISBANK",
    "ASIANPAINT",
    "MARUTI",
    "BAJFINANCE",
    "TITAN",
    "SUNPHARMA",
    "ULTRACEMCO",
    "NESTLEIND",
    "WIPRO",
    "HCLTECH",
    "POWERGRID",
    "NTPC",
    "TATAMOTORS",
    "TATASTEEL",
    "ONGC",
    "JSWSTEEL",
    "ADANIENT",
    "ADANIPORTS",
    "TECHM",
    "INDUSINDBK",
    "BAJAJFINSV",
    "GRASIM",
    "DIVISLAB",
    "DRREDDY",
    "CIPLA",
    "EICHERMOT",
    "HEROMOTOCO",
    "BPCL",
    "COALINDIA",
    "M&M",
    "BRITANNIA",
    "APOLLOHOSP",
    "TATACONSUM",
    "HINDALCO",
    "SBILIFE",
    "HDFCLIFE",
    "UPL",
    "SHREECEM",
    "BAJAJ-AUTO"
]

# BSE Index Options
BSE_INDICES = [
    "SENSEX",
    "BANKEX",
    "SENSEX50"
]

def get_all_options():
    """Get combined list of stocks and indices."""
    return TOP_BSE_STOCKS + BSE_INDICES

def get_default_stocks():
    """Get default selection of popular stocks."""
    return ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]
