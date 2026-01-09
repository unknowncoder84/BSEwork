# Design Document

## Overview

The NSE India Scraper is a Python-based web application that automates the extraction of both Equity (EQ) and Options (OPT) data from the National Stock Exchange of India website. The system follows a modular architecture with separate components for scraping, data processing, persistence, and UI rendering.

The application uses Selenium with undetected-chromedriver for anti-bot bypass, implements robust error handling with exponential backoff, and provides a professional "Quantum" UI with glassmorphism design. All user settings persist to config.json for long-term storage without requiring a database.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                            │
│  (Glassmorphism Theme, Calendar Widget, Multi-Select, Notepad)  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Application Controller                         │
│         (Orchestrates workflow, manages state)                   │
└────────┬───────────────────────────────────────┬────────────────┘
         │                                       │
         ▼                                       ▼
┌──────────────────────┐              ┌──────────────────────────┐
│   NSE Scraper        │              │   Persistence Manager    │
│   ├─ Equity Scraper  │              │   (config.json)          │
│   └─ Options Scraper │              │   ├─ Theme               │
└──────────┬───────────┘              │   ├─ Notepad             │
           │                          │   ├─ History             │
           ▼                          │   └─ Custom Tickers      │
┌──────────────────────┐              └──────────────────────────┘
│   Data Processor     │
│   (Merge, Format)    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Excel Generator    │
│   (Multi-tab Export) │
└──────────────────────┘
```

### Data Flow

1. User selects stocks, dates, strike price, and option type in UI
2. Application Controller validates inputs and initiates scraping
3. NSE Scraper fetches Equity data from eq_security page
4. NSE Scraper fetches Options data from fo_eq_hist_contract_wise page
5. Data Processor merges EQ and OPT data by Date
6. UI displays merged data in unified format
7. Excel Generator creates multi-tab export on user request
8. Persistence Manager saves settings after each change

## Components and Interfaces

### 1. NSE Scraper Component (`nse_scraper.py`)

**Responsibilities:**
- Initialize undetected-chromedriver with anti-bot configuration
- Navigate to NSE Equity and Options pages
- Handle dynamic dropdown population with WebDriverWait
- Extract data tables and convert to DataFrames
- Implement random delays and exponential backoff

**Key Functions:**
```python
def initialize_driver() -> webdriver.Chrome:
    """Creates undetected Chrome driver with NSE-specific headers"""
    
def fetch_equity_data(symbol: str, from_date: date, to_date: date) -> pd.DataFrame:
    """Fetches equity price-volume data from NSE"""
    
def fetch_options_data(symbol: str, expiry_date: date, strike_price: float, 
                       option_type: str, from_date: date, to_date: date) -> pd.DataFrame:
    """Fetches options contract data from NSE"""
    
def wait_for_strike_dropdown(driver: webdriver.Chrome, timeout: int = 15) -> List[str]:
    """Waits for strike price dropdown to populate and returns available options"""
    
def add_human_delay(min_seconds: float = 3.0, max_seconds: float = 6.0):
    """Adds random delay to mimic human behavior"""
```

**Anti-Bot Configuration:**
```python
options = uc.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Critical headers for NSE
driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
    'headers': {
        'Referer': 'https://www.nseindia.com/',
        'User-Agent': get_random_user_agent()
    }
})
```

### 2. Data Processor Component (`data_processor.py`)

**Responsibilities:**
- Normalize column names from NSE data
- Add Series column (EQ/OPT) to data
- Set OI to "-" for equity data
- Merge equity and options data by Date
- Sort merged data by Date

**Key Functions:**
```python
def process_equity_data(df: pd.DataFrame) -> pd.DataFrame:
    """Adds Series='EQ' and OI='-' to equity data"""
    
def process_options_data(df: pd.DataFrame) -> pd.DataFrame:
    """Adds Series='OPT' to options data"""
    
def merge_equity_options(equity_df: pd.DataFrame, options_df: pd.DataFrame) -> pd.DataFrame:
    """Merges EQ and OPT data, sorted by Date"""
    
def format_unified_data(df: pd.DataFrame) -> pd.DataFrame:
    """Ensures columns: Date, Series, Open, High, Low, Close, Volume, Open Interest"""
```

### 3. Persistence Manager Component (`persistence.py`)

**Responsibilities:**
- Load/save all settings to config.json
- Manage theme preference (dark/light)
- Store notepad content
- Track fetch history with timestamps
- Maintain custom ticker lists

**Key Functions:**
```python
def load_config() -> dict:
    """Loads all settings from config.json"""
    
