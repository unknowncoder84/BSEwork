# Implementation Plan: NSE India Scraper

## Overview

This implementation plan covers building a robust NSE India Scraper that extracts both Equity (EQ) and Options (OPT) data into a unified format with a professional Quantum UI featuring glassmorphism design.

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create nse_scraper directory structure
  - Update requirements.txt with undetected-chromedriver, selenium dependencies
  - Create __init__.py files for new modules
  - _Requirements: 8.1, 8.2_

- [ ] 2. Implement NSE Scraper base component
  - [ ] 2.1 Create nse_scraper.py with driver initialization
    - Implement initialize_driver() with undetected-chromedriver
    - Configure headless mode for cloud deployment
    - Add Referer header: https://www.nseindia.com/
    - Add random User-Agent rotation
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ] 2.2 Implement human delay function
    - Create add_human_delay(min=3.0, max=6.0) function
    - Use random.uniform for delay calculation
    - _Requirements: 8.5, 8.6_

  - [ ] 2.3 Write property test for delay bounds
    - **Property 8: Human delay is within bounds**
    - **Validates: Requirements 8.5, 8.6**

- [ ] 3. Implement NSE Equity data extraction
  - [ ] 3.1 Create fetch_equity_data() function
    - Navigate to https://www.nseindia.com/report-detail/eq_security
    - Search for stock symbol
    - Configure date range
    - Click Filter/Download button
    - Extract table data to DataFrame
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ] 3.2 Implement equity data processing
    - Add Series column with value "EQ"
    - Add Open Interest column with value "-"
    - Normalize column names to unified format
    - _Requirements: 1.2, 1.3_

- [ ] 4. Implement NSE Options data extraction
  - [ ] 4.1 Create fetch_options_data() function
    - Navigate to https://www.nseindia.com/report-detail/fo_eq_hist_contract_wise
    - Search for stock symbol
    - Select Expiry Date from dropdown
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ] 4.2 Implement dynamic strike price selection
    - Use WebDriverWait to wait for Strike Price dropdown (15s timeout)
    - Read all available strike prices from dropdown
    - Select user-provided strike price using Select class
    - Raise StrikePriceNotAvailableError if not found
    - _Requirements: 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ] 4.3 Complete options data extraction
    - Select Option Type (CE/PE)
    - Click Filter/Download button
    - Extract table data with Open Interest
    - Add Series column with value "OPT"
    - _Requirements: 3.7, 3.8, 3.9, 1.4, 1.5_

- [ ] 5. Implement Data Processor component
  - [ ] 5.1 Create data_processor.py
    - Implement process_equity_data() to add Series="EQ" and OI="-"
    - Implement process_options_data() to add Series="OPT"
    - Implement merge_equity_options() to combine by Date
    - Implement format_unified_data() for column ordering
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [ ] 5.2 Write property test for unified output structure
    - **Property 1: Unified output structure**
    - **Validates: Requirements 1.1**

  - [ ] 5.3 Write property test for Series/OI consistency
    - **Property 2: Series and OI consistency**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5**

  - [ ] 5.4 Write property test for date sorting
    - **Property 3: Merged data is sorted by Date**
    - **Validates: Requirements 1.6**

- [ ] 6. Checkpoint - Verify scraper and processor work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement Persistence Manager
  - [ ] 7.1 Create/update persistence.py for config.json
    - Implement load_config() and save_config()
    - Implement get_theme() and set_theme()
    - Implement get_notepad() and save_notepad()
    - Implement add_history_entry() and get_history()
    - Implement get_custom_tickers() and add_custom_ticker()
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ] 7.2 Write property test for persistence round-trip
    - **Property 4: Persistence round-trip consistency**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**

- [ ] 8. Implement Excel Generator
  - [ ] 8.1 Create/update excel_generator.py for multi-tab export
    - Implement create_multi_company_excel() with tabs per company
    - Implement generate_filename() with companies and dates
    - Implement apply_formatting() for professional styling
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.7_

  - [ ] 8.2 Write property test for Excel structure
    - **Property 5: Excel structure validation**
    - **Validates: Requirements 9.2, 9.3, 9.4**

  - [ ] 8.3 Write property test for Excel merge
    - **Property 6: Excel merge preserves all data**
    - **Validates: Requirements 9.1**

  - [ ] 8.4 Write property test for filename
    - **Property 7: Filename includes context**
    - **Validates: Requirements 9.7**

- [ ] 9. Implement Glassmorphism UI
  - [ ] 9.1 Create quantum_ui.py with theme CSS
    - Implement dark theme with glassmorphism effects
    - Implement light theme with frosted-glass effects
    - Add gradient backgrounds and Inter font
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ] 9.2 Implement theme toggle
    - Add theme toggle button in sidebar
    - Apply theme immediately without page reload
    - Persist theme selection
    - _Requirements: 5.6_

- [ ] 10. Implement Calendar Widget
  - [ ] 10.1 Add calendar widgets for date selection
    - Create From Date calendar widget
    - Create To Date calendar widget
    - Create Expiry Date calendar widget
    - Highlight selected dates
    - Prevent future date selection for historical data
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [ ] 11. Implement Multi-Stock Selection UI
  - [ ] 11.1 Create stock selection interface
    - Add multi-select dropdown with popular NSE stocks
    - Allow custom stock symbol input
    - Display progress for each stock during fetch
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ] 11.2 Implement error handling for multi-stock
    - Continue with remaining stocks if one fails
    - Report errors for failed stocks
    - _Requirements: 10.6_

- [ ] 12. Implement Error Handling and User Feedback
  - [ ] 12.1 Create error display functions
    - Display "Stock symbol not found on NSE" error
    - Display "No data available for the specified date range" error
    - Display "Unable to connect to NSE" error
    - Display "NSE is blocking requests" error
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [ ] 12.2 Implement progress and state preservation
    - Display progress bar with status messages
    - Preserve user inputs on error
    - _Requirements: 11.5, 11.6_

- [ ] 13. Implement Exponential Backoff Retry
  - [ ] 13.1 Create retry logic for 403 errors
    - Implement fetch_with_retry() with delays [5, 10, 20] seconds
    - Catch RateLimitError and retry
    - Raise after max retries
    - _Requirements: 8.7_

- [ ] 14. Create Main Application Entry Point
  - [ ] 14.1 Create nse_app.py
    - Wire together all components
    - Implement main workflow: select → fetch → process → display → export
    - Add sidebar with all inputs
    - Add main area with data preview and export
    - _Requirements: All_

- [ ] 15. Checkpoint - End-to-end testing
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Update Documentation
  - Update README.md with NSE scraper instructions
  - Document NSE-specific configuration
  - Add usage examples
  - _Requirements: All_

## Notes

- All tasks including property-based tests are required
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- The scraper uses 3-6 second delays between major actions to avoid 403 errors
