from flask import Flask, abort, flash, redirect, render_template, request, url_for
import re
from database.db import get_db_connection
from datetime import datetime


app = Flask(__name__)
app.secret_key = "hospital-management-secret-key"


# ----------------------
# Validation helpers
# ----------------------

ALLOWED_GENDERS = {"Male", "Female", "Other"}
ALLOWED_APPOINTMENT_STATUSES = {"Scheduled", "Completed", "Cancelled"}


def validate_phone(phone):
    return phone.isdigit() and len(phone) == 10


def validate_email(email):
    if not email:
        return False
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None


def parse_patient_form(form):
    return {
        "name": form.get("name", "").strip(),
        "age": form.get("age", "").strip(),
        "gender": form.get("gender", "").strip(),
        "phone": form.get("phone", "").strip(),
    }


def validate_patient_form(data):
    if not data["name"]:
        return "Patient name is required."

    if not data["age"]:
        return "Age is required."

    try:
        age = int(data["age"])
    except ValueError:
        return "Please enter a valid age."

    if age < 0 or age > 120:
        return "Age must be between 0 and 120."

    if data["gender"] not in ALLOWED_GENDERS:
        return "Please select a valid gender."

    if not validate_phone(data["phone"]):
        return "Phone number must contain exactly 10 digits."

    return None


def parse_doctor_form(form):
    return {
        "name": form.get("name", "").strip(),
        "specialization": form.get("specialization", "").strip(),
        "phone": form.get("phone", "").strip(),
        "email": form.get("email", "").strip(),
    }


def validate_doctor_form(data):
    if not data["name"]:
        return "Doctor name is required."

    if not data["specialization"]:
        return "Specialization is required."

    if not validate_phone(data["phone"]):
        return "Phone number must contain exactly 10 digits."

    if not validate_email(data["email"]):
        return "Please enter a valid email address."

    return None


# ----------------------
# Home / Dashboard
# ----------------------


@app.route("/")
def home():
    return render_template("home.html", page_title="Welcome")


