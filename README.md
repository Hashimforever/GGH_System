# GGH Community Association Management System

A comprehensive Django-based system for managing community association members, committee operations, financial contributions, loans, and system documents.

## System Architecture

The project is divided into several specialized Django applications:
- **accounts**: User authentication, groups, and role-based access control.
- **core**: System-wide settings, global configurations, and homepage management.
- **members**: Member registration, profiling, and demographic tracking.
- **committee**: Committee structure, leadership tracking, and roles.
- **contributions**: Monthly contributions, bulk recording matrix, and expected payment generation.
- **finance**: Master ledger (FinancialTransaction), tracking income, withdrawals, and balances.
- **loans**: Loan application, approval workflows, and repayments.
- **documents**: Central repository for uploading and managing system documents.
- **reports**: Financial and membership reports.
- **audit**: System-wide audit logging for all user actions.

## Prerequisites

- Python 3.10+
- `pip` package manager

## Installation & Setup

1. **Clone or Extract the Project**
   Navigate to the project root directory (`c:\xampp\htdocs\gghsystem`).

2. **Create a Virtual Environment** (if not already created)
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser** (if none exists)
   ```bash
   python manage.py createsuperuser
   ```

## Running the Server

You can run the server using the provided batch script on Windows:
```bash
run.bat
```

Alternatively, you can manually run the Django server using the virtual environment python:
```bash
venv\Scripts\python.exe manage.py runserver
```

The system will be accessible at `http://127.0.0.1:8000/`.

## Important Notes

- **Database**: The project currently uses the default SQLite3 database (`db.sqlite3`).
- **Templates & UI**: The system uses AdminLTE 3 / Bootstrap 4 for the primary dashboard user interface, and Jazzmin for the Django Admin interface.
- **DataTables**: Table lists use jQuery DataTables with custom column-specific dropdown filtering enabled.
