# Gym Management System

A modern and responsive Gym Management System developed using **Python, Flask, SQLite, HTML, CSS, and Bootstrap** to simplify and manage day-to-day gym operations.

## Project Overview

The Gym Management System is a web-based application designed to help gym administrators efficiently manage members, membership plans, payments, attendance, and trainers through a centralized dashboard.

## Key Features

- **Dashboard:** Overview of gym activities and key statistics.
- **Member Management:** Add, update, view, search, and manage gym members.
- **Membership Plans:** Create and manage membership plans.
- **Payment Management:** Record and track member payments.
- **Attendance Tracking:** Manage daily member check-ins.
- **Trainer Management:** Maintain trainer information.
- **Reports:** View gym management and payment reports.
- **Responsive Interface:** Clean and user-friendly dashboard.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML5 | Frontend structure |
| CSS3 | Styling |
| Bootstrap | Responsive UI |

## Project Structure

```text
gym_management_system/
│
├── app.py
├── requirements.txt
├── gym.db
│
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
│
└── static/
    └── style.css
```

## Installation & Setup

**1. Clone the repository**

```bash
git clone https://github.com/mujaheed-creates/gym-management-system.git
```

**2. Navigate to the project folder**

```bash
cd gym-management-system
```

**3. Create a virtual environment**

```bash
python -m venv .venv
```

**4. Activate the virtual environment (Windows)**

```bash
.venv\Scripts\activate
```

**5. Install dependencies**

```bash
pip install -r requirements.txt
```

**6. Run the application**

```bash
python app.py
```

**7. Open in your browser**

```text
http://127.0.0.1:5000
```

## Learning Outcomes

Through this project, I gained practical experience in:

- Python backend development.
- Flask application development.
- SQLite database integration.
- CRUD operations.
- Web application structure and routing.
- Frontend and backend integration.
- Git and GitHub version control.

## Future Enhancements

- Admin authentication and role-based access.
- Advanced analytics and visual dashboards.
- Membership expiry notifications.
- Automated payment reminders.
- Deployment to a cloud platform.

## Author

**Mujaheed**

BCA Graduate | Aspiring Software Developer

GitHub: [@mujaheed-creates](https://github.com/mujaheed-creates)

---

*This project was developed as a practical learning project to demonstrate web development, database management, and Python programming skills.*
