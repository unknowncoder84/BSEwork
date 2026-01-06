# Design Document

## Overview

The BSE Derivative Data Downloader is a Python-based web application that automates the retrieval and processing of historical options data from the BSE India website. The system follows a three-tier architecture: a Streamlit-based presentation layer for user interaction, a Selenium-powered scraping layer for data acquisition, and a Pandas-based processing layer for data transformation and Excel generation.

The application operates by accepting user inputs (company name, expiry date, strike price, date range), automating browser interactions to fetch both Call and Put options data, merging the datasets intelligently, and providing a downloadable Excel file. The design emphasizes reliability, user experience, and compliance with web scraping best practices.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                       │
│  (User Input, Data Preview, Download, Error Display)        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Controller                      │
│         (Orchestrates workflow, handles state)               │
└────────┬───────────────────────────────┬────────────────────┘
         │                               │
         ▼                               ▼
┌──────────────────────┐      ┌──────────────────────────────┐
│   Selenium Scraper   │      │     Data Processor           │
│   (Web Automation)   │─────▶│  (Merge, Clean, Format)      │
└──────────────────────┘      └────────────┬─────────────────┘
         │                                  │
         ▼                                  ▼
┌──────────────────────┐      ┌──────────────────────────────┐
│   BSE India Website  │      │     Excel Generator          │
│  (Data Source)       │      │   (File Creation)            │
└──────────────────────┘      └──────────────────────────────┘
```

### Component Interaction Flow

1. User provides inputs through Streamlit UI
2. Application Controller validates inputs and initiates scraping
3. Selenium Scraper navigates BSE website and extracts Call data
4. Selenium Scraper repeats process for Put data
5. Data Processor merges and cleans both datasets
6. Streamlit UI displays preview of merged data
7. Excel Generator creates downloadable file on user request
8. Streamlit UI provides download link to user

## Components and Interfaces

### 1. Streamlit UI Component (`ui.py`)

**Responsibilities:**
- Render user interface with sidebar and main content area
- Collect user inputs (company name, dates, strike price)
- Display loading states and progress indicators
- Show data preview table
- Provide Excel download functionality
- Display error messages

**Key Functions:**
```python
def render_sidebar() -> dict:
    """Renders input sidebar and returns user parameters"""
    
def display_loading_spinner(message: str):
    """Shows loading animation with status message"""
    
def display_data_preview(df: pd.DataFrame):
    """Renders merged data in table format"""
    
def provide_download_button(excel_file: bytes, filename: str):
    """Creates download button for Excel file"""
    
def display_error(error_type: str, message: str):
    """Shows user-friendly error messages"""
```

### 2. Selenium Scraper Component (`scraper.py`)

**Responsibilities:**
- Initialize headless Chrome browser with anti-detection measures
- Navigate to BSE derivative data page
- Search for company/stock
- Select instrument type (Equity/Index Options)
- Configure date range, expiry, and strike price
- Extract Call options data
- Extract Put options data
- Handle dynamic page loading and waits

**Key Functions:**
```python
def initialize_driver() -> webdriver.Chrome:
    """Creates headless Chrome driver with proper configuration"""
    
def search_company(driver: webdriver.Chrome, company_name: str) -> bool:
    """Searches for company and returns success status"""
    
def select_instrument_type(driver: webdriver.Chrome, instrument_type: str):
    """Selects Equity Options or Index Options"""
    
def configure_parameters(driver: webdriver.Chrome, params: dict):
    """Sets expiry date, strike price, and date range"""
    
def fetch_option_data(driver: webdriver.Chrome, option_type: str) -> pd.DataFrame:
    """Fetches Call or Put data and returns as DataFrame"""
    
def add_human_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """Adds random delay to mimic human behavior"""
```

**Anti-Detection Configuration:**
```python
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
```

### 3. Data Processor Component (`processor.py`)

**Responsibilities:**
- Validate fetched data structure
- Merge Call and Put DataFrames on Date and Strike Price
- Handle missing data with "N/A" values
- Format columns consistently
- Ensure data quality and consistency

**Key Functions:**
```python
def validate_dataframe(df: pd.DataFrame, option_type: str) -> bool:
    """Validates DataFrame has required columns"""
    
def merge_call_put_data(call_df: pd.DataFrame, put_df: pd.DataFrame) -> pd.DataFrame:
    """Merges Call and Put data on Date and Strike Price"""
    