@app.route("/dashboard")
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM doctors")
    total_doctors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Scheduled'")
    scheduled_appointments = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT
            appointments.appointment_date,
            appointments.appointment_time,
            appointments.status,
            patients.name AS patient_name,
            doctors.name AS doctor_name
        FROM appointments
        JOIN patients ON appointments.patient_id = patients.id
        JOIN doctors ON appointments.doctor_id = doctors.id
        ORDER BY appointments.appointment_date DESC,
                 appointments.appointment_time DESC,
                 appointments.id DESC
        LIMIT 5
        """
    )
    recent_appointments = cursor.fetchall()
    connection.close()

    return render_template(
        "dashboard.html",
        page_title="Dashboard",
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        scheduled_appointments=scheduled_appointments,
        recent_appointments=recent_appointments,
    )


# ----------------------
# Patients
# ----------------------


@app.route("/patients")
def patients():
    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor()

    if search:
        cursor.execute(
            """
            SELECT id, name, age, gender, phone
            FROM patients
            WHERE name LIKE ?
            ORDER BY id ASC
            """,
            (f"%{search}%",),
        )
    else:
        cursor.execute(
            """
            SELECT id, name, age, gender, phone
            FROM patients
            ORDER BY id ASC
            """
        )

    patients_list = cursor.fetchall()
    connection.close()

    return render_template(
        "patients.html",
        page_title="Patients",
        patients=patients_list,
        search=search,
    )


@app.route("/add-patient", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        form = parse_patient_form(request.form)
        error = validate_patient_form(form)

        if error:
            flash(error, "danger")
            return render_template(
                "add_patient.html",
                page_title="Add Patient",
                form=form,
            )

        connection = get_db_connection()
        connection.execute(
            """
            INSERT INTO patients (name, age, gender, phone)
            VALUES (?, ?, ?, ?)
            """,
            (form["name"], int(form["age"]), form["gender"], form["phone"]),
        )
        connection.commit()
        connection.close()

        flash("Patient added successfully.", "success")
        return redirect(url_for("patients"))

    return render_template("add_patient.html", page_title="Add Patient", form={})


@app.route("/edit-patient/<int:id>", methods=["GET", "POST"])
def edit_patient(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM patients WHERE id = ?", (id,))
    patient = cursor.fetchone()

    if patient is None:
        connection.close()
        abort(404)

    if request.method == "POST":
        form = parse_patient_form(request.form)
        error = validate_patient_form(form)

        if error:
            connection.close()
            flash(error, "danger")
            return render_template(
                "edit_patient.html",
                page_title="Edit Patient",
                patient=patient,
                form=form,
            )

        cursor.execute(
            """
            UPDATE patients
            SET name = ?, age = ?, gender = ?, phone = ?
            WHERE id = ?
            """,
            (
                form["name"],
                int(form["age"]),
                form["gender"],
                form["phone"],
                id,
            ),
        )
        connection.commit()
        connection.close()

        flash("Patient updated successfully.", "success")
        return redirect(url_for("patients"))

    connection.close()
    return render_template(
        "edit_patient.html",
        page_title="Edit Patient",
        patient=patient,
        form={
            "name": patient["name"],
            "age": patient["age"],
            "gender": patient["gender"],
            "phone": patient["phone"],
        },
    )


@app.route("/delete-patient/<int:id>", methods=["POST"])
def delete_patient(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM patients WHERE id = ?", (id,))
    if cursor.fetchone() is None:
        connection.close()
        flash("Patient not found.", "danger")
        return redirect(url_for("patients"))

    cursor.execute(
        "SELECT 1 FROM appointments WHERE patient_id = ? LIMIT 1",
        (id,),
    )

    if cursor.fetchone():
        connection.close()
        flash(
            "This patient cannot be deleted because they have appointments.",
            "warning",
        )
        return redirect(url_for("patients"))

    cursor.execute("DELETE FROM patients WHERE id = ?", (id,))
    connection.commit()
    connection.close()

    flash("Patient deleted successfully.", "success")
    return redirect(url_for("patients"))


# ----------------------
# Doctors
# ----------------------


@app.route("/doctors")
def doctors():
    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor()

    if search:
        cursor.execute(
            """
            SELECT id, name, specialization, phone, email
            FROM doctors
            WHERE name LIKE ? OR specialization LIKE ?
            ORDER BY id ASC
            """,
            (f"%{search}%", f"%{search}%"),
        )
    else:
        cursor.execute(
            """
            SELECT id, name, specialization, phone, email
            FROM doctors
            ORDER BY id ASC
            """
        )

    doctors_list = cursor.fetchall()
    connection.close()

    return render_template(
        "doctors.html",
        doctors=doctors_list,
        search=search,
        page_title="Doctors",
    )


@app.route("/add-doctor", methods=["GET", "POST"])
def add_doctor():
    if request.method == "POST":
        form = parse_doctor_form(request.form)
        error = validate_doctor_form(form)

        if error:
            flash(error, "danger")
            return render_template(
                "add_doctor.html",
                page_title="Add Doctor",
                form=form,
            )

        connection = get_db_connection()
        connection.execute(
            """
            INSERT INTO doctors (name, specialization, phone, email)
            VALUES (?, ?, ?, ?)
            """,
            (
                form["name"],
                form["specialization"],
                form["phone"],
                form["email"],
            ),
        )
        connection.commit()
        connection.close()

        flash("Doctor added successfully.", "success")
        return redirect(url_for("doctors"))

    return render_template("add_doctor.html", page_title="Add Doctor", form={})


@app.route("/edit-doctor/<int:id>", methods=["GET", "POST"])
def edit_doctor(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM doctors WHERE id = ?", (id,))
    doctor = cursor.fetchone()

    if doctor is None:
        connection.close()
        abort(404)

    if request.method == "POST":
        form = parse_doctor_form(request.form)
        error = validate_doctor_form(form)

        if error:
            connection.close()
            flash(error, "danger")
            return render_template(
                "edit_doctor.html",
                page_title="Edit Doctor",
                doctor=doctor,
                form=form,
            )

        cursor.execute(
            """
            UPDATE doctors
            SET name = ?, specialization = ?, phone = ?, email = ?
            WHERE id = ?
            """,
            (
                form["name"],
                form["specialization"],
                form["phone"],
                form["email"],
                id,
            ),
        )
        connection.commit()
        connection.close()

        flash("Doctor updated successfully.", "success")
        return redirect(url_for("doctors"))

    connection.close()
    return render_template(
        "edit_doctor.html",
        page_title="Edit Doctor",
        doctor=doctor,
        form={
            "name": doctor["name"],
            "specialization": doctor["specialization"],
            "phone": doctor["phone"],
            "email": doctor["email"],
        },
    )


@app.route("/delete-doctor/<int:id>", methods=["POST"])
def delete_doctor(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM doctors WHERE id = ?", (id,))
    if cursor.fetchone() is None:
        connection.close()
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctors"))

    cursor.execute(
        "SELECT 1 FROM appointments WHERE doctor_id = ? LIMIT 1",
        (id,),
    )

    if cursor.fetchone():
        connection.close()
        flash(
            "This doctor cannot be deleted because they have appointments.",
            "warning",
        )
        return redirect(url_for("doctors"))

    cursor.execute("DELETE FROM doctors WHERE id = ?", (id,))
    connection.commit()
    connection.close()

    flash("Doctor deleted successfully.", "success")
    return redirect(url_for("doctors"))


# ----------------------
# Appointments
# ----------------------


@app.route("/appointments")
def appointments():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            appointments.id,
            patients.name AS patient_name,
            doctors.name AS doctor_name,
            appointments.appointment_date,
            appointments.appointment_time,
            appointments.status
        FROM appointments
        JOIN patients ON appointments.patient_id = patients.id
        JOIN doctors ON appointments.doctor_id = doctors.id
        WHERE 1 = 1
    """
    params = []

    if search:
        query += """
            AND (
                patients.name LIKE ?
                OR doctors.name LIKE ?
            )
        """
        params.extend([f"%{search}%", f"%{search}%"])

    if status_filter in ALLOWED_APPOINTMENT_STATUSES:
        query += " AND appointments.status = ?"
        params.append(status_filter)

    query += """
        ORDER BY appointments.appointment_date DESC,
                 appointments.appointment_time DESC,
                 appointments.id DESC
    """

    cursor.execute(query, params)
    appointments_list = cursor.fetchall()
    connection.close()

    return render_template(
        "appointments.html",
        page_title="Appointments",
        appointments=appointments_list,
        search=search,
        status_filter=status_filter,
    )


