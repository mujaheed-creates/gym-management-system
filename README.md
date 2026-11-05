# FitTrack Gym Management System

A local gym management web app built with Python, Flask, and SQLite.

## Features
- Dashboard with member, revenue, trainer, and daily attendance stats
- Member create, read, update, delete and search
- Membership plan management
- Payment records with payment method
- Daily attendance check-in
- Trainer records
- Revenue and payment-method reports
- SQLite database created automatically on first run with sample records

## Requirements
- Python 3.10 or newer
- Windows, macOS, or Linux

## Setup (Windows)
1. Extract the ZIP file.
2. Open the extracted `gym_management_system` folder.
3. Open Command Prompt or PowerShell in that folder.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\activate
   ```

5. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   python app.py
   ```

7. Open `http://127.0.0.1:5000` in your browser.

The app creates `gym.db` automatically in the project folder and inserts sample data on first run.

## Stop the app
Press `Ctrl + C` in the terminal.

## Database backup
Stop the app and copy `gym.db` to a safe location. To reset all data, stop the app and delete `gym.db`; it will be recreated on next start.

## Important before real-world deployment
This is a learning/demo starter, not a production-hardened system. Before deploying publicly:
- Replace `app.secret_key` with a long random secret stored in an environment variable.
- Add authentication, role-based permissions, CSRF protection, input validation, and audit logging.
- Use a production WSGI server (for example, Waitress on Windows or Gunicorn on Linux); do not use Flask debug mode.
- Configure HTTPS, backups, and privacy/security controls.
- Add membership expiry calculations and automated payment receipts if required.

## Project structure
```
gym_management_system/
├── app.py
├── requirements.txt
├── README.md
├── gym.db                 # created automatically on first run
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── members.html
│   ├── member_form.html
│   ├── plans.html
│   ├── payments.html
│   ├── attendance.html
│   ├── trainers.html
│   └── reports.html
└── static/
    └── style.css
```
