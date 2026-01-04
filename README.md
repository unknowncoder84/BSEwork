# 📊 BSE Multi-Stock Option Management Suite

A professional, futuristic web application for fetching and merging historical Call & Put options data from BSE India for multiple stocks simultaneously.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🚀 Features

### Multi-Stock Processing
- **Multi-Select Dropdown**: Choose from 50+ top BSE stocks and indices
- **Batch Processing**: Fetch data for multiple stocks in one click
- **Real-time Progress**: See progress bar with current stock being processed
- **Loop Engine**: Automatically fetches Call → Put → Merge for each stock

### Data Management
- **Multi-Sheet Excel Export**: Each stock gets its own sheet + Summary sheet
- **Download History**: Track your last 5 successful downloads
- **Data Preview**: View data in tabs for each stock

### Professional UI
- **Futuristic Dark Theme**: Gradient backgrounds with cyan/green accents
- **Responsive Design**: Works on desktop and mobile
- **Loading Animations**: Progress bars and status updates

### Cloud-Ready
- **Headless Mode**: Configured for server deployment
- **Streamlit Cloud Compatible**: Includes `packages.txt` for free hosting
- **Zero-Cost**: Uses only free, open-source libraries

## 📋 Prerequisites

- Python 3.8 or higher
- Google Chrome browser (for local Selenium)
- Internet connection

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bse-derivative-downloader
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. The `packages.txt` file will automatically install Chromium

## 🚀 Running the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## 📖 Usage

### 1. Select Stocks
- Use the multi-select dropdown to choose stocks
- Click "Top 10" for quick selection of popular stocks
- Click "Clear" to reset selection

### 2. Configure Parameters
- **Instrument Type**: Equity Options or Index Options
- **Expiry Date**: Option expiry date
- **Strike Price**: Target strike price
- **Date Range**: Historical data period

### 3. Process Data
- Click "Process All Stocks" button
- Watch the progress bar: "Fetching 2 of 5: TATA POWER"
- View results in tabbed interface

### 4. Download
- Click "Download Excel" to get multi-sheet file
- Each stock has its own sheet
- Summary sheet shows overview of all stocks

## 📁 Project Structure

```
bse-derivative-downloader/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── packages.txt              # System packages for Streamlit Cloud
├── README.md                 # This file
├── components/
│   ├── __init__.py
│   ├── scraper.py           # Selenium web scraper
│   ├── processor.py         # Data processing and merging
│   └── excel_generator.py   # Multi-sheet Excel generation
├── utils/
│   ├── __init__.py
│   ├── models.py            # Data models and validation
│   ├── stock_list.py        # BSE stock list
│   └── history.py           # Download history management
└── tests/                   # Property-based tests
```

## 📊 Output Format

### Individual Stock Sheets
| Date | Strike Price | Call LTP | Call OI | Put LTP | Put OI |
|------|--------------|----------|---------|---------|--------|
| 01-Jan-2024 | 1000 | 125.50 | 50000 | 98.25 | 45000 |

### Summary Sheet
| Stock | Total Records | Call Records | Put Records | Date Range |
|-------|---------------|--------------|-------------|------------|
| RELIANCE | 20 | 20 | 20 | 01-Jan to 31-Jan |
| TCS | 18 | 18 | 18 | 01-Jan to 31-Jan |

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_processor.py -v

# Run with coverage
pytest tests/ -v --cov=components --cov=utils
```

## ⚠️ Known Limitations

1. **BSE Website Changes**: Scraper may need updates if BSE modifies their site
2. **Rate Limiting**: Processing many stocks may trigger rate limits
3. **CAPTCHA**: Bot detection may occasionally require manual intervention
4. **Demo Mode**: Falls back to demo data if scraping fails

## 🔧 Troubleshooting

### Chrome Driver Issues
```bash
pip install --upgrade webdriver-manager undetected-chromedriver
```

### Streamlit Cloud Issues
- Ensure `packages.txt` contains `chromium` and `chromium-driver`
- Check that all dependencies are in `requirements.txt`

### No Data Found
- Verify stock symbols are correct
- Check if data exists for the specified date range
- Ensure strike price is valid for the selected expiry

## 📝 License

This project is for educational purposes only. Please verify data accuracy before use in any financial decisions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Disclaimer**: This tool is for educational purposes only. The data fetched from BSE India is subject to their terms of service. Always verify data accuracy before making any financial decisions.
