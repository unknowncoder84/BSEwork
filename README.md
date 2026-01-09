# ⚡ Quantum Market Suite

NSE & BSE Unified Data Platform - Fetch, merge, and export Equity + Derivative data.

## Features

- **Dual Data Engine**: Fetch Equity (OHLCV) and Derivative (Call/Put LTP, OI) data
- **Unified Single-Row Format**: Merges Equity + Derivative data by Date using `pd.merge()`
- **Multi-Stock Selection**: Process multiple stocks sequentially
- **Multi-Tab Excel Export**: Single .xlsx file with individual tabs per company
- **Glassmorphism UI**: Dark/Light theme with persistent settings
- **Persistent Notepad**: Notes saved to config.json

## Output Columns

```
Date, Series, EQ Close, Strike Price, Call LTP, Put LTP, Call IO, Put IO, Open, High, Low, Close, Volume, Open Interest
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and deploy

The `packages.txt` file includes Chromium for Selenium support.

## Tech Stack

- Streamlit (UI)
- Pandas (Data processing)
- Selenium + Chromium (Web scraping)
- OpenPyXL (Excel export)

## Files

- `app.py` - Main Streamlit application
- `packages.txt` - System dependencies (chromium, chromium-driver)
- `requirements.txt` - Python dependencies
- `config.json` - Persistent storage (notepad, history, theme)

## License

MIT
