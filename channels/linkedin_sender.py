"""
LinkedIn Sender — opens LinkedIn message URL in browser
No Selenium needed. Works on WSL/Windows.
"""
import subprocess
import urllib.parse
import time
import os

def open_linkedin_message(linkedin_url, message):
    """Open LinkedIn profile in browser so user can send message."""
    try:
        encoded = urllib.parse.quote(message)
        # LinkedIn messaging URL
        url = linkedin_url.strip()
        if not url or 'linkedin.com' not in url:
            return False

        # Open in Windows browser from WSL
        try:
            subprocess.Popen(['cmd.exe', '/c', 'start', '', url])
        except:
            subprocess.Popen(['xdg-open', url])

        print(f"✅ LinkedIn opened: {url}")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"❌ LinkedIn failed: {e}")
        return False

def send_bulk_linkedin(contacts, message_template):
    results = {'success': 0, 'failed': 0, 'logs': []}
    for contact in contacts:
        url = str(contact.linkedin_url or '').strip()
        if not url or 'linkedin.com' not in url:
            continue
        message = message_template \
            .replace('{{name}}', contact.name or 'there') \
            .replace('{{company}}', contact.company_name or '') \
            .replace('{{business_area}}', contact.business_area or '')
        print(f"💼 Opening LinkedIn for {contact.name}...")
        ok = open_linkedin_message(url, message)
        results['logs'].append({'to_contact': url, 'status': 'success' if ok else 'failed'})
        if ok: results['success'] += 1
        else:   results['failed'] += 1
        time.sleep(4)
    return results
