"""
LinkedIn Bulk Message Sender (Selenium)
-----------------------------------------
HOW IT WORKS:
1. Opens LinkedIn login page
2. You login ONCE manually (session is saved)
3. Sends connection requests + messages to LinkedIn profiles automatically

LIMITS: Send max 20-30 messages/day to avoid LinkedIn restrictions.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

PROFILE_DIR = os.path.join(os.path.dirname(__file__), '..', 'linkedin_session')

def get_driver():
    options = Options()
    options.add_argument(f"--user-data-dir={os.path.abspath(PROFILE_DIR)}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def linkedin_login(driver):
    """Open LinkedIn — user logs in manually once, session is saved."""
    driver.get("https://www.linkedin.com/login")
    print("⏳ Please LOGIN to LinkedIn in the browser window (30 seconds)...")
    time.sleep(30)  # Manual login time

def send_linkedin_message(linkedin_url, message, driver=None):
    """Send a LinkedIn message to a profile URL."""
    own_driver = driver is None
    if own_driver:
        driver = get_driver()

    try:
        driver.get(linkedin_url)
        time.sleep(4)

        # Try "Message" button directly
        try:
            msg_btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Message")]'))
            )
            msg_btn.click()
            time.sleep(3)
        except:
            # Try "Connect" then add note
            try:
                connect_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Connect")]'))
                )
                connect_btn.click()
                time.sleep(2)
                add_note = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Add a note")]')
                add_note.click()
                time.sleep(2)
            except Exception as e:
                print(f"❌ Could not open message box: {e}")
                return False

        # Type the message
        try:
            msg_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"] | //textarea[@name="message"]'))
            )
            msg_box.clear()
            msg_box.send_keys(message)
            time.sleep(2)

            # Send
            send_btn = driver.find_element(By.XPATH, '//button[contains(@type, "submit")] | //button[contains(text(), "Send")]')
            send_btn.click()
            time.sleep(3)
            print(f"✅ LinkedIn message sent to {linkedin_url}")
            return True
        except Exception as e:
            print(f"❌ Message send failed: {e}")
            return False

    finally:
        if own_driver:
            driver.quit()

def send_bulk_linkedin(contacts, message_template):
    """Send LinkedIn messages to multiple contacts."""
    results = {'success': 0, 'failed': 0, 'logs': []}
    driver = get_driver()

    try:
        # Check if logged in
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)
        if "login" in driver.current_url:
            linkedin_login(driver)

        for contact in contacts:
            url = (contact.linkedin_url or '').strip()
            if not url or 'linkedin.com' not in url:
                continue

            message = message_template\
                .replace('{{name}}', contact.name or 'there')\
                .replace('{{company}}', contact.company_name or '')\
                .replace('{{business_area}}', contact.business_area or '')

            print(f"💼 Sending LinkedIn message to {contact.name} ({url})...")
            ok = send_linkedin_message(url, message, driver=driver)

            results['logs'].append({
                'to_contact': url,
                'status': 'success' if ok else 'failed'
            })
            if ok:
                results['success'] += 1
            else:
                results['failed'] += 1

            time.sleep(8)  # LinkedIn rate limit — be careful

    finally:
        driver.quit()

    return results
