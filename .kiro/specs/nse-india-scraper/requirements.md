# Requirements Document

## Introduction

The NSE India Scraper is a professional-grade web application that automates the extraction of both Equity (EQ) and Options (OPT) data from the National Stock Exchange of India website. The system provides a unified data format combining equity price-volume data with derivative contract data, featuring a futuristic "Quantum" UI with glassmorphism design, persistent memory, and robust anti-bot measures for reliable cloud deployment.

## Glossary

- **NSE**: National Stock Exchange of India
- **Equity Data (EQ)**: Stock price and volume data from the Security-wise Price Volume Archive
- **Options Data (OPT)**: Derivative contract data including Call and Put options
- **Strike Price**: The predetermined price at which an option can be exercised
- **Open Interest (OI)**: The total number of outstanding derivative contracts
- **Series**: Data type identifier - "EQ" for equity, "OPT" for options
- **Glassmorphism**: A UI design style featuring frosted-glass effect with transparency and blur
- **WebDriverWait**: Selenium explicit wait mechanism for dynamic element loading
- **Undetected ChromeDriver**: Anti-detection Chrome automation library
- **NSE_Scraper**: The Selenium-based component that navigates and extracts data from NSE website
- **Data_Processor**: The component responsible for merging equity and derivative data
- **Excel_Generator**: The component that creates unified Excel exports
- **Persistence_Manager**: The component that saves/loads user settings to config.json
- **UI_Controller**: The Streamlit-based user interface component

## Requirements

### Requirement 1: Unified Data Format

**User Story:** As a financial analyst, I want equity and options data in a unified format, so that I can analyze both data types consistently.

#### Acceptance Criteria

1. THE Data_Processor SHALL output data with columns: Date, Series, Open, High, Low, Close, Volume, Open Interest
2. WHEN fetching Equity data THEN the NSE_Scraper SHALL set the Series column to "EQ"
3. WHEN fetching Equity data THEN the NSE_Scraper SHALL set the Open Interest column to "-" (dash)
4. WHEN fetching Options data THEN the NSE_Scraper SHALL set the Series column to "OPT"
5. WHEN fetching Options data THEN the NSE_Scraper SHALL include the actual Open Interest value
6. WHEN data is merged THEN the Data_Processor SHALL combine EQ and OPT rows sorted by Date

### Requirement 2: NSE Equity Data Extraction

**User Story:** As a financial analyst, I want to fetch historical equity price-volume data from NSE, so that I can analyze stock performance.

#### Acceptance Criteria

1. WHEN fetching Equity data THEN the NSE_Scraper SHALL navigate to https://www.nseindia.com/report-detail/eq_security
2. WHEN the Equity page loads THEN the NSE_Scraper SHALL search for the specified stock symbol
3. WHEN the stock is selected THEN the NSE_Scraper SHALL configure the date range parameters
4. WHEN parameters are configured THEN the NSE_Scraper SHALL click the Filter/Download button
5. WHEN data is retrieved THEN the NSE_Scraper SHALL extract Date, Open, High, Low, Close, and Volume columns
6. WHEN Equity data is extracted THEN the NSE_Scraper SHALL return a DataFrame with the unified format

### Requirement 3: NSE Options Data Extraction

**User Story:** As a financial analyst, I want to fetch historical options contract data from NSE, so that I can analyze derivative performance.

#### Acceptance Criteria

1. WHEN fetching Options data THEN the NSE_Scraper SHALL navigate to https://www.nseindia.com/report-detail/fo_eq_hist_contract_wise
2. WHEN the Options page loads THEN the NSE_Scraper SHALL search for the specified stock symbol
3. WHEN the stock is selected THEN the NSE_Scraper SHALL select the Expiry Date from the dropdown
4. WHEN the Expiry Date is selected THEN the NSE_Scraper SHALL wait for the Strike Price dropdown to populate using WebDriverWait
5. WHEN the Strike Price dropdown is populated THEN the NSE_Scraper SHALL select the user-provided strike price using Selenium Select class
6. WHEN the strike price is not available THEN the UI_Controller SHALL display a warning: "Strike Price not available for this expiry"
7. WHEN parameters are configured THEN the NSE_Scraper SHALL select the Option Type (Call/Put)
8. WHEN all parameters are set THEN the NSE_Scraper SHALL click the Filter/Download button
9. WHEN data is retrieved THEN the NSE_Scraper SHALL extract Date, Open, High, Low, Close, Volume, and Open Interest columns

### Requirement 4: Dynamic Strike Price Selection

**User Story:** As a financial analyst, I want the strike price selection to be dynamic, so that I can select any available strike price for my chosen expiry.

#### Acceptance Criteria

1. THE NSE_Scraper SHALL NOT use hardcoded strike price values
2. WHEN the Expiry Date dropdown value changes THEN the NSE_Scraper SHALL wait for the Strike Price dropdown to refresh
3. WHEN waiting for Strike Price dropdown THEN the NSE_Scraper SHALL use WebDriverWait with a timeout of 15 seconds
4. WHEN the Strike Price dropdown is populated THEN the NSE_Scraper SHALL read all available options
5. WHEN selecting strike price THEN the NSE_Scraper SHALL use Selenium Select class with select_by_visible_text()
6. IF the user-provided strike price is not in the dropdown THEN the NSE_Scraper SHALL raise StrikePriceNotAvailableError

