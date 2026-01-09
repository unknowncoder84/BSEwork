# Requirements Document

## Introduction

The BSE Derivative Data Downloader is a web-based application that automates the process of fetching historical Call and Put options data from the BSE India website. The system eliminates manual data collection by using automated web scraping to retrieve derivative data, merge it intelligently, and provide users with a clean, downloadable Excel file. The application provides a professional user interface built with Streamlit, allowing users to specify search parameters including company name, expiry date, strike price, and date ranges.

## Glossary

- **BSE**: Bombay Stock Exchange, India's stock exchange platform
- **Derivative Data**: Financial instruments (options) whose value is derived from underlying assets
- **Call Option**: A financial contract giving the buyer the right to purchase an asset at a specified price
- **Put Option**: A financial contract giving the buyer the right to sell an asset at a specified price
- **Strike Price**: The predetermined price at which an option can be exercised
- **Expiry Date**: The date on which an options contract expires
- **OI (Open Interest)**: The total number of outstanding derivative contracts
- **Web Scraper**: An automated tool that extracts data from websites
- **Streamlit Application**: The web-based user interface component of the system
- **Selenium Driver**: The browser automation component that navigates and interacts with the BSE website
- **Data Processor**: The component responsible for merging and formatting the retrieved data
- **Excel Generator**: The component that creates downloadable Excel files from processed data

## Requirements

### Requirement 1

**User Story:** As a financial analyst, I want to search for derivative data by company name, so that I can quickly find options data for specific stocks or indices.

#### Acceptance Criteria

1. WHEN the Streamlit Application starts THEN the system SHALL display a sidebar with a searchable company name input field
2. WHEN a user types in the company name field THEN the Streamlit Application SHALL accept text input for stock or index names
3. WHEN the user interface loads THEN the Streamlit Application SHALL present a professional and clean layout with the sidebar for inputs and main screen for data visualization
4. WHEN the Streamlit Application is running THEN the system SHALL provide input fields for expiry date, strike price, and date range (from and to dates)
5. WHEN all required inputs are provided THEN the Streamlit Application SHALL enable the "Fetch & Merge Data" button

### Requirement 2

**User Story:** As a financial analyst, I want the system to automatically fetch both Call and Put data from BSE India, so that I don't have to manually download multiple files.

#### Acceptance Criteria

1. WHEN the user clicks "Fetch & Merge Data" THEN the Selenium Driver SHALL navigate to https://www.bseindia.com/markets/Derivatives/DeriReports/HistoricalData.aspx
2. WHEN the BSE website loads THEN the Selenium Driver SHALL search for the specified company name in the search field
3. WHEN the company is selected THEN the Selenium Driver SHALL select the appropriate instrument type (Equity Options or Index Options)
4. WHEN instrument type is selected THEN the Selenium Driver SHALL configure the expiry date, strike price, and date range parameters
5. WHEN parameters are configured for Call options THEN the Selenium Driver SHALL fetch the Call options data for the specified parameters
6. WHEN Call data is retrieved THEN the Selenium Driver SHALL fetch the Put options data for the same parameters
7. WHEN the Selenium Driver is fetching data THEN the system SHALL use headless browser mode for background operation
8. WHEN the Selenium Driver interacts with the BSE website THEN the system SHALL include User-Agent headers to mimic human browser behavior
9. WHEN the Selenium Driver performs actions THEN the system SHALL add small delays between clicks to avoid detection as a bot

### Requirement 3

**User Story:** As a financial analyst, I want the system to merge Call and Put data intelligently, so that I can analyze both option types side by side.

#### Acceptance Criteria

1. WHEN both Call and Put data are fetched THEN the Data Processor SHALL merge them on Date and Strike Price columns
2. WHEN data is merged THEN the Data Processor SHALL format columns as: Date, Strike Price, Call Price, Call OI, Put Price, Put OI
3. WHEN data for a specific date is missing THEN the Data Processor SHALL fill missing values with "N/A" instead of causing errors
4. WHEN merging is complete THEN the Data Processor SHALL validate that all rows contain consistent date and strike price information
5. WHEN data processing encounters errors THEN the Data Processor SHALL handle exceptions gracefully without crashing the application

