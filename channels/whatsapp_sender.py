"""
WhatsApp Bulk Sender using WhatsApp Web (Selenium)
---------------------------------------------------
Uses Chrome already installed on your system.
First time: scan QR code once. Session saved after that.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import time
import urllib.parse
import os

PROFILE_DIR = os.path.join(os.path.dirname(__file__), '..', 'whatsapp_session')

def get_chrome_driver_path():
    """Find matching chromedriver for installed Chrome version."""
    try:
        # Get Chrome version
        result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
        version = result.stdout.strip().split()[-1]  # e.g. 148.0.7778.215
        major = version.split('.')[0]                # e.g. 148
        print(f"Chrome version: {version} (major: {major})")

        # Download matching chromedriver
        import urllib.request, zipfile, stat
        driver_dir = os.path.expanduser(f'~/.chromedriver/{major}')
        driver_path = os.path.join(driver_dir, 'chromedriver')

        if os.path.exists(driver_path):
            print(f"Using cached chromedriver: {driver_path}")
            return driver_path

        os.makedirs(driver_dir, exist_ok=True)
        url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/linux64/chromedriver-linux64.zip"
        zip_path = os.path.join(driver_dir, 'chromedriver.zip')

        print(f"Downloading chromedriver {version}...")
        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as z:
            for member in z.namelist():
                if member.endswith('chromedriver') and '/' in member:
                    data = z.read(member)
                    with open(driver_path, 'wb') as f:
                        f.write(data)
                    break

        os.chmod(driver_path, os.stat(driver_path).st_mode | stat.S_IEXEC)
        os.remove(zip_path)
        print(f"✅ Chromedriver ready: {driver_path}")
        return driver_path

    except Exception as e:
        print(f"Chromedriver download failed: {e}")
        # Fallback: try system chromedriver
        for path in ['/usr/bin/chromedriver', '/usr/local/bin/chromedriver']:
            if os.path.exists(path):
                return path
        return None

def get_driver():
    options = Options()
    options.add_argument(f"--user-data-dir={os.path.abspath(PROFILE_DIR)}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver_path = get_chrome_driver_path()
    if driver_path:
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    return driver

def send_whatsapp_message(phone_number, message):
    """
    Send a WhatsApp message to a phone number.
    Format: country code + number e.g. 919876543210
    """
    phone_number = str(phone_number).strip().replace('+','').replace(' ','').replace('-','')
    driver = get_driver()
    try:
        encoded_msg = urllib.parse.quote(message)
        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_msg}"
        driver.get(url)

        print(f"⏳ Opening WhatsApp Web for {phone_number}...")
        print("👉 SCAN QR CODE if prompted (first time only — 30 seconds)")
        time.sleep(15)

        try:
            send_btn = WebDriverWait(driver, 25).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
            )
            send_btn.click()
            time.sleep(3)
            print(f"✅ WhatsApp sent to {phone_number}")
            return True
        except:
            try:
                box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                box.send_keys(Keys.ENTER)
                time.sleep(3)
                return True
            except Exception as e:
                print(f"❌ Failed: {e}")
                return False
    finally:
        driver.quit()

def send_bulk_whatsapp(contacts, message_template):
    results = {'success': 0, 'failed': 0, 'logs': []}
    for contact in contacts:
        phone = str(contact.phone or '').strip().replace('+','').replace(' ','').replace('-','')
        if not phone or phone in ('', 'nan'):
            continue
        message = message_template\
            .replace('{{name}}', contact.name or 'there')\
            .replace('{{company}}', contact.company_name or '')\
            .replace('{{business_area}}', contact.business_area or '')
        print(f"📱 Sending to {phone} ({contact.name})...")
        ok = send_whatsapp_message(phone, message)
        results['logs'].append({'to_contact': phone, 'status': 'success' if ok else 'failed'})
        if ok: results['success'] += 1
        else:  results['failed'] += 1
        time.sleep(4)
    return results
