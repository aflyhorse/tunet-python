#!/usr/bin/env python3
"""
Tsinghua University Network Auto Login Script
Automatically logs into the campus network portal in headless mode.
"""

import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TunetAutoLogin:
    def __init__(self, username=None, password=None, headless=True, timeout=30):
        """
        Initialize the auto login client

        Args:
            username (str): Campus network username
            password (str): Campus network password
            headless (bool): Run browser in headless mode
            timeout (int): Maximum wait time for elements
        """
        self.username = username or os.getenv("TUNET_USERNAME")
        self.password = password or os.getenv("TUNET_PASSWORD")
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.login_url = (
            "http://auth6.tsinghua.edu.cn/srun_portal_pc?ac_id=163&theme=pro"
        )

        if not self.username or not self.password:
            raise ValueError(
                "Username and password must be provided either as arguments or environment variables "
                + "(TUNET_USERNAME, TUNET_PASSWORD)"
            )

    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")

        # Additional options for better compatibility
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
            + "Chrome/91.0.4472.124 Safari/537.36"
        )

        try:
            # Use Selenium Manager (built into Selenium 4.6+) to automatically manage ChromeDriver
            # Selenium Manager automatically downloads and manages the correct driver version
            self.driver = webdriver.Chrome(options=chrome_options)
            # Set page load timeout
            self.driver.set_page_load_timeout(60)
            logger.info("Chrome driver initialized successfully using Selenium Manager")
        except WebDriverException as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            logger.info(
                "Please ensure Chrome/Chromium is installed and compatible with current Selenium version"
            )
            raise

    def check_login_status(self):
        """Check if already logged in by examining page content"""
        try:
            page_source = self.driver.page_source

            # Check for success page indicators
            if "page   : 'success'" in page_source or 'page:"success"' in page_source:
                logger.info("Detected success page - already logged in")
                return "already_logged_in"

            # Check for other success indicators
            success_indicators = [
                "已连接",  # Duration
                "已用流量",  # Usage
                "btn-logout",  # Logout button
                "断开连接",  # Disconnect text
                "user_name",  # Username display
            ]

            success_count = sum(
                1 for indicator in success_indicators if indicator in page_source
            )
            if success_count >= 3:  # If we find 3 or more success indicators
                logger.info(
                    f"Detected {success_count} success indicators - likely already logged in"
                )
                return "already_logged_in"

            # Check for login form indicators
            login_indicators = [
                'id="username"',
                'id="password"',
                'id="login-account"',
                "用户名",  # Username label
                "密码",  # Password label
            ]

            login_count = sum(
                1 for indicator in login_indicators if indicator in page_source
            )
            if login_count >= 3:  # If we find 3 or more login indicators
                logger.info(
                    f"Detected {login_count} login indicators - login form present"
                )
                return "need_login"

            logger.warning("Could not determine login status from page content")
            return "unknown"

        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return "unknown"

    def login(self):
        """Perform the login process"""
        try:
            logger.info(f"Navigating to login page: {self.login_url}")
            self.driver.get(self.login_url)

            # Wait for page to load and log current status
            logger.info("Page loaded, checking current URL and title...")
            logger.info(f"Current URL: {self.driver.current_url}")
            logger.info(f"Page title: {self.driver.title}")

            # Check if page content is accessible
            try:
                page_source_length = len(self.driver.page_source)
                logger.info(f"Page source length: {page_source_length} characters")
                if page_source_length < 1000:
                    logger.warning(
                        "Page source seems too short, might be a loading issue"
                    )
                    logger.debug(
                        f"Page source preview: {self.driver.page_source[:500]}"
                    )
            except Exception as e:
                logger.warning(f"Could not get page source: {e}")

            # Wait a moment for page to fully load
            time.sleep(2)

            # Check if already logged in
            login_status = self.check_login_status()
            if login_status == "already_logged_in":
                logger.info("✅ Already logged in! No login required.")
                return True
            elif login_status == "unknown":
                logger.warning(
                    "Cannot determine login status, proceeding with login attempt..."
                )

            # Wait for page to load
            wait = WebDriverWait(self.driver, self.timeout)

            # Wait for username field to be present
            logger.info("Waiting for login form to load...")
            try:
                username_field = wait.until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                logger.info("Username field found successfully")
            except TimeoutException:
                logger.error("Username field not found within timeout")
                # Try to find other elements to debug
                logger.info("Attempting to find alternative selectors...")
                try:
                    # Check if any input fields exist
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    logger.info(f"Found {len(inputs)} input elements")
                    for i, inp in enumerate(inputs[:5]):  # Check first 5 inputs
                        logger.info(
                            f"Input {i}: id='{inp.get_attribute('id')}', type='{inp.get_attribute('type')}', "
                            + f"name='{inp.get_attribute('name')}'"
                        )
                except Exception as e:
                    logger.error(f"Error searching for input elements: {e}")
                raise

            # Fill username
            logger.info("Entering username...")
            username_field.clear()
            username_field.send_keys(self.username)

            # Fill password
            logger.info("Entering password...")
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)

            # Check if domain checkbox should be checked (for external network access)
            domain_checkbox = self.driver.find_element(By.ID, "domain")
            if not domain_checkbox.is_selected():
                logger.info("Checking domain checkbox for external network access...")
                domain_checkbox.click()

            # Click login button
            logger.info("Clicking login button...")
            login_button = wait.until(
                EC.element_to_be_clickable((By.ID, "login-account"))
            )
            login_button.click()

            # Wait a moment for the login to process
            time.sleep(3)

            # Check if login was successful by looking for redirect or success indicators
            current_url = self.driver.current_url
            if current_url != self.login_url:
                logger.info(f"Login appears successful! Redirected to: {current_url}")
                return True
            else:
                # Check for any error messages
                logger.warning("Still on login page, checking for errors...")
                try:
                    # Look for common error indicators
                    error_elements = self.driver.find_elements(By.CLASS_NAME, "error")
                    if error_elements:
                        error_text = error_elements[0].text
                        logger.error(f"Login error: {error_text}")
                        return False
                except Exception as e:
                    logger.warning(f"Error checking for login errors: {e}")
                    pass

                logger.warning("Login status unclear - may need manual verification")
                return None

        except TimeoutException:
            logger.error("Timeout waiting for page elements to load")
            return False
        except Exception as e:
            logger.error(f"Login failed with error: {e}")
            return False

    def run(self):
        """Main execution method"""
        try:
            logger.info("Starting Tsinghua University Network Auto Login")
            self.setup_driver()

            result = self.login()

            if result is True:
                logger.info("✅ Login successful!")
                return True
            elif result is False:
                logger.error("❌ Login failed!")
                return False
            else:
                logger.warning("⚠️ Login status unclear")
                return None

        except Exception as e:
            logger.error(f"Script failed with error: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")


def main():
    """Command line interface"""
    # Load environment variables from .env file if available
    if load_dotenv is not None:
        load_dotenv()

    import argparse

    parser = argparse.ArgumentParser(
        description="Tsinghua University Network Auto Login"
    )
    parser.add_argument("-u", "--username", help="Campus network username")
    parser.add_argument("-p", "--password", help="Campus network password")
    parser.add_argument(
        "--no-headless", action="store_true", help="Run with visible browser window"
    )
    parser.add_argument(
        "--timeout", type=int, default=30, help="Timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        client = TunetAutoLogin(
            username=args.username,
            password=args.password,
            headless=not args.no_headless,
            timeout=args.timeout,
        )

        success = client.run()
        sys.exit(0 if success else 1)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.info("You can set credentials via:")
        logger.info("1. Command line: python tunet_login.py -u USERNAME -p PASSWORD")
        logger.info(
            "2. Environment variables: export TUNET_USERNAME=xxx TUNET_PASSWORD=xxx"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
