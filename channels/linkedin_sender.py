"""
LinkedIn Bulk Message Sender (Selenium)
Login manually once — session is saved after that.
Max 20-30 messages/day to avoid LinkedIn restrictions.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess, time, os, urllib.parse, stat

PROFILE_DIR = os.path.join(os.path.dirname(__file__), '..', 'linkedin_session')

def get_chrome_driver_path():
    try:
        result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
        version = result.stdout.strip().split()[-1]
        major = version.split('.')[0]
        import urllib.request, zipfile
        driver_dir = os.path.expanduser(f'~/.chromedriver/{major}')
        driver_path = os.path.join(driver_dir, 'chromedriver')
        if os.path.exists(driver_path):
            return driver_path
        os.makedirs(driver_dir, exist_ok=True)
        url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/linux64/chromedriver-linux64.zip"
        zip_path = os.path.join(driver_dir, 'chromedriver.zip')
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
        return driver_path
    except Exception as e:
        print(f"Driver error: {e}")
        for p in ['/usr/bin/chromedriver', '/usr/local/bin/chromedriver']:
            if os.path.exists(p):
                return p
        return None

def get_driver():
    options = Options()
    options.add_argument(f"--user-data-dir={os.path.abspath(PROFILE_DIR)}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    driver_path = get_chrome_driver_path()
    if driver_path:
        driver = webdriver.Chrome(service=Service(driver_path), options=options)
    else:
        driver = webdriver.Chrome(options=options)
    return driver

def send_linkedin_message(linkedin_url, message, driver=None):
    own_driver = driver is None
    if own_driver:
        driver = get_driver()
    try:
        driver.get(linkedin_url)
        time.sleep(4)
        try:
            msg_btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Message")]'))
            )
            msg_btn.click()
            time.sleep(3)
        except:
            try:
                connect_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Connect")]'))
                )
                connect_btn.click()
                time.sleep(2)
                note_btn = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Add a note")]')
                note_btn.click()
                time.sleep(2)
            except Exception as e:
                print(f"❌ Could not open message: {e}")
                return False
        try:
            msg_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"] | //textarea[@name="message"]'))
            )
            msg_box.clear()
            msg_box.send_keys(message)
            time.sleep(2)
            send_btn = driver.find_element(By.XPATH, '//button[@type="submit"] | //button[contains(text(),"Send")]')
            send_btn.click()
            time.sleep(3)
            print(f"✅ LinkedIn message sent to {linkedin_url}")
            return True
        except Exception as e:
            print(f"❌ Message failed: {e}")
            return False
    finally:
        if own_driver:
            driver.quit()

def send_bulk_linkedin(contacts, message_template):
    results = {'success': 0, 'failed': 0, 'logs': []}
    driver = get_driver()
    try:
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)
        if "login" in driver.current_url:
            print("⏳ Please LOGIN to LinkedIn in the browser (30 seconds)...")
            driver.get("https://www.linkedin.com/login")
            time.sleep(35)

        for contact in contacts:
            url = str(contact.linkedin_url or '').strip()
            if not url or 'linkedin.com' not in url:
                continue
            message = message_template\
                .replace('{{name}}', contact.name or 'there')\
                .replace('{{company}}', contact.company_name or '')\
                .replace('{{business_area}}', contact.business_area or '')
            print(f"💼 Sending to {contact.name} ({url})...")
            ok = send_linkedin_message(url, message, driver=driver)
            results['logs'].append({'to_contact': url, 'status': 'success' if ok else 'failed'})
            if ok: results['success'] += 1
            else:  results['failed'] += 1
            time.sleep(8)
    finally:
        driver.quit()
    return results
