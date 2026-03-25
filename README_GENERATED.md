# Sovereign Justice: National Grievance Portal 🏛️

A modern, secure, and user-centric platform designed to bridge the gap between citizens and administration. This portal empowers citizens to report local issues across multiple categories and track them in real-time, while providing administrators with a robust suite of tools to manage and resolve grievances efficiently.

## ✨ Key Features

### 👤 Citizen Dashboard
- **Real-time Analytics**: Instant overview of total, pending, and resolved complaints.
- **Complaint Tracking**: Detailed history and current status of every grievance submitted.
- **Success Stories**: A carousel of recently resolved issues to foster trust and community engagement.

### 📝 Grievance Management
- **Multi-Category Reporting**: Support for Infrastructure, Water, Electricity, Healthcare, Education, and more.
- **Secure Authentication**: OTP-based login verified through automated email systems.
- **Feedback Loop**: Citizens can provide feedback once an issue is marked as "Resolved."

### 🛡️ Admin Command Center
- **Unified Management**: Centralized dashboard to monitor all incoming grievances.
- **Status Updates**: Seamless workflow to move complaints from "Pending" to "In Progress" and "Resolved."
- **Internal Comments**: Admins can add notes and attach images for status updates.

### 📧 Automated Notifications
- **Registration Alerts**: Instant email confirmation upon complaint submission.
- **Status Updates**: Real-time email notifications whenever an admin updates the status of a grievance.

## 🛠️ Tech Stack

- **Framework**: [Flask](https://flask.palletsprojects.com/) (Python)
- **Database**: [SQLAlchemy](https://www.sqlalchemy.org/) (SQLite for portability)
- **Email Services**: [Flask-Mail](https://pythonhosted.org/Flask-Mail/)
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism UI), and JavaScript.
- **Production Server**: [Gunicorn](https://gunicorn.org/)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- A Gmail account (for OTP and notifications)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/sovereign-justice.git
   cd sovereign-justice
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   Create environment variables for your email credentials:
   - `MAIL_USERNAME`: Your Gmail address
   - `MAIL_PASSWORD`: Your Gmail App Password

4. **Run the application**:
   ```bash
   python app.py
   ```
   Access the portal at `http://localhost:5000`.

## 🌐 Deployment

This project is ready for deployment on platforms like **Render**, **Railway**, or **PythonAnywhere**. 

- **Procfile**: Included for Gunicorn support.
- **Waitress/Gunicorn**: Configured for production-grade performance.

---
*Built with ❤️ for a better tomorrow.*
