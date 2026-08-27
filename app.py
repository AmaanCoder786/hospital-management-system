# Import required flask modules
from flask import Flask, render_template, request, redirect, flash

# Import sqlite3 for database helper
import sqlite3 
from database.db import get_db_connection

# Create Flask application
app = Flask(__name__)
app.secret_key = "hospital-management-secret-key"  # Required for flashing

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

    # Count Scheduled Appointments
    cursor.execute("""
                   SELECT COUNT(*) FROM appointments 
                   WHERE status = 'Scheduled'
                   """)
    scheduled_appointments = cursor.fetchone()[0]

    # Fetch the 5 most recent appointments
    cursor.execute("""
        SELECT
            appointments.appointment_date,
            appointments.appointment_time,
            appointments.status,
            patients.name AS patient_name,
            doctors.name AS doctor_name
        FROM appointments
        JOIN patients ON appointments.patient_id = patients.id
        JOIN doctors ON appointments.doctor_id = doctors.id
        ORDER BY appointments.id DESC LIMIT 5
    """)
    
    recent_appointments = cursor.fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        page_title="Dashboard",
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        scheduled_appointments=scheduled_appointments,
        recent_appointments=recent_appointments
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
            "SELECT * FROM patients WHERE name LIKE ? ORDER BY id ASC",
            ('%' + search + '%',)
        )
    else:
        cursor.execute("SELECT * FROM patients ORDER BY id ASC")

    patients = cursor.fetchall()

    connection.close()

    return render_template(
        "patients.html",
        page_title="Patients",
        patients=patients,
        search=search
    )

# Add a new patient to the database
@app.route("/add-patient", methods=["GET", "POST"])
def add_patient():

    if request.method == "POST":

        name = request.form["name"].strip()
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"].strip()

        # Server-side age validation
        try:
            age = int(age)

            if age < 0 or age > 120:
                flash("Age must be between 0 and 120.", "danger")
                return redirect("/add-patient")

        except ValueError:
            flash("Please enter a valid age.", "danger")
            return redirect("/add-patient")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO patients
            (name, age, gender, phone)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            age,
            gender,
            phone
        ))

        connection.commit()
        connection.close()

        return redirect("/patients")

    return render_template(
        "add_patient.html",
        page_title="Add Patient"
    )

# Edit an existing patient's details in the database
@app.route("/edit-patient/<int:id>", methods=["GET", "POST"])
def edit_patient(id):

    if request.method == "POST":

        name = request.form["name"].strip()
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"].strip()

        # Server-side age validation
        try:
            age = int(age)

            if age < 0 or age > 120:
                flash("Age must be between 0 and 120.", "danger")
                return redirect(f"/edit-patient/{id}")

        except ValueError:
            flash("Please enter a valid age.", "danger")
            return redirect(f"/edit-patient/{id}")

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
        page_title="Edit Patient",
        patient=patient
    )

# Delete a patient from the database
@app.route("/delete-patient/<int:id>", methods=["POST"])
def delete_patient(id):

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether the patient has any appointments
    cursor.execute(
        "SELECT COUNT(*) FROM appointments WHERE patient_id = ?",
        (id,)
    )

    appointment_count = cursor.fetchone()[0]

    if appointment_count > 0:

        connection.close()

        flash(
            "This patient cannot be deleted because they have existing appointments.",
            "warning"
        )

        return redirect("/patients")

    # Delete the patient if no appointments exist
    cursor.execute(
        "DELETE FROM patients WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    flash(
        "Patient deleted successfully.",
        "success"
    )

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
    return render_template("doctors.html", doctors=doctors, page_title="Doctors")

# Add a new doctor to the database
@app.route("/add-doctor", methods=["GET", "POST"])
def add_doctor():

    if request.method == "POST":

        name = request.form["name"].strip()
        specialization = request.form["specialization"].strip()
        phone = request.form["phone"].strip()
        email = request.form["email"].strip()

        # Validate name
        if not name:
            flash("Doctor name is required.", "danger")
            return render_template(
                "add_doctor.html",
                page_title="Add Doctor",
                form=request.form
            )

        # Validate specialization
        if not specialization:
            flash("Specialization is required.", "danger")
            return render_template(
                "add_doctor.html",
                page_title="Add Doctor",
                form=request.form
            )

        # Validate phone
        if not phone.isdigit() or len(phone) != 10:
            flash("Phone number must contain exactly 10 digits.", "danger")
            return render_template(
                "add_doctor.html",
                page_title="Add Doctor",
                form=request.form
            )

        # Validate email
        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "danger")
            return render_template(
                "add_doctor.html",
                page_title="Add Doctor",
                form=request.form
            )

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO doctors
            (name, specialization, phone, email)
            VALUES (?, ?, ?, ?)
        """, (name, specialization, phone, email))

        connection.commit()
        connection.close()

        flash("Doctor added successfully.", "success")

        return redirect("/doctors")

    return render_template(
        "add_doctor.html",
        page_title="Add Doctor"
    )

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
        page_title="Edit Doctor",
        doctor=doctor
    )

# Delete a doctor from the database

@app.route("/delete-doctor/<int:id>", methods=["POST"])
def delete_doctor(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    # Check whether the doctor has any appointments
    cursor.execute(
        "SELECT id FROM appointments WHERE doctor_id = ? LIMIT 1",
        (id,)
    )
    appointment = cursor.fetchone()
    if appointment:
        connection.close()
        flash(
            "This doctor cannot be deleted because they have appointments.",
            "warning"
        )
        return redirect("/doctors")
    # Delete doctor if no appointments exist
    cursor.execute(
        "DELETE FROM doctors WHERE id = ?",
        (id,)
    )
    connection.commit()
    connection.close()
    flash("Doctor deleted successfully.", "success")
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
        page_title="Appointments",
        appointments=appointments
    )

# Mark a scheduled appointment as completed
@app.route("/complete-appointment/<int:appointment_id>", methods=["POST"])
def complete_appointment(appointment_id):

    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Update the appointment status
    cursor.execute("""
        UPDATE appointments
        SET status = 'Completed'
        WHERE id = ?
    """, (appointment_id,))

    # Save the change
    connection.commit()

    # Close the database connection
    connection.close()

    # Return to the appointments page
    return redirect("/appointments")

# Mark a scheduled appointment as cancelled
@app.route("/cancel-appointment/<int:appointment_id>", methods=["POST"])
def cancel_appointment(appointment_id):

    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Update the appointment status
    cursor.execute("""
        UPDATE appointments
        SET status = 'Cancelled'
        WHERE id = ?
    """, (appointment_id,))

    # Save the change
    connection.commit()

    # Close the database connection
    connection.close()

    # Return to the appointments page
    return redirect("/appointments")

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
    cursor.execute("""
                   SELECT id, name, age, gender, phone
                   FROM patients
                   ORDER BY id ASC
                   """)
    patients = cursor.fetchall()

    # Get all doctors
    cursor.execute("""
                   SELECT id, name, specialization 
                   FROM doctors
                   ORDER BY id ASC
                   """)
    doctors = cursor.fetchall()

    connection.close()

    return render_template(
        "add_appointment.html",
        patients=patients,
        doctors=doctors,
        page_title="Add Appointment"
    )

# Start the Flask development server
if __name__ == "__main__":
    app.run(debug=True)