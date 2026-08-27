"""Reset the HMS database and populate it with realistic demo data.

WARNING: Running this script permanently deletes all existing patients,
doctors, and appointments from database/hospital.db.
"""

from datetime import date, datetime, timedelta
from pathlib import Path
import random
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hospital.db"

random.seed(20260826)

FIRST_NAMES = [
    "Aarav", "Aditi", "Aditya", "Akash", "Aman", "Ananya", "Anika", "Anil",
    "Arjun", "Aryan", "Ashish", "Avni", "Ayush", "Bhavna", "Chetan", "Deepak",
    "Diya", "Divya", "Farhan", "Gaurav", "Ishaan", "Isha", "Jatin", "Karan",
    "Kavya", "Kiran", "Manish", "Meera", "Mohit", "Naina", "Neha", "Nikhil",
    "Nisha", "Pankaj", "Pooja", "Pranav", "Priya", "Rahul", "Riya", "Rohan",
    "Rohit", "Sahil", "Sakshi", "Sameer", "Sana", "Shivam", "Shruti", "Simran",
    "Sonia", "Tanya"
]

LAST_NAMES = [
    "Agarwal", "Ansari", "Bansal", "Bhatia", "Chauhan", "Das", "Gupta", "Iyer",
    "Jain", "Kapoor", "Khan", "Malhotra", "Mehta", "Mishra", "Nair", "Patel",
    "Rao", "Saxena", "Sharma", "Singh", "Sinha", "Srivastava", "Verma", "Yadav"
]

DOCTORS = [
    ("Dr. Rajiv Mehra", "Cardiology"),
    ("Dr. Priya Sharma", "Dermatology"),
    ("Dr. Arvind Kapoor", "Orthopedics"),
    ("Dr. Neha Gupta", "Pediatrics"),
    ("Dr. Sameer Khan", "General Medicine"),
    ("Dr. Anjali Rao", "Gynecology"),
    ("Dr. Vikram Singh", "Neurology"),
    ("Dr. Pooja Mehta", "Ophthalmology"),
    ("Dr. Amit Verma", "ENT"),
    ("Dr. Ritu Bansal", "Psychiatry"),
    ("Dr. Kunal Jain", "Urology"),
    ("Dr. Sneha Iyer", "Pulmonology"),
    ("Dr. Rohit Nair", "Gastroenterology"),
    ("Dr. Shalini Das", "Oncology"),
    ("Dr. Manish Patel", "General Surgery"),
    ("Dr. Kavita Sinha", "Endocrinology"),
    ("Dr. Nitin Chawla", "Nephrology"),
    ("Dr. Ayesha Siddiqui", "Radiology"),
    ("Dr. Deepak Yadav", "Anesthesiology"),
    ("Dr. Meera Malhotra", "Rheumatology"),
    ("Dr. Farhan Ali", "Internal Medicine"),
    ("Dr. Swati Saxena", "Pathology"),
    ("Dr. Vivek Tiwari", "Emergency Medicine"),
    ("Dr. Nandini Joshi", "Nutrition"),
    ("Dr. Harsh Vardhan", "Dental Surgery"),
    ("Dr. Sonal Arora", "ENT"),
    ("Dr. Rajesh Sethi", "Cardiology"),
    ("Dr. Komal Khanna", "Pediatrics"),
    ("Dr. Imran Sheikh", "Orthopedics"),
    ("Dr. Rakesh Tripathi", "General Medicine"),
]


def make_patients():
    patients = []
    used_names = set()
    number = 0

    while len(patients) < 100:
        first = FIRST_NAMES[number % len(FIRST_NAMES)]
        last = LAST_NAMES[(number * 7) % len(LAST_NAMES)]
        name = f"{first} {last}"
        number += 1
        if name in used_names:
            continue
        used_names.add(name)

        age = random.randint(5, 82)
        gender = random.choice(["Male", "Female", "Other"])
        phone = f"{random.choice('6789')}{random.randint(100000000, 999999999)}"
        patients.append((name, age, gender, phone))

    return patients


