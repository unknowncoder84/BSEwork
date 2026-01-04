"""
Selenium-based web scraper for BSE Derivative Data.
Uses undetected-chromedriver for anti-bot detection bypass.
"""
import time
import random
import pandas as pd
from datetime import date
from typing import Optional, Tuple, List
from io import StringIO

try:
    import undetected_chromedriver as uc
    USE_UNDETECTED = True
except ImportError:
    USE_UNDETECTED = False

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    WebDriverException, StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager

from utils.models import (
    FetchParameters, ConnectivityError, CompanyNotFoundError,
    NoDataError, BotDetectionError, ElementNotFoundError, DataValidationError
)

# BSE Historical Data URL
BSE_URL = "https://www.bseindia.com/markets/Derivatives/DeriReports/HistoricalData.aspx"

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def add_human_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> float:
    """
    Add random delay to mimic human behavior.
    Returns the actual delay used.
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay


def get_random_user_agent() -> str:
    """Get a random user agent string."""
    return random.choice(USER_AGENTS)


def initialize_driver() -> webdriver.Chrome:
    """
    Initialize Chrome WebDriver with anti-detection configuration.
    Uses undetected-chromedriver if available, falls back to standard selenium.
    """
    if USE_UNDETECTED:
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--user-agent={get_random_user_agent()}')
        
        driver = uc.Chrome(options=options)
    else:
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--user-agent={get_random_user_agent()}')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Execute CDP commands to prevent detection
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": get_random_user_agent()
        })
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
    
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(10)
    
    return driver


def wait_for_element(driver: webdriver.Chrome, by: By, value: str, 
                     timeout: int = 20, clickable: bool = False):
    """
    Wait for element to be present/clickable with explicit wait.
    """
    wait = WebDriverWait(driver, timeout)
    if clickable:
        return wait.until(EC.element_to_be_clickable((by, value)))
    return wait.until(EC.presence_of_element_located((by, value)))


def check_for_bot_detection(driver: webdriver.Chrome) -> bool:
    """Check if bot detection/CAPTCHA is present."""
    page_source = driver.page_source.lower()
    bot_indicators = ['captcha', 'robot', 'blocked', 'access denied', 'unusual traffic']
    return any(indicator in page_source for indicator in bot_indicators)


def exponential_backoff_retry(func, max_retries: int = 3, base_delay: float = 2.0):
    """
    Retry function with exponential backoff.
    """
    last_exception = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
    raise last_exception


class BSEScraper:
    """
    Scraper class for fetching derivative data from BSE India website.
    """
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.delays_applied: List[float] = []
    
    def __enter__(self):
        self.driver = initialize_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the browser driver."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def navigate_to_bse(self) -> bool:
        """Navigate to BSE Historical Data page."""
        try:
            self.driver.get(BSE_URL)
            self.delays_applied.append(add_human_delay(2, 4))
            
            if check_for_bot_detection(self.driver):
                raise BotDetectionError()
            
            # Wait for page to load
            wait_for_element(self.driver, By.ID, "ContentPlaceHolder1_ddlInstrument", timeout=30)
            return True
            
        except TimeoutException:
            raise ConnectivityError("BSE website took too long to load. Please try again.")
        except WebDriverException as e:
            raise ConnectivityError(f"Unable to connect to BSE website: {str(e)}")
    
    def search_company(self, company_name: str) -> bool:
        """
        Search for company in the search field.
        """
        try:
            self.delays_applied.append(add_human_delay(1, 2))
            
            # Find and interact with company search field
            search_input = wait_for_element(
                self.driver, By.ID, "ContentPlaceHolder1_txtUnderlying", 
                timeout=20, clickable=True
            )
            search_input.clear()
            
            # Type company name character by character to mimic human
            for char in company_name:
                search_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            self.delays_applied.append(add_human_delay(1, 2))
            
            # Wait for autocomplete suggestions
            try:
                autocomplete = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-autocomplete"))
                )
                
                # Click first suggestion
                suggestions = autocomplete.find_elements(By.TAG_NAME, "li")
                if suggestions:
                    suggestions[0].click()
                    self.delays_applied.append(add_human_delay(0.5, 1))
                    return True
                else:
                    raise CompanyNotFoundError(company_name)
                    
            except TimeoutException:
                # Try pressing Enter if no autocomplete
                search_input.send_keys(Keys.RETURN)
                self.delays_applied.append(add_human_delay(1, 2))
                return True
                
        except NoSuchElementException:
            raise ElementNotFoundError("Company search field")
        except Exception as e:
            if "not found" in str(e).lower():
                raise CompanyNotFoundError(company_name)
            raise
    
    def select_instrument_type(self, instrument_type: str) -> bool:
        """Select Equity Options or Index Options."""
        try:
            self.delays_applied.append(add_human_delay(0.5, 1.5))
            
            dropdown = wait_for_element(
                self.driver, By.ID, "ContentPlaceHolder1_ddlInstrument",
                timeout=15, clickable=True
            )
            
            select = Select(dropdown)
            
            if instrument_type == "Equity Options":
                select.select_by_visible_text("Stock Options")
            else:
                select.select_by_visible_text("Index Options")
            
            self.delays_applied.append(add_human_delay(1, 2))
            return True
            
        except NoSuchElementException:
            raise ElementNotFoundError("Instrument type dropdown")
    
    def configure_parameters(self, params: FetchParameters) -> bool:
        """Configure expiry date, strike price, and date range."""
        try:
            self.delays_applied.append(add_human_delay(1, 2))
            
            # Set expiry date
            try:
                expiry_dropdown = wait_for_element(
                    self.driver, By.ID, "ContentPlaceHolder1_ddlExpiry",
                    timeout=15, clickable=True
                )
                select_expiry = Select(expiry_dropdown)
                expiry_str = params.expiry_date.strftime("%d-%b-%Y")
                
                # Try to find matching expiry
                for option in select_expiry.options:
                    if expiry_str.lower() in option.text.lower():
                        select_expiry.select_by_visible_text(option.text)
                        break
                
                self.delays_applied.append(add_human_delay(0.5, 1))
            except:
                pass  # Expiry might not be available for all instruments
            
            # Set strike price
            try:
                strike_input = wait_for_element(
                    self.driver, By.ID, "ContentPlaceHolder1_txtStrikePrice",
                    timeout=10, clickable=True
                )
                strike_input.clear()
                strike_input.send_keys(str(params.strike_price))
                self.delays_applied.append(add_human_delay(0.5, 1))
            except:
                pass  # Strike price field might not be present
            
            # Set from date
            try:
                from_date_input = wait_for_element(
                    self.driver, By.ID, "ContentPlaceHolder1_txtFromDt",
                    timeout=10, clickable=True
                )
                from_date_input.clear()
                from_date_input.send_keys(params.from_date.strftime("%d/%m/%Y"))
                self.delays_applied.append(add_human_delay(0.3, 0.7))
            except:
                pass
            
            # Set to date
            try:
                to_date_input = wait_for_element(
                    self.driver, By.ID, "ContentPlaceHolder1_txtToDt",
                    timeout=10, clickable=True
                )
                to_date_input.clear()
                to_date_input.send_keys(params.to_date.strftime("%d/%m/%Y"))
                self.delays_applied.append(add_human_delay(0.3, 0.7))
            except:
                pass
            
            return True
            
        except Exception as e:
            raise ElementNotFoundError(f"Parameter configuration: {str(e)}")
    
    def select_option_type(self, option_type: str) -> bool:
        """Select Call or Put option type."""
        try:
            self.delays_applied.append(add_human_delay(0.5, 1))
            
            option_dropdown = wait_for_element(
                self.driver, By.ID, "ContentPlaceHolder1_ddlOptType",
                timeout=15, clickable=True
            )
            
            select = Select(option_dropdown)
            select.select_by_visible_text(option_type.upper())
            
            self.delays_applied.append(add_human_delay(0.5, 1))
            return True
            
        except NoSuchElementException:
            raise ElementNotFoundError("Option type dropdown")
    
    def click_submit(self) -> bool:
        """Click the submit/get data button."""
        try:
            self.delays_applied.append(add_human_delay(0.5, 1))
            
            submit_btn = wait_for_element(
                self.driver, By.ID, "ContentPlaceHolder1_btnSubmit",
                timeout=15, clickable=True
            )
            submit_btn.click()
            
            self.delays_applied.append(add_human_delay(2, 4))
            
            if check_for_bot_detection(self.driver):
                raise BotDetectionError()
            
            return True
            
        except NoSuchElementException:
            raise ElementNotFoundError("Submit button")
    
    def extract_table_data(self) -> pd.DataFrame:
        """Extract data from the results table."""
        try:
            self.delays_applied.append(add_human_delay(1, 2))
            
            # Wait for table to load
            table = wait_for_element(
                self.driver, By.ID, "ContentPlaceHolder1_gvReport",
                timeout=30
            )
            
            # Get table HTML and parse with pandas
            table_html = table.get_attribute('outerHTML')
            dfs = pd.read_html(StringIO(table_html))
            
            if dfs and len(dfs) > 0:
                df = dfs[0]
                if len(df) > 0:
                    return df
            
            raise NoDataError("No data found in the results table.")
            
        except TimeoutException:
            raise NoDataError("No data available for the specified parameters.")
        except ValueError:
            raise NoDataError("Unable to parse data from the results table.")
    
    def fetch_option_data(self, params: FetchParameters, option_type: str) -> pd.DataFrame:
        """
        Fetch Call or Put options data.
        
        Args:
            params: FetchParameters with all search criteria
            option_type: "CE" for Call or "PE" for Put
            
        Returns:
            DataFrame with options data
        """
        try:
            # Navigate to BSE if not already there
            if BSE_URL not in self.driver.current_url:
                self.navigate_to_bse()
            
            # Search for company
            self.search_company(params.company_name)
            
            # Select instrument type
            self.select_instrument_type(params.instrument_type)
            
            # Configure parameters
            self.configure_parameters(params)
            
            # Select option type (CE or PE)
            self.select_option_type(option_type)
            
            # Submit and get data
            self.click_submit()
            
            # Extract table data
            df = self.extract_table_data()
            
            # Add option type column
            df['Option_Type'] = option_type
            
            return df
            
        except BSEScraperError:
            raise
        except Exception as e:
            raise DataValidationError(f"Error fetching {option_type} data: {str(e)}")
    
    def fetch_call_and_put_data(self, params: FetchParameters) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetch both Call and Put data sequentially.
        
        Returns:
            Tuple of (call_df, put_df)
        """
        # Fetch Call data first
        call_df = self.fetch_option_data(params, "CE")
        
        # Add delay between fetches
        self.delays_applied.append(add_human_delay(2, 4))
        
        # Navigate back to form for Put data
        self.driver.get(BSE_URL)
        self.delays_applied.append(add_human_delay(2, 3))
        
        # Fetch Put data
        put_df = self.fetch_option_data(params, "PE")
        
        return call_df, put_df


def fetch_derivative_data(params: FetchParameters) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main function to fetch derivative data from BSE.
    
    Args:
        params: FetchParameters with all search criteria
        
    Returns:
        Tuple of (call_df, put_df)
    """
    with BSEScraper() as scraper:
        return scraper.fetch_call_and_put_data(params)
