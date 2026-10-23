# Campus Complaint Portal

A faithful full-stack reconstruction of the **Campus Complaint Portal** developed during the Full Stack Python internship at Knovative Technologies, matching the original UI design, color schemes, typography, layout, and functionality documented in the internship report.

---

## 📋 Features

- **Public Landing Page**: Horizontal navigation, logo, hero banner with campus photograph overlay, call-to-action buttons, and 4 feature cards (*Easy Reporting*, *Track Status*, *Quick Resolution*, *Better Campus*).
- **Split-Screen Authentication**: Left-side branded illustrated panel with right-side form for Student Registration and Student Login.
- **Student Dashboard**: 4 live metric cards (*Total Complaints*, *Pending*, *In Progress*, *Resolved*), recent complaints table with colored status badges, and quick actions.
- **Complaint Submission & Tracking**: Multi-category complaint filing (*WiFi, Classroom, Hostel, Library, Laboratory, Transport, Canteen, Others*), auto-generation of unique complaint IDs (e.g., `CMP012`), real-time status tracking, and strict student data isolation.
- **Administrator Dashboard**: System-wide complaint metrics, Chart.js *Complaints by Category* bar chart, *Complaints Status* doughnut chart with center total label, and live statistics.
- **Complaint Management**: Search and status filtering, complaint detail inspection, status updates (*Pending &rarr; In Progress &rarr; Resolved*), and administrator remarks.
- **Analytical Reports**: Category-wise distribution pie chart with percentage shares and summary panel.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, Flask, Jinja2 Templates, Flask Sessions, Werkzeug Password Hashing
- **Database**: MySQL 8.0+ (PyMySQL connector) with automatic fallback to SQLite for local development / testing
- **Frontend**: Custom CSS3, HTML5, Vanilla JavaScript, Chart.js (included locally)
- **Testing**: pytest

---

## 🚀 Windows PowerShell Setup and Execution Guide

### 1. Prerequisites
- **Python 3.12 or newer** installed and available in PATH.
- **MySQL Server** (via MySQL Community Server, XAMPP, or Laragon).

---

### 2. Set Up Virtual Environment

Open **Windows PowerShell** in the project directory:

```powershell
cd C:\Users\Admin\OneDrive\Documents\campus-complaint-portal

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

> **Note**: If PowerShell displays an execution policy error when activating, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

### 3. Install Python Dependencies

```powershell
.\.venv\Scripts\pip install -r requirements.txt
```

---

### 4. Database Setup (MySQL)

#### Option A: Using Local MySQL Server / XAMPP

1. **Start MySQL Server**:
   - If using **XAMPP**: Start the MySQL module in the XAMPP Control Panel.
   - If using **Windows MySQL Service**:
     ```powershell
     Start-Service MySQL80  # Or net start mysql
     ```

2. **Create Database**:
   Log into MySQL and run:
   ```sql
   CREATE DATABASE IF NOT EXISTS campus_complaint_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Configure `.env`**:
   Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
   Edit `.env` with your credentials:
   ```env
   SECRET_KEY=your_secret_key_here
   DB_ENGINE=mysql
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=campus_complaint_portal
   ALLOW_SQLITE_FALLBACK=1
   ```

4. **Initialize Schema & Seed Reference Data**:
   ```powershell
   .\.venv\Scripts\python scripts/init_db.py --reset
   ```
   This creates all tables and seeds the 42 reference complaints matching the internship report figures.

#### Option B: Standalone / Zero-Configuration Mode (SQLite)

The application includes built-in dual-engine support. If MySQL is not currently running, simply set:
```env
DB_ENGINE=sqlite
```
in `.env`, then initialize:
```powershell
.\.venv\Scripts\python scripts/init_db.py --reset
```

---

### 5. Create or Reset Administrator Account

To create a new administrator or change the admin password:

```powershell
# Interactive mode
.\.venv\Scripts\python scripts/create_admin.py

# Or command-line arguments: <Name> <Email> <Password>
.\.venv\Scripts\python scripts/create_admin.py "Admin S" "admin@campus.edu" "Admin123!"
```

---

### 6. Start the Application

```powershell
.\.venv\Scripts\python app.py
```

The application will start on:
👉 **http://127.0.0.1:5000**

#### One-step Windows setup

Run `run_local.bat` from File Explorer or a Command Prompt opened in the project folder. Choose **Full setup and start the application** to create the virtual environment, install dependencies, create `.env` if needed, optionally seed the demo database, optionally create an administrator, run tests, and start Flask.

The script does not overwrite an existing `.env`. Review its database settings before running; choose `DB_ENGINE=sqlite` for a local SQLite setup or configure MySQL credentials. The database reset option requires explicit confirmation and deletes existing complaints, students, and administrators before loading the demo data. Choose not to reset to preserve existing data.

The other menu options can install dependencies, initialize the demo database, create/update an administrator, run tests, or start the application separately. The script uses the virtual-environment Python executable directly, so PowerShell activation policy changes are not needed.

