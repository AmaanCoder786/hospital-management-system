from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "database" / "hospital.db"

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    phone TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Scheduled', 'Completed', 'Cancelled')),
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_patients_name
ON patients(name)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_doctors_name
ON doctors(name)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_appointments_date
ON appointments(appointment_date, appointment_time)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_slot
ON appointments(doctor_id, appointment_date, appointment_time, status)
""")

connection.commit()
connection.close()

print(f"Database initialized: {DATABASE_PATH}")