### Requirement 4

**User Story:** As a financial analyst, I want to preview the merged data before downloading, so that I can verify the data is correct.

#### Acceptance Criteria

1. WHEN data merging is complete THEN the Streamlit Application SHALL display a preview table in the main screen area
2. WHEN the preview table is displayed THEN the Streamlit Application SHALL show all merged columns with proper formatting
3. WHEN data is being fetched THEN the Streamlit Application SHALL display a loading spinner with status information
4. WHEN the preview is shown THEN the Streamlit Application SHALL enable the "Download Excel" button

### Requirement 5

**User Story:** As a financial analyst, I want to download the merged data as an Excel file, so that I can use it in my analysis tools.

#### Acceptance Criteria

1. WHEN the user clicks "Download Excel" THEN the Excel Generator SHALL create an Excel file with the merged data
2. WHEN the Excel file is created THEN the Excel Generator SHALL use the openpyxl library for file generation
3. WHEN the Excel file is generated THEN the Streamlit Application SHALL provide the file for download to the user
4. WHEN the Excel file is created THEN the Excel Generator SHALL include proper column headers and formatting
5. WHEN the download is initiated THEN the system SHALL provide a meaningful filename including company name and date range

### Requirement 6

**User Story:** As a system administrator, I want the application to use only open-source libraries and free resources, so that the system remains cost-free to operate.

#### Acceptance Criteria

1. WHEN the system is deployed THEN the system SHALL use only open-source libraries: Streamlit, Selenium, Pandas, and Openpyxl
2. WHEN the Selenium Driver initializes THEN the system SHALL use webdriver-manager to handle ChromeDriver automatically
3. WHEN the system fetches data THEN the system SHALL rely on direct scraping of the public BSE Historical Data page without using paid APIs
4. WHEN dependencies are installed THEN the system SHALL require only freely available Python packages

### Requirement 7

**User Story:** As a financial analyst, I want the system to handle website blocking gracefully, so that data fetching remains reliable.

#### Acceptance Criteria

1. WHEN the Selenium Driver makes requests THEN the system SHALL include realistic User-Agent headers in all HTTP requests
2. WHEN the Selenium Driver performs sequential actions THEN the system SHALL add delays between interactions to simulate human behavior
3. WHEN the BSE website responds slowly THEN the Selenium Driver SHALL wait for elements to load before interacting with them
4. WHEN the website blocks a request THEN the system SHALL provide clear error messages to the user
5. WHEN retrying failed requests THEN the Selenium Driver SHALL implement exponential backoff delays

### Requirement 8

**User Story:** As a financial analyst, I want clear error messages when data cannot be fetched, so that I understand what went wrong and can take corrective action.

#### Acceptance Criteria

1. WHEN the company name is not found THEN the Streamlit Application SHALL display an error message indicating the company was not found
2. WHEN no data exists for the specified date range THEN the Streamlit Application SHALL inform the user that no data is available
3. WHEN the BSE website is unreachable THEN the Streamlit Application SHALL display a connectivity error message
4. WHEN an unexpected error occurs THEN the system SHALL log the error details and display a user-friendly message
5. WHEN errors are displayed THEN the Streamlit Application SHALL maintain the user's input values for easy retry

### Requirement 9

**User Story:** As a financial analyst, I want the strike price I enter in the UI to be used exactly when fetching data, so that the downloaded data corresponds to my specified strike price.

#### Acceptance Criteria

1. WHEN the user enters a strike price in the UI THEN the Selenium Driver SHALL use that exact strike price value when configuring the BSE website form
2. WHEN the Selenium Driver configures the strike price field THEN the system SHALL clear any existing value before entering the user-provided strike price
3. WHEN the strike price is not available for the selected stock and expiry THEN the Streamlit Application SHALL display a warning message: "Strike Price not available for this expiry"
4. WHEN multiple stocks are selected THEN the Selenium Driver SHALL clear the previous strike price from the web form before entering the strike price for the next stock
5. WHEN data is fetched and displayed THEN the Strike Price column in the preview and Excel output SHALL match exactly the strike price entered by the user
6. WHEN the strike price input changes THEN the Streamlit Application SHALL update the displayed strike price metric in real-time
