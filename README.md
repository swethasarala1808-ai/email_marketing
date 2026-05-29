# 🚀 BizAxl Multi-Channel Outreach App

Send **Email + WhatsApp + LinkedIn** messages to 100–1,000 people per day from one dashboard.

## ✨ Features

| Channel | How it works | Daily Limit |
|---------|-------------|-------------|
| 📧 Email | Hostinger SMTP | 500–1000/day |
| 📱 WhatsApp | WhatsApp Web (scan QR once) | 100–200/day |
| 💼 LinkedIn | LinkedIn Web (login once) | 20–30/day |

## 🚀 Quick Start

```bash
git clone https://github.com/swethasarala1808-ai/outreach-app.git
cd outreach-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Hostinger email password
python3 app.py
```

Open: **http://localhost:5000**

## 📋 How to Use

### 1. Add Contacts
- Add manually (name, email, phone, LinkedIn URL)
- Or import CSV with columns: `name, email, phone, linkedin_url, company_name, business_area`
- **Phone format for WhatsApp**: `919876543210` (country code + number, no + or spaces)

### 2. Create a Template
- Click **"+ Create New Template"**
- Choose channel: Email / WhatsApp / LinkedIn
- Click a **starter template** button to load a ready-made message
- Customize with your content
- Use `{{name}}`, `{{company}}`, `{{business_area}}` for personalisation

### 3. Send Campaign
- **Email**: Enter how many to send (e.g. 100) → Click "Send Emails"
- **WhatsApp**: Enter phone in test box → click "Test Send" first → then "Send to All"
- **LinkedIn**: Click "Send to All" (max 20/day recommended)

## 📱 WhatsApp Setup (First Time)
1. Click "Test Send" with your own number
2. Chrome will open WhatsApp Web
3. **Scan the QR code** with your phone
4. Session is saved — you won't need to scan again

## 💼 LinkedIn Setup (First Time)
1. Click "Send to All" for a LinkedIn template
2. Chrome opens LinkedIn login
3. **Login manually** (30 seconds)
4. Session is saved — you won't need to login again

## ⚠️ Important Limits
- **WhatsApp**: Don't send more than 100-200/day to avoid being banned
- **LinkedIn**: Max 20-30 messages/day to avoid account restriction
- **Email**: Up to 500/day with Hostinger free plan
