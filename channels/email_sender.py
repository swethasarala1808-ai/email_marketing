"""
Email Sender — Hostinger SMTP
Supports both TLS (port 587) and SSL (port 465)
"""
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
import os
import time

def send_email(to_email, name, company, subject, html_content):
    smtp_server  = os.getenv('SMTP_SERVER',    'smtp.hostinger.com')
    smtp_port    = int(os.getenv('SMTP_PORT',  '465'))
    smtp_user    = os.getenv('SMTP_USERNAME',  '')
    smtp_pass    = os.getenv('SMTP_PASSWORD',  '')
    from_email   = os.getenv('SMTP_FROM_EMAIL', smtp_user)

    if not smtp_user or not smtp_pass:
        print("❌ SMTP credentials missing — check your .env file")
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = (subject or '')  \
        .replace('{{name}}', name or '') \
        .replace('{{company}}', company or '')
    msg['From']    = f"bizaxl <{from_email}>"
    msg['To']      = to_email

    body = (html_content or '') \
        .replace('{{name}}',          name    or 'there') \
        .replace('{{company}}',       company or '') \
        .replace('{{business_area}}', '') \
        .replace('{{unsubscribe_link}}', '#')
    msg.attach(MIMEText(body, 'html'))

    # Try SSL (port 465) first — most reliable for Hostinger
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, 465, context=context, timeout=30) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            print(f"✅ Email sent to {to_email} (SSL)")
            return True
    except Exception as e1:
        print(f"SSL failed ({e1}), trying TLS...")
        # Fallback: TLS port 587
        try:
            with smtplib.SMTP(smtp_server, 587, timeout=30) as server:
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                print(f"✅ Email sent to {to_email} (TLS)")
                return True
        except Exception as e2:
            print(f"❌ Both SSL and TLS failed for {to_email}: {e2}")
            return False


def send_bulk_email(contacts, subject, html_content):
    results = {'success': 0, 'failed': 0, 'logs': []}
    for contact in contacts:
        email = str(contact.email or '').strip()
        if not email or email == 'nan':
            continue
        ok = send_email(
            email,
            contact.name        or 'there',
            contact.company_name or '',
            subject,
            html_content
        )
        results['logs'].append({
            'to_contact': email,
            'status': 'success' if ok else 'failed'
        })
        if ok:
            results['success'] += 1
        else:
            results['failed'] += 1
        time.sleep(1)   # small delay between sends
    return results
