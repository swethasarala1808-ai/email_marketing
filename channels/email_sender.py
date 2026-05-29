from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

def send_email(to_email, name, company, subject, html_content):
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.hostinger.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject.replace('{{name}}', name).replace('{{company}}', company)
    msg['From'] = from_email
    msg['To'] = to_email

    body = html_content.replace('{{name}}', name).replace('{{company}}', company)
    body = body.replace('{{unsubscribe_link}}', '#')
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed to {to_email}: {e}")
        return False

def send_bulk_email(contacts, subject, html_content):
    results = {'success': 0, 'failed': 0, 'logs': []}
    for contact in contacts:
        if not contact.email:
            continue
        ok = send_email(contact.email, contact.name or 'Team',
                        contact.company_name or '', subject, html_content)
        results['logs'].append({
            'to_contact': contact.email,
            'status': 'success' if ok else 'failed'
        })
        if ok:
            results['success'] += 1
        else:
            results['failed'] += 1
    return results