def save_config(config: dict):
    """Saves all settings to config.json"""
    
def get_theme() -> str:
    """Returns current theme ('dark' or 'light')"""
    
def set_theme(theme: str):
    """Sets and persists theme preference"""
    
def get_notepad() -> str:
    """Returns saved notepad content"""
    
def save_notepad(content: str):
    """Saves notepad content"""
    
def add_history_entry(entry: dict):
    """Adds fetch history entry with timestamp"""
    
def get_history() -> List[dict]:
    """Returns fetch history"""
```

### 4. Excel Generator Component (`excel_generator.py`)

**Responsibilities:**
- Create Excel workbook with multiple tabs
- Name tabs by company symbol
- Apply professional formatting
- Generate descriptive filename

**Key Functions:**
```python
def create_multi_company_excel(data: Dict[str, pd.DataFrame], 
                                from_date: date, to_date: date) -> bytes:
    """Creates Excel with one tab per company"""
    
def generate_filename(companies: List[str], from_date: date, to_date: date) -> str:
    """Generates filename with company names and date range"""
    
def apply_formatting(worksheet, df: pd.DataFrame):
    """Applies headers, alternating row colors, column widths"""
```

### 5. UI Controller Component (`quantum_ui.py`)

**Responsibilities:**
- Render glassmorphism theme (dark/light)
- Provide calendar widgets for date selection
- Multi-select for stock symbols
- Display progress and error messages
- Notepad and history panels

**Key Functions:**
```python
def apply_glassmorphism_theme(is_dark: bool):
    """Applies CSS for glassmorphism effect"""
    
def render_sidebar() -> dict:
    """Renders sidebar with all inputs, returns parameters"""
    
def render_calendar_widget(label: str, default: date) -> date:
    """Renders date picker with calendar"""
    
def display_progress(current: int, total: int, message: str):
    """Shows progress bar with status"""
    
def display_data_preview(df: pd.DataFrame):
    """Renders data table with unified format"""
```

## Data Models

### Unified Data Format
```python
UNIFIED_COLUMNS = [
    'Date',           # Trading date
    'Series',         # 'EQ' or 'OPT'
    'Open',           # Opening price
    'High',           # High price
    'Low',            # Low price
    'Close',          # Closing price
    'Volume',         # Trading volume
    'Open Interest'   # OI (numeric for OPT, '-' for EQ)
]
```

### Fetch Parameters
```python
@dataclass
class NSEFetchParameters:
    symbol: str
    from_date: date
    to_date: date
    fetch_equity: bool = True
    fetch_options: bool = True
    expiry_date: Optional[date] = None
    strike_price: Optional[float] = None
    option_type: Optional[str] = None  # 'CE' or 'PE'