### Requirement 5: Glassmorphism UI Design

**User Story:** As a user, I want a futuristic dark/light theme with glassmorphism effects, so that the application looks professional and modern.

#### Acceptance Criteria

1. THE UI_Controller SHALL provide both dark and light theme options
2. WHEN dark theme is active THEN the UI_Controller SHALL display semi-transparent sidebar panels with blur effect
3. WHEN light theme is active THEN the UI_Controller SHALL display frosted-glass effect panels
4. THE UI_Controller SHALL apply gradient backgrounds with subtle color transitions
5. THE UI_Controller SHALL use modern typography with the Inter font family
6. WHEN the user toggles theme THEN the UI_Controller SHALL immediately apply the new theme without page reload

### Requirement 6: Persistent Memory

**User Story:** As a user, I want my settings and history to persist across sessions, so that I don't have to reconfigure the application each time.

#### Acceptance Criteria

1. THE Persistence_Manager SHALL save all user settings to config.json file
2. THE Persistence_Manager SHALL persist the Notepad content across sessions
3. THE Persistence_Manager SHALL persist the search/fetch history with timestamps
4. THE Persistence_Manager SHALL persist the selected theme (dark/light)
5. THE Persistence_Manager SHALL persist custom ticker lists added by the user
6. WHEN the application starts THEN the Persistence_Manager SHALL load all saved settings from config.json
7. WHEN any setting changes THEN the Persistence_Manager SHALL immediately save to config.json

### Requirement 7: Integrated Calendar Widget

**User Story:** As a user, I want a calendar widget for date selection, so that I can precisely select date ranges.

#### Acceptance Criteria

1. THE UI_Controller SHALL provide a calendar widget for From Date selection
2. THE UI_Controller SHALL provide a calendar widget for To Date selection
3. THE UI_Controller SHALL provide a calendar widget for Expiry Date selection
4. WHEN a date is selected THEN the calendar widget SHALL highlight the selected date
5. THE calendar widget SHALL prevent selection of future dates for historical data
6. THE calendar widget SHALL display the current month by default

### Requirement 8: Anti-Bot Measures

**User Story:** As a system administrator, I want robust anti-bot measures, so that the scraper can reliably fetch data without being blocked.

#### Acceptance Criteria

1. THE NSE_Scraper SHALL use undetected-chromedriver for browser automation
2. THE NSE_Scraper SHALL run in headless mode for cloud deployment
3. WHEN making requests THEN the NSE_Scraper SHALL include the header: Referer: https://www.nseindia.com/
4. WHEN making requests THEN the NSE_Scraper SHALL include a random User-Agent from a predefined list
5. WHEN selecting a stock THEN the NSE_Scraper SHALL add a random delay between 3 to 6 seconds before clicking Filter/Download
6. WHEN performing sequential actions THEN the NSE_Scraper SHALL add random delays between 1 to 3 seconds
7. IF a 403 error is received THEN the NSE_Scraper SHALL implement exponential backoff retry with delays of 5, 10, 20 seconds

### Requirement 9: Unified Excel Export

**User Story:** As a financial analyst, I want to export merged data to Excel with separate tabs per company, so that I can analyze multiple stocks in one file.

#### Acceptance Criteria

1. WHEN exporting data THEN the Excel_Generator SHALL merge Equity and Derivative data by Date
2. WHEN creating Excel file THEN the Excel_Generator SHALL create separate tabs for each company
3. WHEN naming tabs THEN the Excel_Generator SHALL use the company symbol as the tab name
4. THE Excel_Generator SHALL include proper column headers in each tab
5. THE Excel_Generator SHALL apply professional formatting with alternating row colors
6. WHEN the export is complete THEN the UI_Controller SHALL provide a download button for the Excel file
7. THE Excel_Generator SHALL generate a filename including company names and date range

### Requirement 10: Multi-Stock Selection

**User Story:** As a financial analyst, I want to select multiple stocks at once, so that I can fetch data for multiple companies in a single operation.

#### Acceptance Criteria

1. THE UI_Controller SHALL provide a multi-select input for stock selection
2. THE UI_Controller SHALL display a list of popular NSE stocks for quick selection
3. THE UI_Controller SHALL allow users to add custom stock symbols
4. WHEN multiple stocks are selected THEN the NSE_Scraper SHALL fetch data for each stock sequentially
5. WHEN fetching multiple stocks THEN the UI_Controller SHALL display progress for each stock
6. WHEN one stock fails THEN the NSE_Scraper SHALL continue with remaining stocks and report the error

### Requirement 11: Error Handling and User Feedback

**User Story:** As a user, I want clear error messages and feedback, so that I understand what's happening and can take corrective action.

#### Acceptance Criteria

1. WHEN the stock symbol is not found THEN the UI_Controller SHALL display: "Stock symbol not found on NSE"
2. WHEN no data exists for the date range THEN the UI_Controller SHALL display: "No data available for the specified date range"
3. WHEN the NSE website is unreachable THEN the UI_Controller SHALL display: "Unable to connect to NSE. Please check your internet connection"
4. WHEN a 403 error persists after retries THEN the UI_Controller SHALL display: "NSE is blocking requests. Please try again later"
5. WHEN data is being fetched THEN the UI_Controller SHALL display a progress bar with status messages
6. WHEN errors occur THEN the UI_Controller SHALL preserve all user input values for easy retry