def make_doctors():
    doctors = []
    for index, (name, specialization) in enumerate(DOCTORS, start=1):
        phone = f"{random.choice('6789')}{index:09d}"
        email_name = name.lower().replace("dr. ", "").replace(" ", ".")
        email = f"{email_name}@citycarehospital.example"
        doctors.append((name, specialization, phone, email))
    return doctors


def make_appointments(patient_count, doctor_count, count=180):
    appointments = []
    slots = [(hour, minute) for hour in range(9, 17) for minute in (0, 30)]
    used_slots = set()
    today = date(2026, 8, 26)

    # Generate appointments across roughly four months, with past and future data.
    start = today - timedelta(days=90)
    end = today + timedelta(days=45)

    attempts = 0
    while len(appointments) < count and attempts < count * 50:
        attempts += 1
        appointment_date = start + timedelta(days=random.randint(0, (end - start).days))
        doctor_id = random.randint(1, doctor_count)
        patient_id = random.randint(1, patient_count)
        hour, minute = random.choice(slots)
        appointment_time = f"{hour:02d}:{minute:02d}"
        key = (doctor_id, appointment_date.isoformat(), appointment_time)

        if key in used_slots:
            continue
        used_slots.add(key)

        if appointment_date < today:
            status = "Cancelled" if random.random() < 0.12 else "Completed"
        elif appointment_date == today:
            status = random.choice(["Completed", "Scheduled", "Scheduled"])
        else:
            status = "Scheduled"

        appointments.append((
            patient_id,
            doctor_id,
            appointment_date.isoformat(),
            appointment_time,
            status,
        ))

    appointments.sort(key=lambda row: (row[2], row[3]))
    return appointments


def seed_database():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    # Clear all existing application data.
    cursor.execute("DELETE FROM appointments")
    cursor.execute("DELETE FROM doctors")
    cursor.execute("DELETE FROM patients")

    # Reset AUTOINCREMENT counters so the fresh demo data starts at ID 1.
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'appointments'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'doctors'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'patients'")

    patients = make_patients()
    doctors = make_doctors()
    appointments = make_appointments(100, len(doctors), 180)

    cursor.executemany(
        """
        INSERT INTO patients (name, age, gender, phone)
        VALUES (?, ?, ?, ?)
        """,
        patients,
    )

    cursor.executemany(
        """
        INSERT INTO doctors (name, specialization, phone, email)
        VALUES (?, ?, ?, ?)
        """,
        doctors,
    )

    cursor.executemany(
        """
        INSERT INTO appointments
            (patient_id, doctor_id, appointment_date, appointment_time, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        appointments,
    )

    connection.commit()

    counts = {
        "patients": cursor.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
        "doctors": cursor.execute("SELECT COUNT(*) FROM doctors").fetchone()[0],
        "appointments": cursor.execute("SELECT COUNT(*) FROM appointments").fetchone()[0],
        "scheduled": cursor.execute(
            "SELECT COUNT(*) FROM appointments WHERE status = 'Scheduled'"
        ).fetchone()[0],
        "completed": cursor.execute(
            "SELECT COUNT(*) FROM appointments WHERE status = 'Completed'"
        ).fetchone()[0],
        "cancelled": cursor.execute(
            "SELECT COUNT(*) FROM appointments WHERE status = 'Cancelled'"
        ).fetchone()[0],
    }

    connection.close()
    return counts


if __name__ == "__main__":
    counts = seed_database()
    print("HMS demo database reset successfully.")
    print(f"Patients:      {counts['patients']}")
    print(f"Doctors:       {counts['doctors']}")
    print(f"Appointments:  {counts['appointments']}")
    print(f"  Scheduled:   {counts['scheduled']}")
    print(f"  Completed:   {counts['completed']}")
    print(f"  Cancelled:   {counts['cancelled']}")
