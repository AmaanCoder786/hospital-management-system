# Import required flask modules
from flask import Flask, render_template, request, redirect

# Import sqlite3 for database helper
import sqlite3
from database.db import get_db_connection

# Create Flask application
app = Flask(__name__)

# ----------------------
# Home Page
# ----------------------
@app.route("/")
def home():
    return render_template("home.html")

# Fetch dashboard statistics from the database
@app.route("/dashboard")
def dashboard():

    connection = get_db_connection()
    cursor = connection.cursor()

    # Count total Patients
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    # Count total Doctors
    cursor.execute("SELECT COUNT(*) FROM doctors")
    total_doctors = cursor.fetchone()[0]

    # Count total Appointments
    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments
    )

# ----------------------
# Patients Module
# ----------------------

# Display all patients with search by name
@app.route("/patients")
def patients():

    search = request.args.get("search", "")

    connection = get_db_connection()
    cursor = connection.cursor()

    if search:
        cursor.execute(
            "SELECT * FROM patients WHERE name LIKE ?",
            ('%' + search + '%',)
        )
    else:
        cursor.execute("SELECT * FROM patients")

    patients = cursor.fetchall()

    connection.close()

    return render_template(
        "patients.html",
        patients=patients,
        search=search
    )

# Add a new patient to the database
@app.route("/add-patient", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
                       INSERT INTO patients 
                       (name, age, gender, phone) 
                       VALUES (?, ?, ?, ?)""",
                       (name, age, gender, phone))
        connection.commit()
        connection.close()

        return redirect("/patients")
    return render_template("add_patient.html")

# Edit an existing patient's details in the database
@app.route("/edit-patient/<int:id>", methods=["GET", "POST"])
def edit_patient(id):

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE patients
            SET name = ?, age = ?, gender = ?, phone = ?
            WHERE id = ?
            """,
            (name, age, gender, phone, id)
        )

        connection.commit()
        connection.close()

        return redirect("/patients")

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id = ?",
        (id,)
    )

    patient = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_patient.html",
        patient=patient
    )

# Delete a patient from the database
@app.route("/delete-patient/<int:id>")
def delete_patient(id):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM patients WHERE id = ?",
        (id,)
    )

    connection.commit()

    connection.close()

    return redirect("/patients") 

# ----------------------
# Doctors Module
# ----------------------

# Display all doctors with search by name
@app.route("/doctors")
def doctors():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    connection.close()
    return render_template("doctors.html", doctors=doctors)

# Add a new doctor to the database
@app.route("/add_doctor", methods=["GET", "POST"])
def add_doctor():
    if request.method == "POST":

        name = request.form["name"]
        specialization = request.form["specialization"]
        phone = request.form["phone"]
        email = request.form["email"]

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
                       INSERT INTO doctors 
                       (name, specialization, phone, email) 
                       VALUES (?, ?, ?, ?)""",
                       (name, specialization, phone, email))
        connection.commit()
        connection.close()

        return redirect("/doctors")
    return render_template("add_doctor.html")

# Edit an existing doctor's details in the database
@app.route("/edit-doctor/<int:id>", methods=["GET", "POST"])
def edit_doctor(id):

    if request.method == "POST":

        name = request.form["name"]
        specialization = request.form["specialization"]
        phone = request.form["phone"]
        email = request.form["email"]

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE doctors
            SET name = ?, specialization = ?, phone = ?, email = ?
            WHERE id = ?
            """,
            (name, specialization, phone, email, id)
        )

        connection.commit()
        connection.close()

        return redirect("/doctors")

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM doctors WHERE id = ?",
        (id,)
    )

    doctor = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_doctor.html",
        doctor=doctor
    )

# Delete a doctor from the database
@app.route("/delete-doctor/<int:id>")
def delete_doctor(id):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM doctors WHERE id = ?",
        (id,)
    )

    connection.commit()

    connection.close()

    return redirect("/doctors")

# ----------------------
# Appointments Module
# ----------------------

# Display all appointments with patient and doctor names
@app.route("/appointments")
def appointments():

    # connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Retrieve appointment details.
    # SQL JOIN is used to display patient and doctor names instead of their database IDs.
    cursor.execute("""
        SELECT
            appointments.id,
            patients.name,
            doctors.name,
            appointments.appointment_date,
            appointments.appointment_time,
            appointments.status
        FROM appointments
        JOIN patients
            ON appointments.patient_id = patients.id
        JOIN doctors
            ON appointments.doctor_id = doctors.id
    """)

    appointments = cursor.fetchall()

    # close the database connection 
    connection.close()

    # Send appointment data to the template
    return render_template(
        "appointments.html",
        appointments=appointments
    )

# Add a new appointment to the database
@app.route("/add-appointment", methods=["GET", "POST"])
def add_appointment():

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        doctor_id = request.form["doctor_id"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        status = request.form["status"]

        cursor.execute("""
            INSERT INTO appointments
            (patient_id, doctor_id, appointment_date, appointment_time, status)
            VALUES (?, ?, ?, ?, ?)
        """,
        (
            patient_id,
            doctor_id,
            appointment_date,
            appointment_time,
            status
        ))

        connection.commit()
        connection.close()

        return redirect("/appointments")

    # Get all patients
    cursor.execute("SELECT id, name FROM patients")
    patients = cursor.fetchall()

    # Get all doctors
    cursor.execute("SELECT id, name FROM doctors")
    doctors = cursor.fetchall()

    connection.close()

    return render_template(
        "add_appointment.html",
        patients=patients,
        doctors=doctors
    )

# Start the Flask development server
if __name__ == "__main__":
    app.run(debug=True)