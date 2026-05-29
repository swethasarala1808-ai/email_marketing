"""
WhatsApp Bulk Sender using WhatsApp Web (selenium)
----------------------------------------------------
HOW IT WORKS:
1. Opens WhatsApp Web in Chrome
2. You scan the QR code ONCE (first time)
3. After login, it sends messages to all contacts automatically

REQUIREMENTS:
- Google Chrome installed
- pip install selenium webdriver-manager
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse
import os

# Persist WhatsApp Web session so you only scan QR once
PROFILE_DIR = os.path.join(os.path.dirname(__file__), '..', 'whatsapp_session')

def get_driver():
    options = Options()
    options.add_argument(f"--user-data-dir={os.path.abspath(PROFILE_DIR)}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--headless")  # Uncomment after first QR scan
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def send_whatsapp_message(phone_number, message):
    """
    Send a WhatsApp message to a phone number.
    Phone number format: country code + number, e.g. 919876543210 (no + or spaces)
    """
    driver = get_driver()
    try:
        encoded_msg = urllib.parse.quote(message)
        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_msg}"
        driver.get(url)

        # Wait for page to load and QR to be scanned (first time)
        print(f"⏳ Opening WhatsApp Web for {phone_number}...")
        time.sleep(12)

        # Wait for the send button
        try:
            send_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
            )
            send_btn.click()
            time.sleep(3)
            print(f"✅ WhatsApp sent to {phone_number}")
            return True
        except Exception as e:
            # Try pressing Enter as fallback
            try:
                input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                input_box.send_keys(Keys.ENTER)
                time.sleep(3)
                return True
            except:
                print(f"❌ Failed to send to {phone_number}: {e}")
                return False
    finally:
        driver.quit()

def send_bulk_whatsapp(contacts, message_template):
    """Send bulk WhatsApp messages to a list of contacts."""
    results = {'success': 0, 'failed': 0, 'logs': []}

    for contact in contacts:
        phone = (contact.phone or '').strip().replace('+', '').replace(' ', '').replace('-', '')
        if not phone:
            continue

        message = message_template\
            .replace('{{name}}', contact.name or 'there')\
            .replace('{{company}}', contact.company_name or '')\
            .replace('{{business_area}}', contact.business_area or '')

        print(f"📱 Sending WhatsApp to {phone} ({contact.name})...")
        ok = send_whatsapp_message(phone, message)

        results['logs'].append({
            'to_contact': phone,
            'status': 'success' if ok else 'failed'
        })
        if ok:
            results['success'] += 1
        else:
            results['failed'] += 1

        time.sleep(3)  # Avoid rate limits

    return results
