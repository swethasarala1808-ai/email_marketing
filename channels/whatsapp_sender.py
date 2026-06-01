"""
WhatsApp Sender — uses WhatsApp Web via direct URL
Opens your default browser, you click send once per message.
For bulk: use WhatsApp Business API (recommended for 100+/day)
"""
import subprocess
import urllib.parse
import time
import os
import webbrowser

def send_whatsapp_message(phone_number, message):
    """
    Opens WhatsApp Web with the message pre-filled.
    Phone format: 919876543210 (country code + number, no + or spaces)
    """
    phone = str(phone_number).strip().replace('+','').replace(' ','').replace('-','')
    if not phone or phone == 'nan':
        return False

    encoded_msg = urllib.parse.quote(message)
    url = f"https://api.whatsapp.com/send?phone={phone}&text={encoded_msg}"

    try:
        # Try to open in Windows browser (WSL environment)
        windows_browsers = [
            '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe',
            '/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe',
            '/mnt/c/Windows/System32/cmd.exe',
        ]

        opened = False
        for browser in windows_browsers:
            if os.path.exists(browser):
                if 'cmd.exe' not in browser:
                    subprocess.Popen([browser, url])
                    opened = True
                    break

        if not opened:
            # WSL: use explorer to open URL in Windows browser
            subprocess.Popen(['cmd.exe', '/c', 'start', '', url])

        print(f"✅ WhatsApp Web opened for {phone} — message pre-filled, just press Send!")
        time.sleep(2)
        return True

    except Exception as e:
        print(f"❌ Failed to open WhatsApp for {phone}: {e}")
        # Last resort: print the URL for manual use
        print(f"   Open manually: {url}")
        return False


def send_bulk_whatsapp(contacts, message_template):
    """Open WhatsApp Web for each contact with message pre-filled."""
    results = {'success': 0, 'failed': 0, 'logs': []}

    for contact in contacts:
        phone = str(contact.phone or '').strip().replace('+','').replace(' ','').replace('-','')
        if not phone or phone in ('', 'nan'):
            continue

        message = message_template \
            .replace('{{name}}', contact.name or 'there') \
            .replace('{{company}}', contact.company_name or '') \
            .replace('{{business_area}}', contact.business_area or '')

        print(f"📱 Opening WhatsApp for {phone} ({contact.name})...")
        ok = send_whatsapp_message(phone, message)

        results['logs'].append({
            'to_contact': phone,
            'status': 'success' if ok else 'failed'
        })
        if ok:
            results['success'] += 1
        else:
            results['failed'] += 1

        time.sleep(5)  # Give time to send each message

    return results
