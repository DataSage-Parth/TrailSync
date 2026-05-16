# 🏕️ TrailSync - Trekking Management Application

A comprehensive Flask-based web application for managing adventure trekking activities. It streamlines operations for administrators, empowers trek staff to manage participants, and allows users to easily book and track their expeditions.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)](https://www.sqlite.org/)
---

## ✨ Features

### 🔐 Role-Based Access Control
Three distinct user portals with specific permissions:

#### Admin Portal
- Comprehensive dashboard with system-wide statistics and data visualizations (Chart.js)
- Complete user and staff management
  - View, search, and manage registered trekkers and staff members
  - Activate or blacklist users and staff
- Complete Trek lifecycle management
  - Create, edit, and delete trekking expeditions
  - Assign specific staff members to guide treks
- Global bookings oversight across all treks
- Contextual search functionality within every module

#### Staff Portal
- Dedicated dashboard displaying assigned treks
- Dynamic slot tracking and management
- Ability to update trek statuses (e.g., Open, Completed)
- View and manage participant rosters for specific treks

#### User (Trekker) Portal
- Browse and explore available treks with advanced search and filtering (by location, difficulty)
- Single-click trek booking system with real-time slot validation
- View active bookings and easily cancel if needed
- Maintain a permanent history of completed treks
- Profile management

---

## 🛠 Technology Stack

### Backend
- **Flask** — Lightweight Python web framework
- **Flask-SQLAlchemy** — ORM for database operations
- **Werkzeug** — Password hashing and security utilities

### Frontend
- **HTML5 / CSS3 / Vanilla JS** — Structure and styling
- **Jinja2** — Template engine
- **Bootstrap 5** — Responsive UI framework
- **Chart.js** — Interactive dashboard visualizations

### Database
- **SQLite** — Lightweight relational database

---

## 🗄 Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│      USER       │
│─────────────────│
│ id (PK)         │
│ username        │
│ email (UNIQUE)  │
│ password        │
│ full_name       │
│ role            │
│ status          │
└─────────────────┘
        │
   ─────┴─────
   │         │
   │ 1:N     │ 1:N
   ▼         ▼
┌──────────────┐    ┌──────────────────┐
│   BOOKING    │    │      TREK        │
│──────────────│    │──────────────────│
│ id (PK)      │    │ id (PK)          │
│ user_id (FK) │    │ assigned_staff   │
│ trek_id (FK) │    │ name             │
│ status       │    │ location         │
│ booking_date │    │ total_slots      │
└──────────────┘    │ status           │
                    └──────────────────┘
```

---

## 📡 Route Design

### Authentication
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET, POST | `/login` | User/Admin login | Public |
| GET, POST | `/register` | New trekker registration | Public |
| GET | `/logout` | Terminate session | Authenticated |

### Admin Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/admin/` | Admin dashboard with statistics | Admin |
| GET, POST | `/admin/treks/add` | Create a new trek | Admin |
| GET, POST | `/admin/treks/<id>/edit` | Edit a trek | Admin |
| POST | `/admin/treks/<id>/delete` | Delete a trek | Admin |
| GET, POST | `/admin/staff/add` | Add new staff member | Admin |
| POST | `/admin/users/<id>/toggle` | Blacklist/Activate user | Admin |
| GET | `/admin/bookings` | View global bookings | Admin |

### Staff Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/staff/` | Staff dashboard | Staff |
| GET, POST | `/staff/trek/<id>` | Manage specific assigned trek | Staff |

### User Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/user/dashboard` | User dashboard overview | User |
| GET | `/user/treks` | Browse available treks | User |
| GET | `/user/treks/<id>` | View trek details | User |
| POST | `/user/treks/<id>/book` | Book a slot | User |
| GET | `/user/history` | View completed treks | User |

### REST API
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/treks` | Get all open treks | Public |
| GET | `/api/treks/<id>` | Get specific trek details | Public |
| GET | `/api/users/<id>` | Get user details | Public |
| GET | `/api/bookings/<id>`| Get booking details | Public |

---

## 📁 Project Structure

```
Trekking_management/
│
├── app.py                      # Application entry point
├── models.py                   # SQLAlchemy models
├── config.py                   # Configuration settings
├── helpers.py                  # Utility functions
├── seed.py                     # Demo data generator
│
├── routes/                     # Blueprint definitions
│   ├── __init__.py
│   ├── auth.py
│   ├── admin.py
│   ├── staff.py
│   ├── user.py
│   └── api.py
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html
│   ├── landing.html
│   ├── auth/
│   ├── admin/
│   ├── staff/
│   └── user/
│
├── static/
│   └── css/style.css           # Custom stylesheets
│
└── instance/                   # SQLite database
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-link>
cd Trekking_management

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Generate Demo Data (Optional but recommended)
python seed.py

# 6. Run the application
python app.py
```

> ⚠️ **Note:** The `seed.py` script is provided strictly for generating demo data and populating the database during development or evaluation. It should not be included in your main production project deployment.

The application will start on **http://127.0.0.1:5000**

---

## 🔑 Demo Credentials

If you generated data using `seed.py`, you can use the following credentials to explore the system:

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Staff** | `staff_alex_1` | `password123` |
| **User** | `trekker_alex_1` | `password123` |

*(Note: The seed script randomly generates first names, so the exact staff and user usernames will vary, but their passwords are always `password123`.)*

---
<div align="center">
Made with ❤️ by Parth Sharma
</div>