def appointment_form_data(connection):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, age
        FROM patients
        ORDER BY name
        """
    )
    patients_list = cursor.fetchall()

    cursor.execute(
        """
        SELECT id, name, specialization
        FROM doctors
        ORDER BY name
        """
    )
    doctors_list = cursor.fetchall()

    return patients_list, doctors_list


@app.route("/add-appointment", methods=["GET", "POST"])
def add_appointment():
    connection = get_db_connection()

    patients_list, doctors_list = appointment_form_data(connection)

    if request.method == "POST":
        form = {
            "patient_id": request.form.get("patient_id", "").strip(),
            "doctor_id": request.form.get("doctor_id", "").strip(),
            "appointment_date": request.form.get("appointment_date", "").strip(),
            "appointment_time": request.form.get("appointment_time", "").strip(),
            "status": request.form.get("status", "Scheduled").strip(),
        }

        error = None

        try:
            patient_id = int(form["patient_id"])
            doctor_id = int(form["doctor_id"])
        except ValueError:
            error = "Please select a valid patient and doctor."

        if error is None and not form["appointment_date"]:
            error = "Appointment date is required."

        if error is None and not form["appointment_time"]:
            error = "Appointment time is required."

        if error is None:
            try:
                datetime.strptime(
                    f"{form['appointment_date']} {form['appointment_time']}",
                    "%Y-%m-%d %H:%M",
                )
            except ValueError:
                error = "Please enter a valid appointment date and time."

        if error is None and form["status"] not in ALLOWED_APPOINTMENT_STATUSES:
            error = "Please select a valid appointment status."

        if error is None:
            cursor = connection.cursor()

            cursor.execute(
                "SELECT id FROM patients WHERE id = ?",
                (patient_id,),
            )
            patient_exists = cursor.fetchone()

            cursor.execute(
                "SELECT id FROM doctors WHERE id = ?",
                (doctor_id,),
            )
            doctor_exists = cursor.fetchone()

            if not patient_exists or not doctor_exists:
                error = "The selected patient or doctor does not exist."

        if error is None and form["status"] == "Scheduled":
            cursor.execute(
                """
                SELECT 1
                FROM appointments
                WHERE doctor_id = ?
                  AND appointment_date = ?
                  AND appointment_time = ?
                  AND status = 'Scheduled'
                LIMIT 1
                """,
                (
                    doctor_id,
                    form["appointment_date"],
                    form["appointment_time"],
                ),
            )

            if cursor.fetchone():
                error = (
                    "This doctor already has a scheduled appointment "
                    "at that date and time."
                )

        if error:
            connection.close()
            flash(error, "danger")
            return render_template(
                "add_appointment.html",
                patients=patients_list,
                doctors=doctors_list,
                page_title="Add Appointment",
                form=form,
            )

        connection.execute(
            """
            INSERT INTO appointments
            (patient_id, doctor_id, appointment_date, appointment_time, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                doctor_id,
                form["appointment_date"],
                form["appointment_time"],
                form["status"],
            ),
        )
        connection.commit()
        connection.close()

        flash("Appointment added successfully.", "success")
        return redirect(url_for("appointments"))

    connection.close()

    return render_template(
        "add_appointment.html",
        patients=patients_list,
        doctors=doctors_list,
        page_title="Add Appointment",
        form={},
    )


@app.route("/complete-appointment/<int:appointment_id>", methods=["POST"])
def complete_appointment(appointment_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE appointments
        SET status = 'Completed'
        WHERE id = ? AND status = 'Scheduled'
        """,
        (appointment_id,),
    )

    if cursor.rowcount == 0:
        connection.close()
        flash(
            "Appointment could not be completed. It may not be scheduled.",
            "warning",
        )
        return redirect(url_for("appointments"))

    connection.commit()
    connection.close()

    flash("Appointment marked as completed.", "success")
    return redirect(url_for("appointments"))


@app.route("/cancel-appointment/<int:appointment_id>", methods=["POST"])
def cancel_appointment(appointment_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE appointments
        SET status = 'Cancelled'
        WHERE id = ? AND status = 'Scheduled'
        """,
        (appointment_id,),
    )

    if cursor.rowcount == 0:
        connection.close()
        flash(
            "Appointment could not be cancelled. It may not be scheduled.",
            "warning",
        )
        return redirect(url_for("appointments"))

    connection.commit()
    connection.close()

    flash("Appointment cancelled successfully.", "success")
    return redirect(url_for("appointments"))


if __name__ == "__main__":
    app.run(debug=True)
