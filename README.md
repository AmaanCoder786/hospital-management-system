# 🏥 Hospital Management System

A web-based Hospital Management System built using **Python, Flask, SQLite, HTML, CSS, and JavaScript**.

This project helps manage patients, doctors, and appointments through a clean and user-friendly interface. It is being developed as part of my MCA portfolio to demonstrate full-stack web development skills using Flask.

---

## 📌 Features

### 👨‍⚕️ Doctor Management
- Add new doctors
- View all doctors
- Edit doctor details
- Delete doctors

### 🧑 Patient Management
- Add new patients
- View all patients
- Edit patient details
- Delete patients

### 📅 Appointment Management
- Schedule appointments
- View appointment list
- Link appointments with doctors and patients

### 📊 Dashboard
- Simple navigation dashboard
- Organized interface for managing hospital records

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| Flask | Web Framework |
| SQLite | Database |
| HTML5 | Structure |
| CSS3 | Styling |
| JavaScript | Client-side Interactions |
| Jinja2 | Template Engine |

---

## 📂 Project Structure

```
hospital-management-system/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── database/
│   ├── db.py
│   └── init_db.py
│
├── static/
│   ├── css/
│   └── js/
│
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── patients.html
    ├── doctors.html
    ├── appointments.html
    ├── add_patient.html
    ├── add_doctor.html
    ├── add_appointment.html
    ├── edit_patient.html
    └── edit_doctor.html
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/AmaanCoder786/hospital-management-system.git
```

### 2. Navigate to the project

```bash
cd hospital-management-system
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Initialize the database

```bash
python database/init_db.py
```

### 7. Run the application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 📸 Screenshots

### Dashboard

*(Add screenshot here)*

```
images/dashboard.png
```

### Patients

*(Add screenshot here)*

### Doctors

*(Add screenshot here)*

### Appointments

*(Add screenshot here)*

---

## 📅 Current Progress

### ✅ Phase 1 Completed

- Patient CRUD
- Doctor CRUD
- Appointment Management
- SQLite Database
- Flask Routing
- Jinja Templates
- Responsive UI

---

## 🚧 Upcoming Features (Phase 2)

- Search Patients
- Search Doctors
- Dashboard Statistics
- Authentication/Login
- Appointment Status
- Medical History
- Prescription Module
- CSV/PDF Export
- Responsive Improvements

---

## 🎯 Learning Objectives

This project demonstrates:

- Flask Web Development
- CRUD Operations
- Database Design
- SQLite Integration
- Jinja Templates
- Python Programming
- Git & GitHub Workflow
- Frontend Integration

---

## 👨‍💻 Author

**Amaan Khan**

MCA Student | Python Developer | Aspiring Backend & Cloud Engineer

GitHub:
https://github.com/AmaanCoder786

---

## 📄 License

This project is licensed under the MIT License.