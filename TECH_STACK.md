# Technology Stack

## Overview
This document lists all the tools, libraries, and technologies used to build the BSE Derivative Data Downloader application.

---

## Core Technologies

### Python 3.8+
- Main programming language
- Used for backend logic, data processing, and web scraping

### Streamlit
- **Version**: 1.28.0+
- **Purpose**: Web application framework
- **Features Used**:
  - Page configuration
  - Sidebar navigation
  - Data input widgets (multiselect, date picker, number input)
  - Session state management
  - File download functionality
  - Progress bars
  - Custom CSS styling

---

## Web Scraping

### Selenium
- **Version**: 4.15.0+
- **Purpose**: Browser automation for scraping BSE website
- **Features Used**:
  - Headless Chrome browser
  - WebDriver management
  - Element location and interaction
  - Explicit waits
  - Form filling and submission

### Undetected ChromeDriver
- **Version**: 3.5.0+
- **Purpose**: Anti-bot detection bypass
- **Features Used**:
  - Stealth mode browsing
  - User-Agent rotation
  - Automation detection prevention

### WebDriver Manager
- **Version**: 4.0.0+
- **Purpose**: Automatic ChromeDriver installation and management
- **Features Used**:
  - Auto-download correct driver version
  - Cross-platform support

---

## Data Processing

### Pandas
- **Version**: 2.0.0+
- **Purpose**: Data manipulation and analysis
- **Features Used**:
  - DataFrame operations
  - Data merging (Call/Put options)
  - Data cleaning and formatting
  - Date range generation
  - CSV/Excel parsing

### OpenPyXL
- **Version**: 3.1.0+
- **Purpose**: Excel file generation
- **Features Used**:
  - Workbook creation
  - Cell formatting and styling
  - Multiple sheet support
  - Column width adjustment
  - Header formatting

### XlsxWriter
- **Version**: 3.1.0+
- **Purpose**: Alternative Excel writer
- **Features Used**:
  - Excel file creation
  - Formatting options

---

## Testing

### Pytest
- **Version**: 7.4.0+
- **Purpose**: Unit testing framework
- **Features Used**:
  - Test discovery
  - Fixtures
  - Assertions
  - Test organization

### Hypothesis
- **Version**: 6.92.0+
- **Purpose**: Property-based testing
- **Features Used**:
  - Random data generation
  - Property verification
  - Edge case discovery
  - Test strategies

---

## Frontend/UI

### Custom CSS
- **Purpose**: Professional dark theme styling
- **Features Used**:
  - Glass morphism effects
  - Gradient backgrounds (indigo/rose theme)
  - Custom card components
  - Responsive design
  - Custom scrollbars
  - Animation effects

### Google Fonts (Inter)
- **Purpose**: Typography
- **Features Used**:
  - Clean, modern font family
  - Multiple font weights

---

## Data Storage

### JSON
- **Purpose**: Local data persistence
- **Features Used**:
  - Configuration storage
  - Download history
  - Custom tickers
  - User preferences

---

## Deployment

### Streamlit Cloud
- **Purpose**: Free cloud hosting
- **Features Used**:
  - GitHub integration
  - Auto-deployment on push
  - Environment management

### GitHub
- **Purpose**: Version control and deployment source
- **Features Used**:
  - Code repository
  - Automatic deployment triggers

---

## System Dependencies

### Chromium
- **Purpose**: Headless browser for web scraping
- **Installation**: Via packages.txt for Streamlit Cloud

### Chromium Driver
- **Purpose**: WebDriver for Chromium
- **Installation**: Via packages.txt for Streamlit Cloud

---

## File Structure

```
BSEwork/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── packages.txt              # System dependencies
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── components/
│   ├── scraper.py            # Selenium web scraper
│   ├── processor.py          # Data processing logic
│   └── excel_generator.py    # Excel file generation
├── utils/
│   ├── models.py             # Data models and validation
│   ├── stock_list.py         # BSE stock list
│   └── persistence.py        # JSON data storage
└── tests/                    # Test files
```

---

## Dependencies Summary

### requirements.txt
```
streamlit>=1.28.0
selenium>=4.15.0
pandas>=2.0.0
openpyxl>=3.1.0
webdriver-manager>=4.0.0
undetected-chromedriver>=3.5.0
hypothesis>=6.92.0
pytest>=7.4.0
xlsxwriter>=3.1.0
```

### packages.txt (System)
```
chromium
chromium-driver
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                       │
│  (User Input, Data Preview, Download, Custom CSS)           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Controller                      │
│         (app.py - Orchestrates workflow)                    │
└────────┬───────────────────────────────┬────────────────────┘
         │                               │
         ▼                               ▼
┌──────────────────────┐      ┌──────────────────────────────┐
│   Selenium Scraper   │      │     Data Processor           │
│   (Web Automation)   │─────▶│  (Pandas - Merge, Clean)     │
└──────────────────────┘      └────────────┬─────────────────┘
         │                                  │
         ▼                                  ▼
┌──────────────────────┐      ┌──────────────────────────────┐
│   BSE India Website  │      │     Excel Generator          │
│  (Data Source)       │      │   (OpenPyXL - File Creation) │
└──────────────────────┘      └──────────────────────────────┘
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Initial | Basic scraping and Excel export |
| 2.0 | Current | Professional UI, multi-stock support, glass morphism design |

---

## Credits

Built with ❤️ using open-source technologies.
