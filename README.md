# Government Complaint Portal

A Flask-based grievance portal for citizens to register local civic issues, track complaint status, and receive updates. The app includes an admin dashboard for reviewing complaints, updating statuses, and managing users.

## Features

- OTP-based citizen login
- Citizen dashboard with complaint counts and recent activity
- Multi-category complaint reporting
- Complaint tracking through Pending, In Progress, and Resolved states
- Citizen feedback after a complaint is resolved
- Admin login and complaint management dashboard
- Admin status updates with optional comments
- Email notifications for OTPs, complaint confirmations, and status updates
- MongoDB-backed users, complaints, complaint history, and counters collections

## Complaint Categories

The portal supports common public-service categories including:

- Infrastructure
- Water and Sanitation
- Electricity
- Healthcare
- Education
- Housing
- Waste Management
- Transport
- Law and Order
- Environment

## Tech Stack

- Python
- Flask
- MongoDB
- PyMongo
- HTML, CSS, and JavaScript
- Brevo email API for email delivery
- Gunicorn for production deployment

## MongoDB Collections

The app uses these collections:

- `users` - Citizen accounts, Aadhaar, phone, email, and login OTP state
- `complaints` - Complaint records and current status
- `complaint_history` - Admin status-change timeline entries
- `counters` - Numeric ID counters for users, complaints, and history entries

Numeric IDs are generated in MongoDB so existing URLs like `/admin/complaint/1` continue to work.

## Project Structure

- `app.py` - Main Flask application and MongoDB-backed route logic
- `api/index.py` - Serverless wrapper that imports the main Flask app
- `templates/` - HTML templates
- `static/css/` - Stylesheets
- `static/js/` - Frontend JavaScript
- `static/images/` - Complaint category and UI images
- `requirements.txt` - Python dependencies
- `Procfile` - Gunicorn start command
- `render.yaml` - Render deployment configuration

## Environment Variables

Required for MongoDB:

- `MONGO_URI` - MongoDB connection string, such as a MongoDB Atlas URI
- `MONGO_DB_NAME` - Database name, defaults to `government_complaint_portal`

Required for email delivery:

- `BREVO_API_KEY` - Brevo API key used to send OTP and notification emails
- `BREVO_SENDER_EMAIL` - Verified Brevo sender email address

General app settings:

- `SECRET_KEY` - Flask session secret
- `ADMIN_USERNAME` - Admin username, defaults to `admin`
- `ADMIN_PASSWORD` - Admin password, defaults to `admin123`

## Getting Started

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Set required environment variables.

PowerShell example:

```powershell
$env:SECRET_KEY="replace-with-a-secure-secret"
$env:MONGO_URI="mongodb+srv://user:password@cluster.example.mongodb.net/?retryWrites=true&w=majority"
$env:MONGO_DB_NAME="government_complaint_portal"
$env:BREVO_API_KEY="replace-with-your-brevo-api-key"
$env:BREVO_SENDER_EMAIL="your-verified-brevo-sender@example.com"
$env:ADMIN_USERNAME="admin"
$env:ADMIN_PASSWORD="admin123"
```

For local development, you can also run a local MongoDB server and use:

```powershell
$env:MONGO_URI="mongodb://localhost:27017/government_complaint_portal"
```

4. Run the app.

```bash
python app.py
```

5. Open the portal.

```text
http://localhost:5000
```

## Default Seed Users

When the MongoDB `users` collection is empty, the app seeds sample users:

- `user1@example.com` / Aadhaar `111122223333` / Phone `9876543210`
- `user2@example.com` / Aadhaar `444455556666` / Phone `9123456780`
- `dhanishkanth1122@gmail.com` / Aadhaar `777788889999` / Phone `9988776655`

## Render Deployment

The project includes deployment files for Render:

- `Procfile` starts the app with Gunicorn.
- `render.yaml` defines the web service and required environment variables.

When deploying from `render.yaml`, Render will prompt for values marked with `sync: false`. Add these in the Render dashboard or Blueprint setup screen:

- `MONGO_URI` - Paste your MongoDB Atlas connection string here.
- `BREVO_API_KEY` - Paste your Brevo API key here. Do not commit it to Git.
- `BREVO_SENDER_EMAIL` - Use the sender email verified in Brevo.
- `ADMIN_USERNAME` - Choose an admin username.
- `ADMIN_PASSWORD` - Choose a strong admin password.

`SECRET_KEY` is generated automatically by Render because `render.yaml` uses `generateValue: true`.

For production, rotate any API key that was shared publicly or committed accidentally, then store only the new value in Render environment variables.