def format_merged_data(df: pd.DataFrame) -> pd.DataFrame:
    """Formats columns and handles missing values"""
    
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Removes duplicates and invalid rows"""
```

### 4. Excel Generator Component (`excel_generator.py`)

**Responsibilities:**
- Convert DataFrame to Excel format
- Apply formatting and styling
- Generate meaningful filename
- Return file as bytes for download

**Key Functions:**
```python
def create_excel_file(df: pd.DataFrame, company_name: str, date_range: tuple) -> bytes:
    """Creates formatted Excel file and returns as bytes"""
    
def generate_filename(company_name: str, from_date: str, to_date: str) -> str:
    """Creates descriptive filename"""
    
def apply_excel_formatting(workbook, worksheet):
    """Applies professional formatting to Excel sheet"""
```

### 5. Application Controller (`app.py`)

**Responsibilities:**
- Orchestrate overall workflow
- Manage application state
- Handle errors and exceptions
- Coordinate between components

**Key Functions:**
```python
def main():
    """Main application entry point"""
    
def fetch_and_merge_data(params: dict) -> pd.DataFrame:
    """Orchestrates data fetching and merging process"""
    
def handle_error(exception: Exception) -> str:
    """Converts exceptions to user-friendly messages"""
```

## Data Models

### User Input Parameters
```python
@dataclass
class FetchParameters:
    company_name: str
    instrument_type: str  # "Equity Options" or "Index Options"
    expiry_date: date
    strike_price: float
    from_date: date
    to_date: date
```

### Raw Options Data (from BSE)
```python
# Expected columns from BSE website
call_columns = ['Date', 'Strike Price', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest']
put_columns = ['Date', 'Strike Price', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest']
```

### Merged Data Structure
```python
merged_columns = [
    'Date',
    'Strike Price',
    'Call Price',  # Close price for Call
    'Call OI',     # Open Interest for Call
    'Put Price',   # Close price for Put
    'Put OI'       # Open Interest for Put
]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Input validation enables action button
*For any* set of user inputs, the "Fetch & Merge Data" button should be enabled if and only if all required fields (company name, instrument type, expiry date, strike price, from date, to date) contain valid values.
**Validates: Requirements 1.5**

### Property 2: Company search handles all valid inputs
*For any* valid company name string, the Selenium Driver should successfully perform a search operation on the BSE website without throwing exceptions.
**Validates: Requirements 2.2**

### Property 3: Parameter configuration is consistent
*For any* valid set of parameters (expiry date, strike price, date range), the Selenium Driver should configure all parameters on the BSE website before fetching data.
**Validates: Requirements 2.4**

### Property 4: Both option types are fetched sequentially
*For any* valid parameter set, when Call options data is successfully fetched, the system should then fetch Put options data using the same parameters.
**Validates: Requirements 2.5, 2.6**

### Property 5: Anti-detection measures are applied consistently
*For any* sequence of Selenium Driver actions, the system should include User-Agent headers and add delays between consecutive actions to mimic human behavior.
**Validates: Requirements 2.8, 2.9, 7.1, 7.2**

### Property 6: Data merge preserves all records
*For any* Call DataFrame and Put DataFrame with matching date ranges, the merged result should contain all unique combinations of Date and Strike Price from both datasets.
**Validates: Requirements 3.1**

### Property 7: Merged data has required structure
*For any* merged dataset, the output DataFrame should contain exactly these columns in order: Date, Strike Price, Call Price, Call OI, Put Price, Put OI.
**Validates: Requirements 3.2**

### Property 8: Missing data is handled gracefully
*For any* merged dataset with missing values, all NaN or None values should be replaced with "N/A" and the operation should complete without raising exceptions.
**Validates: Requirements 3.3, 3.5**

### Property 9: Merged data maintains referential integrity
*For any* merged dataset, every row should have a valid date value and a valid strike price value (not null, not empty).
**Validates: Requirements 3.4**

### Property 10: Excel file contains all merged data
*For any* merged DataFrame, the generated Excel file should contain all rows and columns from the DataFrame with proper headers.
**Validates: Requirements 5.1, 5.4**

### Property 11: Filename includes context information
*For any* company name and date range, the generated Excel filename should contain the company name, from date, and to date in a readable format.
**Validates: Requirements 5.5**

### Property 12: Element interactions wait for readiness
*For any* web element that the Selenium Driver interacts with, the driver should wait for the element to be present and interactable before performing actions.
**Validates: Requirements 7.3**

### Property 13: Retry logic uses exponential backoff
*For any* sequence of retry attempts after failures, the delay between attempts should increase exponentially (e.g., 1s, 2s, 4s, 8s).
**Validates: Requirements 7.5**

### Property 14: Errors preserve user input state
*For any* error condition, the Streamlit Application should maintain all user input values so they can retry without re-entering data.
**Validates: Requirements 8.5**

### Property 15: Strike price is dynamically applied
*For any* user-provided strike price value, the Selenium Driver should clear any existing value in the strike price field and enter the exact user-provided value before fetching data.
**Validates: Requirements 9.1, 9.2, 9.4**

### Property 16: Strike price validation provides feedback
*For any* strike price that is not available for the selected stock and expiry, the system should display a user-friendly warning message without crashing.
**Validates: Requirements 9.3**

### Property 17: Output data matches user strike price
*For any* successfully fetched data, the Strike Price column in both the preview and Excel output should exactly match the strike price entered by the user.
**Validates: Requirements 9.5**

## Error Handling

### Error Categories and Handling Strategies

**1. Network and Connectivity Errors**
- BSE website unreachable
- Timeout during page load
- Connection reset during data fetch

**Handling:**
```python
try:
    driver.get(BSE_URL)
except (TimeoutException, WebDriverException) as e:
    raise ConnectivityError("Unable to reach BSE website. Please check your internet connection.")
```

**2. Element Not Found Errors**
- Company name not found in search
- Expected form elements missing
- Data table not present

**Handling:**
```python
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "element_id"))
    )
except TimeoutException:
    raise ElementNotFoundError("Expected element not found on page.")
```

**3. Data Validation Errors**
- Empty dataset returned
- Malformed data structure
- Missing required columns

**Handling:**
```python
if df.empty:
    raise NoDataError(f"No data available for {company_name} in the specified date range.")
    
required_columns = ['Date', 'Strike Price', 'Close', 'Open Interest']
if not all(col in df.columns for col in required_columns):
    raise DataValidationError("Fetched data is missing required columns.")
```

**4. User Input Errors**
- Invalid date range (from_date > to_date)
- Invalid strike price (negative or zero)
- Empty company name

**Handling:**
```python
def validate_inputs(params: FetchParameters) -> List[str]:
    errors = []
    if not params.company_name.strip():
        errors.append("Company name cannot be empty")
    if params.from_date > params.to_date:
        errors.append("From date must be before To date")
    if params.strike_price <= 0:
        errors.append("Strike price must be positive")
    return errors
```

**5. Bot Detection Errors**
- CAPTCHA presented
- Access denied by website
- Rate limiting triggered

**Handling:**
```python
if "captcha" in driver.page_source.lower():
    raise BotDetectionError("CAPTCHA detected. Please try again later.")
    
# Implement exponential backoff
for attempt in range(max_retries):
    try:
        fetch_data()
        break
    except RateLimitError:
        delay = 2 ** attempt
        time.sleep(delay)
```

### Error Message Guidelines

All error messages should:
- Be user-friendly and avoid technical jargon
- Suggest corrective actions when possible
- Preserve context (user inputs) for easy retry
- Log technical details for debugging

**Example Error Messages:**
- ❌ "WebDriverException: Message: unknown error: net::ERR_CONNECTION_REFUSED"
- ✅ "Unable to connect to BSE website. Please check your internet connection and try again."

## Testing Strategy

### Unit Testing Approach

Unit tests will verify individual component functionality in isolation using mocking where appropriate:

**1. Data Processor Tests**
- Test merge logic with sample Call and Put DataFrames
- Test missing value handling with incomplete datasets
- Test column formatting and ordering
- Test data validation with malformed inputs

**2. Excel Generator Tests**
- Test file creation with sample DataFrames
- Test filename generation with various inputs
- Test that generated files are valid Excel format

**3. Input Validation Tests**
- Test validation logic with valid and invalid inputs
- Test date range validation
- Test strike price validation

**4. Error Handler Tests**
- Test error message generation for different exception types
- Test that errors preserve user state

### Property-Based Testing Approach

Property-based tests will verify universal properties across many randomly generated inputs using the **Hypothesis** library for Python.

**Configuration:**
- Each property test should run a minimum of 100 iterations
- Use Hypothesis strategies to generate realistic test data
- Each test must reference its corresponding correctness property

**Property Test Examples:**

**Test 1: Merge Preserves Records**
```python
# Feature: bse-derivative-downloader, Property 6: Data merge preserves all records
@given(
    call_df=dataframes(columns=[...]),
    put_df=dataframes(columns=[...])
)
@settings(max_examples=100)
def test_merge_preserves_records(call_df, put_df):
    merged = merge_call_put_data(call_df, put_df)
    # Verify all unique date/strike combinations are present
    assert len(merged) >= max(len(call_df), len(put_df))
```

**Test 2: Missing Data Handling**
```python
# Feature: bse-derivative-downloader, Property 8: Missing data is handled gracefully
@given(
    df=dataframes(columns=[...], allow_nan=True)
)
@settings(max_examples=100)
def test_missing_data_handling(df):
    result = format_merged_data(df)
    # Verify no NaN values remain
    assert not result.isnull().any().any()
    # Verify "N/A" is used for missing values
    assert "N/A" in result.values
```

**Test 3: Filename Generation**
```python
# Feature: bse-derivative-downloader, Property 11: Filename includes context information
@given(
    company=text(min_size=1, max_size=50),
    from_date=dates(),
    to_date=dates()
)
@settings(max_examples=100)
def test_filename_includes_context(company, from_date, to_date):
    filename = generate_filename(company, from_date, to_date)
    assert company.replace(" ", "_") in filename
    assert from_date.strftime("%Y%m%d") in filename
    assert to_date.strftime("%Y%m%d") in filename
```

### Integration Testing

Integration tests will verify end-to-end workflows with mocked BSE website responses:

**Test Scenarios:**
1. Complete workflow: Input → Scrape → Merge → Preview → Download
2. Error recovery: Network failure → Retry → Success
3. Empty results: Valid inputs but no data available
4. Invalid company: Company not found on BSE

### Manual Testing Checklist

Due to the nature of web scraping, some aspects require manual verification:

- [ ] UI renders correctly in browser
- [ ] Loading spinner displays during fetch
- [ ] Preview table is readable and formatted
- [ ] Excel download works in browser
- [ ] Bot detection measures are effective
- [ ] Application works with real BSE website

## Implementation Notes

### Technology Stack

- **Python 3.8+**: Core language
- **Streamlit 1.28+**: Web UI framework
- **Selenium 4.15+**: Browser automation
- **Pandas 2.0+**: Data manipulation
- **Openpyxl 3.1+**: Excel file generation
- **webdriver-manager 4.0+**: Automatic ChromeDriver management
- **Hypothesis 6.92+**: Property-based testing library

### Selenium Best Practices

1. **Always use explicit waits** instead of implicit waits or sleep()
2. **Close driver properly** in finally blocks to prevent resource leaks
3. **Use headless mode** for production to reduce resource usage
4. **Implement retry logic** for transient failures
5. **Rotate User-Agent strings** if bot detection becomes an issue

### Streamlit State Management

Streamlit reruns the entire script on each interaction, so state management is critical:

```python
# Use session state to persist data across reruns
if 'merged_data' not in st.session_state:
    st.session_state.merged_data = None
    
if 'fetch_params' not in st.session_state:
    st.session_state.fetch_params = None
```

### Performance Considerations

- **Caching**: Use `@st.cache_data` for expensive operations
- **Lazy loading**: Only initialize Selenium driver when needed
- **Timeout configuration**: Set reasonable timeouts (10-30 seconds)
- **Resource cleanup**: Always close browser instances

### Security Considerations

- **Input sanitization**: Validate and sanitize all user inputs
- **No credential storage**: Application doesn't require authentication
- **Rate limiting**: Implement delays to avoid overwhelming BSE servers
- **Error information**: Don't expose sensitive system information in error messages

## Deployment Considerations

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Requirements File

```
streamlit>=1.28.0
selenium>=4.15.0
pandas>=2.0.0
openpyxl>=3.1.0
webdriver-manager>=4.0.0
hypothesis>=6.92.0  # For property-based testing
```

### System Requirements

- Python 3.8 or higher
- Chrome browser (for ChromeDriver)
- 2GB RAM minimum
- Internet connection for BSE website access

### Known Limitations

1. **BSE website changes**: If BSE modifies their website structure, selectors will need updates
2. **Rate limiting**: Excessive requests may trigger rate limiting
3. **CAPTCHA**: May appear if bot detection is triggered
4. **Data availability**: Historical data availability depends on BSE
5. **Browser dependency**: Requires Chrome/Chromium installation