---

### 7. Pre-Seeded Demonstration Accounts

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Student** | `aarthi.s@gmail.com` | `Password123!` | Matches Figures 1.2 – 1.7 (12 complaints: 5 Pending, 4 In Progress, 3 Resolved) |
| **Administrator** | `admin@campus.edu` | `Admin123!` | Matches Figures 2.1 – 2.4 (42 total complaints, full dashboard & reports) |

---

### 8. Running Automated Tests

Run the complete test suite with `pytest`:

```powershell
.\.venv\Scripts\pytest -v
```

All 15 tests covering authentication, registration, student complaints, admin workflows, filters, and reports will execute.

### 9. GitHub Actions CI

The workflow in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs the test suite on every push and pull request, and can also be started manually from the GitHub Actions tab. It uses Python 3.12 and SQLite-backed test fixtures, so it does not require production database credentials.

This workflow verifies changes; it does not deploy the app to a hosting provider. A provider-specific deploy job requires a hosting target and its deployment credentials.

---

### 10. Troubleshooting

- **MySQL Connection Refused (`2003: Can't connect to MySQL server on 'localhost'`):**
  - Verify the MySQL service is running via Windows Services (`services.msc`) or XAMPP.
  - Verify that `DB_PORT` in `.env` matches your MySQL port (typically `3306` or `3307`).
  - If you do not have MySQL installed, keep `ALLOW_SQLITE_FALLBACK=1` or set `DB_ENGINE=sqlite` to test immediately.
- **Access Denied for user 'root'@'localhost':**
  - Check your password in `.env` (`DB_PASSWORD`). In XAMPP, default password is empty (`DB_PASSWORD=`).
- **ModuleNotFoundError:**
  - Verify your virtual environment is activated and run `pip install -r requirements.txt`.

---

## 📁 Project Structure

```
campus-complaint-portal/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions test pipeline
├── app.py                     # Flask application factory, filters, routes
├── config.py                  # Environment and database configuration
├── db.py                      # Multi-engine (MySQL/SQLite) database connection layer
├── requirements.txt           # Python package dependencies
├── schema.sql                 # MySQL schema definitions
├── .env.example               # Example environment variable file
├── .env                       # Local environment configuration (git ignored)
├── .gitignore                 # Version control exclusions
├── README.md                  # System documentation and instructions
│
├── routes/
│   ├── __init__.py            # Routes package marker
│   ├── auth.py                # Student & admin registration, login, logout
│   ├── student.py             # Student dashboard, complaint submission, history, details
│   └── admin.py               # Admin dashboard, management, status updates, reports
│
├── templates/
│   ├── base.html              # Core HTML5 layout
│   ├── home.html              # Public landing page (Figure 1.1)
│   ├── student_register.html  # Split-screen registration (Figure 1.2)
│   ├── student_login.html     # Split-screen student login (Figure 1.3)
│   ├── admin_login.html       # Split-screen admin login
│   ├── student/
│   │   ├── base_student.html  # Student sidebar & header layout
│   │   ├── dashboard.html     # Student dashboard (Figure 1.4)
│   │   ├── raise_complaint.html # Raise complaint form (Figure 1.5)
│   │   ├── my_complaints.html # My complaints table (Figure 1.6)
│   │   ├── complaint_details.html # Complaint details card (Figure 1.7)
│   │   └── profile.html       # Student profile view & update
│   └── admin/
│       ├── base_admin.html    # Admin sidebar & header layout
│       ├── dashboard.html     # Admin dashboard with charts (Figure 2.1)
│       ├── manage_complaints.html # Manage complaints table (Figure 2.2)
│       ├── view_complaint.html # Admin view complaint
│       ├── update_complaint.html # Update complaint status & remarks (Figure 2.3)
│       ├── reports.html       # Category-wise reports & summary (Figure 2.4)
│       └── profile.html       # Admin profile view & update
│
├── static/
│   ├── css/
│   │   └── style.css          # Pixel-matched stylesheet
│   ├── js/
│   │   ├── main.js            # UI interactions and password toggle
│   │   ├── charts.js          # Chart management utilities
│   │   └── chart.min.js       # Local Chart.js library
│   └── images/
│       ├── campus-hero.jpg    # Hero banner background
│       ├── registration-illustration.png # Registration panel graphic
│       ├── login-illustration.png        # Login panel graphic
│       └── logo.png           # Shield emblem logo
│
├── scripts/
│   ├── init_db.py             # Schema initialization & reference seeding
│   └── create_admin.py        # Safe CLI administrator creation tool
│
└── tests/
    ├── __init__.py            # Test package marker
    ├── conftest.py            # Pytest fixtures and test client configuration
    ├── test_auth.py           # Authentication and registration test suite
    ├── test_complaints.py     # Complaint submission, codes, and isolation tests
    └── test_admin.py          # Admin dashboard, management, and report tests
```