```

### Config Schema
```python
config_schema = {
    "theme": "dark",  # or "light"
    "notepad": "",
    "history": [
        {
            "timestamp": "2026-01-06T10:30:00",
            "symbols": ["RELIANCE", "TCS"],
            "from_date": "2025-12-01",
            "to_date": "2026-01-06",
            "status": "success"
        }
    ],
    "custom_tickers": ["CUSTOMSYM1", "CUSTOMSYM2"]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Unified output structure
*For any* data returned by the Data_Processor, the output DataFrame SHALL contain exactly these columns in order: Date, Series, Open, High, Low, Close, Volume, Open Interest.
**Validates: Requirements 1.1**

### Property 2: Series and OI consistency
*For any* row in the output data:
- If Series is "EQ", then Open Interest SHALL be "-"
- If Series is "OPT", then Open Interest SHALL be a numeric value (not "-")
**Validates: Requirements 1.2, 1.3, 1.4, 1.5**

### Property 3: Merged data is sorted by Date
*For any* merged dataset containing both EQ and OPT rows, the Date column SHALL be in ascending chronological order.
**Validates: Requirements 1.6**

### Property 4: Persistence round-trip consistency
*For any* configuration data (theme, notepad, history, custom_tickers), saving to config.json and then loading SHALL return equivalent data.
**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**

### Property 5: Excel structure validation
*For any* list of company symbols and their data:
- The Excel file SHALL have exactly one tab per company
- Each tab name SHALL match the company symbol
- Each tab SHALL contain the unified column headers
**Validates: Requirements 9.2, 9.3, 9.4**

### Property 6: Excel merge preserves all data
*For any* equity DataFrame and options DataFrame for the same company, the merged Excel tab SHALL contain all unique dates from both datasets.
**Validates: Requirements 9.1**

### Property 7: Filename includes context
*For any* list of company symbols and date range, the generated filename SHALL contain at least one company symbol and both dates.
**Validates: Requirements 9.7**

### Property 8: Human delay is within bounds
*For any* call to add_human_delay(min, max), the actual delay SHALL be >= min and <= max seconds.
**Validates: Requirements 8.5, 8.6**

## Error Handling

### Error Categories

**1. Network Errors**
```python
class NSEConnectionError(Exception):
    """Raised when unable to connect to NSE website"""
    message = "Unable to connect to NSE. Please check your internet connection"
```

**2. Symbol Not Found**
```python
class SymbolNotFoundError(Exception):
    """Raised when stock symbol is not found on NSE"""
    def __init__(self, symbol: str):
        self.message = f"Stock symbol '{symbol}' not found on NSE"
```

**3. Strike Price Not Available**
```python
class StrikePriceNotAvailableError(Exception):
    """Raised when strike price is not available for the expiry"""
    def __init__(self, strike_price: float):
        self.message = f"Strike Price {strike_price} not available for this expiry"
```

**4. Rate Limiting (403 Error)**
```python
class RateLimitError(Exception):
    """Raised when NSE blocks requests"""
    message = "NSE is blocking requests. Please try again later"
```

### Exponential Backoff Strategy
```python
def fetch_with_retry(fetch_func, max_retries=3):
    delays = [5, 10, 20]  # seconds
    for attempt in range(max_retries):
        try:
            return fetch_func()
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(delays[attempt])
            else:
                raise
```

## Testing Strategy

### Unit Tests
- Test data processor functions with sample DataFrames
- Test persistence manager with mock config.json
- Test Excel generator with sample data
- Test filename generation with various inputs

### Property-Based Tests (using Hypothesis)

**Test 1: Unified Output Structure**
```python
# Feature: nse-india-scraper, Property 1: Unified output structure
@given(equity_data=dataframes(...), options_data=dataframes(...))
@settings(max_examples=100)
def test_unified_output_structure(equity_data, options_data):
    result = merge_equity_options(equity_data, options_data)
    assert list(result.columns) == UNIFIED_COLUMNS
```

**Test 2: Series and OI Consistency**
```python
# Feature: nse-india-scraper, Property 2: Series and OI consistency
@given(merged_data=dataframes(...))
@settings(max_examples=100)
def test_series_oi_consistency(merged_data):
    for _, row in merged_data.iterrows():
        if row['Series'] == 'EQ':
            assert row['Open Interest'] == '-'
        elif row['Series'] == 'OPT':
            assert row['Open Interest'] != '-'
```

**Test 3: Persistence Round-Trip**
```python
# Feature: nse-india-scraper, Property 4: Persistence round-trip consistency
@given(config=dictionaries(...))
@settings(max_examples=100)
def test_persistence_roundtrip(config):
    save_config(config)
    loaded = load_config()
    assert loaded == config
```

### Integration Tests
- Test full scraping workflow with mocked NSE responses
- Test multi-stock fetch with progress tracking
- Test error recovery and retry logic

## Implementation Notes

### Technology Stack
- **Python 3.8+**: Core language
- **Streamlit 1.28+**: Web UI framework
- **undetected-chromedriver**: Anti-bot browser automation
- **Selenium 4.15+**: WebDriver support
- **Pandas 2.0+**: Data manipulation
- **Openpyxl 3.1+**: Excel generation
- **Hypothesis 6.92+**: Property-based testing

### NSE-Specific Considerations

1. **Session Cookies**: NSE requires valid session cookies. The scraper should first visit the main page to establish a session before accessing data pages.

2. **Dynamic Dropdowns**: Strike price dropdown populates asynchronously after expiry selection. Always use WebDriverWait with EC.presence_of_all_elements_located.

3. **Rate Limiting**: NSE aggressively rate-limits automated requests. Implement delays of 3-6 seconds between major actions.

4. **Data Format**: NSE returns data in various formats. The processor must handle date format variations (DD-MMM-YYYY, YYYY-MM-DD).

### Glassmorphism CSS
```css
.glass-panel {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}
```

## Deployment Considerations

### Cloud Deployment (Streamlit Cloud)
- Use headless Chrome with `--headless=new` flag
- Install Chrome via `packages.txt`: `chromium`, `chromium-driver`
- Set appropriate timeouts for cloud environment

### Local Development
```bash
pip install -r requirements.txt
streamlit run nse_app.py
```

### Requirements
```
streamlit>=1.28.0
undetected-chromedriver>=3.5.0
selenium>=4.15.0
pandas>=2.0.0
openpyxl>=3.1.0
hypothesis>=6.92.0
```
