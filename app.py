from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
import threading
import schedule
import time

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'outreach-secret-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///outreach.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ─── Models ───────────────────────────────────────────────────────────────────

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='')
    email = db.Column(db.String(120), default='')
    phone = db.Column(db.String(20), default='')        # WhatsApp number
    linkedin_url = db.Column(db.String(300), default='')
    company_name = db.Column(db.String(100), default='')
    business_area = db.Column(db.String(100), default='')
    added_date = db.Column(db.DateTime, default=datetime.utcnow)

class MessageTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    channel = db.Column(db.String(20), nullable=False)  # email, whatsapp, linkedin
    subject = db.Column(db.String(200), default='')
    message_content = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class CampaignLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    to_contact = db.Column(db.String(200))
    template_name = db.Column(db.String(100))
    channel = db.Column(db.String(20))
    status = db.Column(db.String(20))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

# ─── Routes: Contacts ─────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    contacts = Contact.query.order_by(Contact.added_date.desc()).all()
    templates = MessageTemplate.query.all()
    logs = CampaignLog.query.order_by(CampaignLog.sent_at.desc()).limit(30).all()
    stats = {
        'total_contacts': Contact.query.count(),
        'total_sent': CampaignLog.query.filter_by(status='success').count(),
        'total_failed': CampaignLog.query.filter_by(status='failed').count(),
        'whatsapp_sent': CampaignLog.query.filter_by(channel='whatsapp', status='success').count(),
        'linkedin_sent': CampaignLog.query.filter_by(channel='linkedin', status='success').count(),
        'email_sent': CampaignLog.query.filter_by(channel='email', status='success').count(),
    }
    return render_template('index.html', contacts=contacts, templates=templates, logs=logs, stats=stats)

@app.route('/add_contact', methods=['POST'])
def add_contact():
    contact = Contact(
        name=request.form.get('name', ''),
        email=request.form.get('email', ''),
        phone=request.form.get('phone', ''),
        linkedin_url=request.form.get('linkedin_url', ''),
        company_name=request.form.get('company_name', ''),
        business_area=request.form.get('business_area', '')
    )
    db.session.add(contact)
    db.session.commit()
    flash('Contact added!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_contact/<int:cid>', methods=['POST'])
def delete_contact(cid):
    db.session.delete(Contact.query.get_or_404(cid))
    db.session.commit()
    flash('Contact deleted.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/bulk_import', methods=['POST'])
def bulk_import():
    import pandas as pd
    file = request.files.get('csv_file')
    if not file:
        flash('No file!', 'error')
        return redirect(url_for('dashboard'))
    try:
        df = pd.read_csv(file)
        added = 0
        for _, row in df.iterrows():
            c = Contact(
                name=str(row.get('name', '')),
                email=str(row.get('email', '')),
                phone=str(row.get('phone', '')),
                linkedin_url=str(row.get('linkedin_url', '')),
                company_name=str(row.get('company_name', '')),
                business_area=str(row.get('business_area', ''))
            )
            db.session.add(c)
            added += 1
        db.session.commit()
        flash(f'Imported {added} contacts!', 'success')
    except Exception as e:
        flash(f'Import error: {e}', 'error')
    return redirect(url_for('dashboard'))

# ─── Routes: Templates ────────────────────────────────────────────────────────

@app.route('/create_template', methods=['GET', 'POST'])
def create_template():
    if request.method == 'POST':
        t = MessageTemplate(
            name=request.form['name'],
            channel=request.form['channel'],
            subject=request.form.get('subject', ''),
            message_content=request.form['message_content']
        )
        db.session.add(t)
        db.session.commit()
        flash('Template created!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('template_builder.html')

@app.route('/edit_template/<int:tid>', methods=['GET', 'POST'])
def edit_template(tid):
    t = MessageTemplate.query.get_or_404(tid)
    if request.method == 'POST':
        t.name = request.form['name']
        t.channel = request.form['channel']
        t.subject = request.form.get('subject', '')
        t.message_content = request.form['message_content']
        db.session.commit()
        flash('Template updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('template_builder.html', template=t)

@app.route('/delete_template/<int:tid>', methods=['POST'])
def delete_template(tid):
    db.session.delete(MessageTemplate.query.get_or_404(tid))
    db.session.commit()
    flash('Template deleted.', 'success')
    return redirect(url_for('dashboard'))

# ─── Routes: Send Campaigns ───────────────────────────────────────────────────

@app.route('/send_email_campaign/<int:tid>', methods=['POST'])
def send_email_campaign(tid):
    from channels.email_sender import send_bulk_email
    template = MessageTemplate.query.get_or_404(tid)
    limit = int(request.form.get('limit', 100))
    contacts = Contact.query.filter(Contact.email != '').all()[:limit]
    results = send_bulk_email(contacts, template.subject, template.message_content)
    for log in results['logs']:
        db.session.add(CampaignLog(**log, template_name=template.name, channel='email'))
    db.session.commit()
    flash(f'📧 Email campaign done! ✅ {results["success"]} sent, ❌ {results["failed"]} failed.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/send_whatsapp_campaign/<int:tid>', methods=['POST'])
def send_whatsapp_campaign(tid):
    from channels.whatsapp_sender import send_bulk_whatsapp
    template = MessageTemplate.query.get_or_404(tid)
    limit = int(request.form.get('limit', 50))
    contacts = Contact.query.filter(Contact.phone != '').all()[:limit]
    results = send_bulk_whatsapp(contacts, template.message_content)
    for log in results['logs']:
        db.session.add(CampaignLog(**log, template_name=template.name, channel='whatsapp'))
    db.session.commit()
    flash(f'📱 WhatsApp campaign done! ✅ {results["success"]} sent, ❌ {results["failed"]} failed.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/send_linkedin_campaign/<int:tid>', methods=['POST'])
def send_linkedin_campaign(tid):
    from channels.linkedin_sender import send_bulk_linkedin
    template = MessageTemplate.query.get_or_404(tid)
    limit = int(request.form.get('limit', 20))
    contacts = Contact.query.filter(Contact.linkedin_url != '').all()[:limit]
    results = send_bulk_linkedin(contacts, template.message_content)
    for log in results['logs']:
        db.session.add(CampaignLog(**log, template_name=template.name, channel='linkedin'))
    db.session.commit()
    flash(f'💼 LinkedIn campaign done! ✅ {results["success"]} sent, ❌ {results["failed"]} failed.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/test_whatsapp/<int:tid>', methods=['POST'])
def test_whatsapp(tid):
    from channels.whatsapp_sender import send_whatsapp_message
    template = MessageTemplate.query.get_or_404(tid)
    phone = request.form.get('test_phone', '').strip()
    if not phone:
        flash('Enter a phone number!', 'error')
        return redirect(url_for('dashboard'))
    msg = template.message_content.replace('{{name}}', 'Test').replace('{{company}}', 'Test Co')
    success = send_whatsapp_message(phone, msg)
    flash(f'{"✅ WhatsApp sent!" if success else "❌ Failed — check terminal for errors"}', 'success' if success else 'error')
    return redirect(url_for('dashboard'))

@app.route('/api/stats')
def api_stats():
    return jsonify({
        'contacts': Contact.query.count(),
        'sent': CampaignLog.query.filter_by(status='success').count(),
    })

# ─── Scheduler ────────────────────────────────────────────────────────────────

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(debug=True, port=5000)
