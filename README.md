# 🏥 Hospital Management System

A web-based Hospital Management System built with **Python, Flask, SQLite, HTML, CSS, Bootstrap, and JavaScript**.

This is a portfolio project focused on demonstrating practical Flask backend development, relational database design, CRUD operations, validation, and a clean admin-style interface.

## ✨ Current Features

### 👤 Patient Management
- Add patients
- View patient records
- Search patients by name
- Edit patient information
- Delete patients only when they have no appointments
- Server-side validation
- Browser-side validation
- Form values preserved after validation errors

### 👨‍⚕️ Doctor Management
- Add doctors
- View doctor records
- Search by name or specialization
- Edit doctor information
- Delete doctors only when they have no appointments
- Phone and email validation
- Form values preserved after validation errors

### 📅 Appointment Management
- Schedule appointments
- Select patients and doctors from the database
- Date and time validation
- Appointment status tracking
- Search by patient or doctor
- Filter by status
- Prevent double-booking a doctor at the same date and time
- Mark scheduled appointments as completed
- Cancel scheduled appointments
- Protected appointment state transitions

### 📊 Dashboard
- Total patients
- Total doctors
- Total appointments
- Scheduled appointments
- Recent appointments
- Quick actions
- Responsive layout

### 🛡️ Database & Application Quality
- SQLite foreign-key enforcement
- Parameterized SQL queries
- Database path resolved relative to the project
- POST requests for destructive/state-changing actions
- Consistent Flask `url_for()` routing
- Empty states and flash messages
- Responsive sidebar/navigation
- Clean project structure

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap 5
- **Icons:** Bootstrap Icons
- **Template Engine:** Jinja2
- **JavaScript:** Vanilla JavaScript
- **Version Control:** Git & GitHub

## 📂 Project Structure

```text
hospital-management-system/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── database/
│   ├── db.py
│   ├── init_db.py
│   └── hospital.db
│
├── templates/
│   ├── Components/
│   │   ├── navbar.html
│   │   └── sidebar.html
│   ├── add_appointment.html
│   ├── add_doctor.html
│   ├── add_patient.html
│   ├── appointments.html
│   ├── base.html
│   ├── dashboard.html
│   ├── doctors.html
│   ├── edit_doctor.html
│   ├── edit_patient.html
│   ├── home.html
│   └── patients.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/AmaanCoder786/hospital-management-system.git
cd hospital-management-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate it

**Windows PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize the database

Run this from the project root:

```bash
python database/init_db.py
```

If the database already exists, the initialization script uses `CREATE TABLE IF NOT EXISTS` and does not erase existing records.

### 6. Start the application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## 🧪 Phase 2 Completion Checklist

- [x] Patient CRUD
- [x] Patient search
- [x] Patient validation
- [x] Doctor CRUD
- [x] Doctor search
- [x] Doctor validation
- [x] Appointment scheduling
- [x] Appointment validation
- [x] Appointment search/filter
- [x] Appointment status workflow
- [x] Dashboard statistics
- [x] Recent appointments
- [x] Relational database protection
- [x] POST-based delete/state-changing actions
- [x] Responsive UI
- [x] Empty states
- [x] Flash messages
- [x] README and dependency cleanup

## 🎯 Learning Objectives

This project demonstrates:

- Flask routing and request handling
- CRUD operations
- SQLite relational database design
- SQL joins and filtering
- Server-side validation
- Jinja2 templating
- Bootstrap-based UI development
- Git/GitHub workflow
- Basic application integrity and state management

## 🔮 Possible Future Modules

These are intentionally outside the completed Phase 2 scope:

- Authentication and role-based access
- Medical records/history
- Prescriptions
- Billing
- Reports/export
- Deployment

## 👨‍💻 Author

**Amaan Khan**

MCA Student | Python Developer

GitHub: https://github.com/AmaanCoder786
