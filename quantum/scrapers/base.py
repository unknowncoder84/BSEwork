"""
Quantum Market Suite - Scraper Base

Base scraper class with anti-detection measures including random delays,
user-agent rotation, and rate limit handling.
Configured for Streamlit Cloud deployment with system Chromium.
"""

import random
import time
import os
from typing import Optional, List
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Cloud deployment paths - CRITICAL for Streamlit Cloud
CHROMIUM_BINARY_PATH = "/usr/bin/chromium"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"


def is_cloud_environment() -> bool:
    """Check if running in cloud environment (Streamlit Cloud, etc.)"""
    return (
        os.path.exists(CHROMIUM_BINARY_PATH) or
        os.environ.get('STREAMLIT_SHARING_MODE') is not None or
        os.environ.get('IS_CLOUD') is not None
    )


class ScraperBase(ABC):
    """Base class for exchange scrapers with anti-detection measures."""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    # Human-like delays (3-6 seconds as per requirements)
    MIN_DELAY = 3.0
    MAX_DELAY = 6.0
    RATE_LIMIT_WAIT = 30.0
    REQUEST_TIMEOUT = 60
    MAX_RETRIES = 3
    
    def __init__(self, headless: bool = True):
        """Initialize scraper with optional headless mode."""
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self._current_user_agent_index = 0
        self._last_request_time: Optional[float] = None
        self._request_delays: List[float] = []
        self._is_cloud = is_cloud_environment()

    def _get_chrome_options(self) -> Options:
        """Configure Chrome options for anti-detection and cloud deployment."""
        options = Options()
        
        # CRITICAL: Set binary location for Streamlit Cloud
        if self._is_cloud and os.path.exists(CHROMIUM_BINARY_PATH):
            options.binary_location = CHROMIUM_BINARY_PATH
        
        # Mandatory headless arguments for cloud
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--user-agent={self._get_current_user_agent()}")
        
        # Anti-detection options
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        return options
    
    def _get_current_user_agent(self) -> str:
        """Get current user agent string."""
        return self.USER_AGENTS[self._current_user_agent_index % len(self.USER_AGENTS)]
    
    def rotate_user_agent(self) -> str:
        """Switch to a different user agent and return it."""
        self._current_user_agent_index = (self._current_user_agent_index + 1) % len(self.USER_AGENTS)
        return self._get_current_user_agent()
    
    def get_user_agent_history(self) -> List[str]:
        """Get list of user agents used (for testing)."""
        return [self.USER_AGENTS[i % len(self.USER_AGENTS)] 
                for i in range(self._current_user_agent_index + 1)]
    
    def random_delay(self, min_sec: Optional[float] = None, max_sec: Optional[float] = None) -> float:
        """Implement human-like random delay. Returns actual delay used."""
        min_delay = min_sec if min_sec is not None else self.MIN_DELAY
        max_delay = max_sec if max_sec is not None else self.MAX_DELAY
        
        delay = random.uniform(min_delay, max_delay)
        self._request_delays.append(delay)
        time.sleep(delay)
        
        return delay

    def get_request_delays(self) -> List[float]:
        """Get list of all delays used (for testing)."""
        return self._request_delays.copy()
    
    def clear_delay_history(self) -> None:
        """Clear delay history (for testing)."""
        self._request_delays = []
    
    def handle_rate_limit(self) -> float:
        """Wait for rate limit cooldown. Returns actual wait time."""
        wait_time = self.RATE_LIMIT_WAIT
        start = time.time()
        time.sleep(wait_time)
        actual_wait = time.time() - start
        self.rotate_user_agent()
        return actual_wait
    
    def init_driver(self) -> webdriver.Chrome:
        """Initialize Chrome WebDriver with anti-detection settings for cloud deployment."""
        if self.driver is not None:
            return self.driver
        
        try:
            options = self._get_chrome_options()
            
            # CRITICAL: Set chromedriver path for Streamlit Cloud
            if self._is_cloud and os.path.exists(CHROMEDRIVER_PATH):
                service = Service(CHROMEDRIVER_PATH)
            else:
                # Try webdriver-manager for local development
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                except Exception:
                    service = Service()
            
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Execute CDP commands to prevent detection
            try:
                self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": self._get_current_user_agent()
                })
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    """
                })
            except Exception:
                pass  # CDP commands may not be available in all configurations
            
            self.driver.set_page_load_timeout(self.REQUEST_TIMEOUT)
            self.driver.implicitly_wait(10)
            
        except WebDriverException as e:
            raise RuntimeError(f"Failed to initialize Chrome driver: {e}")
        
        return self.driver
    
    def close_driver(self) -> None:
        """Close and cleanup WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def fetch_page(self, url: str, retry_on_rate_limit: bool = True) -> str:
        """Fetch page content with anti-detection measures."""
        driver = self.init_driver()
        
        for attempt in range(self.MAX_RETRIES):
            try:
                self.random_delay()
                driver.get(url)
                
                WebDriverWait(driver, self.REQUEST_TIMEOUT).until(
                    EC.presence_of_element_located(("tag name", "body"))
                )
                
                if self._is_rate_limited(driver.page_source):
                    if retry_on_rate_limit and attempt < self.MAX_RETRIES - 1:
                        self.handle_rate_limit()
                        continue
                    raise RateLimitError("Rate limited by exchange")
                
                return driver.page_source
                
            except TimeoutException:
                if attempt < self.MAX_RETRIES - 1:
                    self.random_delay(2.0, 5.0)
                    continue
                raise
        
        raise RuntimeError(f"Failed to fetch {url} after {self.MAX_RETRIES} attempts")
    
    def _is_rate_limited(self, page_source: str) -> bool:
        """Check if response indicates rate limiting."""
        rate_limit_indicators = [
            "too many requests",
            "rate limit",
            "access denied",
            "blocked",
            "captcha",
        ]
        page_lower = page_source.lower()
        return any(indicator in page_lower for indicator in rate_limit_indicators)
    
    @abstractmethod
    def get_exchange_name(self) -> str:
        """Return the exchange name (NSE or BSE)."""
        pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup driver."""
        self.close_driver()
        return False


class RateLimitError(Exception):
    """Raised when exchange rate limits the scraper."""
    pass


class ScrapingError(Exception):
    """General scraping error."""
    pass
