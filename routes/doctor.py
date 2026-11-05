"""
MediMitra Doctor Dashboard & Clinical Workflows
Handles:
1. Doctor Overview & Clinical Statistics
2. Patient Management & Detailed Profiles
3. Prescription Review & Approval (Approve, Reject, Correct, Request Clearer Image)
4. Patient Health Queries (Read questions, review attached images, provide medical instructions)
5. Create Digital Prescriptions
6. Medication Safety & Adherence Monitoring
"""

import json
import os
from datetime import datetime, date
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_from_directory, session, url_for
from database.db import execute_db, query_db
from routes.auth import login_required
from services.safety_engine import run_safety_checks

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


def _doctor_profile(user_id):
    return query_db("SELECT * FROM doctor_profiles WHERE user_id=?", [user_id], one=True)


def _require_verified_doctor():
    if session.get("role") != "doctor":
        abort(403)
    profile = _doctor_profile(session["user_id"])
    if not profile or profile["verification_status"] != "verified":
        return None
    return profile


@doctor_bp.get("/<int:prescription_id>/image")
@login_required
def prescription_image(prescription_id):
    profile = _require_verified_doctor()
    if not profile:
        abort(403)
    p = query_db("SELECT image_path FROM prescriptions WHERE id = ?", [prescription_id], one=True)
    if not p or not p["image_path"]:
        return "Not found", 404
    filename = os.path.basename(p["image_path"])
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


# ==============================================================
# A. Doctor Overview
# ==============================================================
@doctor_bp.get("")
@login_required
def index():
    profile = _require_verified_doctor()
    if not profile:
        return render_template("doctor_dashboard.html", profile=_doctor_profile(session["user_id"]), prescriptions=[])

    doc_id = session["user_id"]

    # Pending prescription approvals
    pending_prescriptions = query_db(
        """SELECT p.*, u.full_name AS patient_name, u.email AS patient_email
           FROM prescriptions p 
           JOIN users u ON u.id = p.user_id 
           WHERE p.assigned_doctor_id = ? AND p.status = 'under_review' 
           ORDER BY p.patient_confirmed_at DESC""",
        [doc_id]
    )

    # Incoming patient queries
    pending_queries = query_db(
        """SELECT pq.*, u.full_name AS patient_name 
           FROM patient_queries pq
           JOIN users u ON u.id = pq.patient_id
           WHERE (pq.doctor_id = ? OR pq.doctor_id IS NULL) AND pq.status = 'pending'
           ORDER BY pq.created_at DESC""",
        [doc_id]
    )

    # Assigned unique patients count
    patients_count = query_db(
        """SELECT COUNT(DISTINCT user_id) as count FROM (
               SELECT user_id FROM prescriptions WHERE assigned_doctor_id = ?
               UNION
               SELECT patient_id AS user_id FROM patient_queries WHERE doctor_id = ?
           )""",
        [doc_id, doc_id], one=True
    )["count"] or 0

    # Low adherence count (< 70%)
    low_adherence_patients = query_db(
        """SELECT u.id, u.full_name,
                  COUNT(CASE WHEN dl.status = 'taken' THEN 1 END) AS taken,
                  COUNT(CASE WHEN dl.status = 'missed' THEN 1 END) AS missed
           FROM users u
           JOIN dose_logs dl ON dl.user_id = u.id
           GROUP BY u.id
           HAVING (COUNT(CASE WHEN dl.status = 'taken' THEN 1 END) * 100.0 / NULLIF(COUNT(dl.id), 0)) < 70"""
    )

    # Missed doses in last 48 hours across patients
    recent_missed = query_db(
        """SELECT dl.*, u.full_name AS patient_name, m.name AS medicine_name
           FROM dose_logs dl
           JOIN users u ON u.id = dl.user_id
           JOIN schedules s ON s.id = dl.schedule_id
           JOIN medicines m ON m.id = s.medicine_id
           WHERE dl.status = 'missed' AND dl.scheduled_for >= datetime('now', '-2 days')
           ORDER BY dl.scheduled_for DESC LIMIT 5"""
    )

    stats = {
        "patients": max(patients_count, 1),
        "pending_prescriptions": len(pending_prescriptions),
        "pending_queries": len(pending_queries),
        "low_adherence_count": len(low_adherence_patients),
        "missed_alerts": len(recent_missed)
    }

    return render_template(
        "doctor_dashboard.html",
        profile=profile,
        prescriptions=pending_prescriptions,
        queries=pending_queries,
        stats=stats,
        recent_missed=recent_missed
    )


# ==============================================================
# B. Patient Management
# ==============================================================
@doctor_bp.get("/patients")
@login_required
def patients():
    profile = _require_verified_doctor()
    if not profile:
        abort(403)

    search = request.args.get("q", "").strip()
    query = """
        SELECT u.id, u.full_name, u.email, u.phone,
               pp.age, pp.gender, pp.blood_group, pp.allergies, pp.conditions,
               COUNT(DISTINCT m.id) as active_medicines,
               ROUND(SUM(CASE WHEN dl.status = 'taken' THEN 1.0 ELSE 0.0 END) * 100.0 / NULLIF(COUNT(dl.id), 0), 1) as adherence_rate
        FROM users u
        LEFT JOIN patient_profiles pp ON pp.user_id = u.id
        LEFT JOIN medicines m ON m.user_id = u.id
        LEFT JOIN dose_logs dl ON dl.user_id = u.id
        WHERE u.role = 'patient'
    """
    params = []
    if search:
        query += " AND (u.full_name LIKE ? OR u.email LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " GROUP BY u.id ORDER BY u.full_name"
    patient_list = query_db(query, params)

    return render_template("doctor_patients.html", patients=patient_list, search=search)


@doctor_bp.get("/patients/<int:patient_id>")
@login_required
def patient_detail(patient_id):
    profile = _require_verified_doctor()
    if not profile:
        abort(403)

    patient = query_db("SELECT * FROM users WHERE id = ? AND role = 'patient'", [patient_id], one=True)
    if not patient:
        abort(404)

    health_profile = query_db("SELECT * FROM patient_profiles WHERE user_id = ?", [patient_id], one=True)
    medicines = query_db("SELECT * FROM medicines WHERE user_id = ? ORDER BY created_at DESC", [patient_id])
    prescriptions = query_db("SELECT * FROM prescriptions WHERE user_id = ? ORDER BY scan_date DESC", [patient_id])
    queries = query_db("SELECT * FROM patient_queries WHERE patient_id = ? ORDER BY created_at DESC", [patient_id])
    safety_alerts = query_db("SELECT * FROM safety_alerts WHERE user_id = ? AND is_dismissed = 0", [patient_id])

    # Adherence logs
    doses = query_db(
        """SELECT dl.*, m.name as medicine_name, s.time_of_day 
           FROM dose_logs dl
           JOIN schedules s ON s.id = dl.schedule_id
           JOIN medicines m ON m.id = s.medicine_id
           WHERE dl.user_id = ? 
           ORDER BY dl.scheduled_for DESC LIMIT 15""",
        [patient_id]
    )

    taken = sum(1 for d in doses if d["status"] == "taken")
    missed = sum(1 for d in doses if d["status"] == "missed")
    total = taken + missed
    adherence = round((taken / total * 100), 1) if total else 100.0

    return render_template(
        "doctor_patient_detail.html",
        patient=patient,
        health_profile=health_profile,
        medicines=medicines,
        prescriptions=prescriptions,
        queries=queries,
        safety_alerts=safety_alerts,
        doses=doses,
        adherence=adherence
    )


# ==============================================================
# C. Prescription Review & Approval ⭐
# ==============================================================
@doctor_bp.get("/prescriptions")
@login_required
def prescriptions():
    profile = _require_verified_doctor()
    if not profile:
        abort(403)

    rows = query_db(
        """SELECT p.*, u.full_name AS patient_name, u.email AS patient_email
           FROM prescriptions p 
           JOIN users u ON u.id = p.user_id 
           WHERE p.assigned_doctor_id = ? 
           ORDER BY p.patient_confirmed_at DESC""",
        [session["user_id"]]
    )
    items = []
    for r in rows:
        d = dict(r)
        d["fields"] = json.loads(d.get("extracted_data") or "{}")
        items.append(d)

    return render_template("doctor_prescriptions.html", prescriptions=items)


@doctor_bp.route("/prescriptions/<int:prescription_id>", methods=["GET", "POST"])
@login_required
def review(prescription_id):
    profile = _require_verified_doctor()
    if not profile:
        abort(403)

    prescription = query_db(
        """SELECT p.*, u.full_name AS patient_name, u.email AS patient_email
           FROM prescriptions p 
           JOIN users u ON u.id = p.user_id 
           WHERE p.id = ? AND (p.assigned_doctor_id = ? OR p.assigned_doctor_id IS NULL)""",
        [prescription_id, session["user_id"]], one=True
    )
    if not prescription:
        abort(404)

    fields = json.loads(prescription["extracted_data"] or "{}")

    if request.method == "POST":
        action = request.form.get("action")  # 'approve', 'reject', 'request_clearer'
        comments = request.form.get("comments", "").strip()

        if action not in {"approve", "reject", "request_clearer"}:
            flash("Invalid clinical action selected.", "error")
            return redirect(url_for("doctor.review", prescription_id=prescription_id))

        if action == "request_clearer":
            execute_db(
                """UPDATE prescriptions 
                   SET status = 'clarification_requested' 
                   WHERE id = ?""",
                [prescription_id]
            )
            execute_db(
                """INSERT INTO prescription_reviews (prescription_id, doctor_id, action, comments, extracted_data)
                   VALUES (?, ?, 'request_clearer', ?, ?)""",
                [prescription_id, session["user_id"], comments or "Please upload a clearer, well-lit photo of the prescription.", json.dumps(fields)]
            )
            flash("Requested patient to upload a clearer image of the prescription.", "success")
            return redirect(url_for("doctor.index"))

        elif action == "reject":
            execute_db(
                """UPDATE prescriptions SET status = 'rejected' WHERE id = ?""",
                [prescription_id]
            )
            execute_db(
                """INSERT INTO prescription_reviews (prescription_id, doctor_id, action, comments, extracted_data)
                   VALUES (?, ?, 'reject', ?, ?)""",
                [prescription_id, session["user_id"], comments or "Prescription rejected following clinical review.", json.dumps(fields)]
            )
            flash("Prescription has been marked as rejected with your comments.", "success")
            return redirect(url_for("doctor.index"))

        elif action == "approve":
            # Extract medicines to add to patient's medicine cabinet
            med_names = request.form.getlist("medicine_name")
            dosages = request.form.getlist("dosage")
            frequencies = request.form.getlist("frequency")
            instructions_list = request.form.getlist("instructions")

            patient_id = prescription["user_id"]
            created_med_ids = []

            for i in range(len(med_names)):
                name = med_names[i].strip()
                if not name:
                    continue
                dosage = dosages[i].strip() if i < len(dosages) else "Standard"
                freq = frequencies[i].strip() if i < len(frequencies) else "Daily"
                inst = instructions_list[i].strip() if i < len(instructions_list) else "Take as prescribed"

                med_id = execute_db(
                    """INSERT INTO medicines 
                       (user_id, name, dosage, form, active_ingredients, purpose, warnings, 
                        quantity, prescription_id, source, verified, before_after_food)
                       VALUES (?, ?, ?, 'Tablet', ?, 'Prescribed by doctor', ?, 30, ?, 'prescription', 1, ?)""",
                    [patient_id, name, dosage, json.dumps([name]), inst, prescription_id, inst]
                )
                created_med_ids.append(med_id)

                # Create default schedule
                execute_db(
                    """INSERT INTO schedules 
                       (user_id, medicine_id, time_of_day, scheduled_time, dosage_amount, instructions, start_date, is_active)
                       VALUES (?, ?, 'morning', '09:00', '1 Tablet', ?, DATE('now'), 1)""",
                    [patient_id, med_id, inst]
                )

            # Update prescription status
            execute_db(
                """UPDATE prescriptions 
                   SET status = 'approved', approved_at = CURRENT_TIMESTAMP, extracted_data = ?
                   WHERE id = ?""",
                [json.dumps(fields), prescription_id]
            )

            execute_db(
                """INSERT INTO prescription_reviews (prescription_id, doctor_id, action, comments, extracted_data)
                   VALUES (?, ?, 'approve', ?, ?)""",
                [prescription_id, session["user_id"], comments or "Prescription approved. Medicines added to patient cabinet and schedule.", json.dumps(fields)]
            )

            # Run safety checks for newly added medicines
            run_safety_checks(patient_id)

            flash(f"Prescription approved! {len(created_med_ids)} medicines added to patient's cabinet and schedule.", "success")
            return redirect(url_for("doctor.index"))

    return render_template("doctor_review.html", prescription=prescription, fields=fields)


# ==============================================================
# D. Patient Health Queries ⭐
# ==============================================================
@doctor_bp.route("/queries", methods=["GET"])
@login_required
def queries():
    profile = _require_verified_doctor()
    if not profile:
        abort(403)

    doc_id = session["user_id"]
    incoming = query_db(
        """SELECT pq.*, u.full_name AS patient_name, u.email AS patient_email, pp.allergies, pp.conditions
           FROM patient_queries pq
           JOIN users u ON u.id = pq.patient_id
           LEFT JOIN patient_profiles pp ON pp.user_id = u.id
           WHERE pq.doctor_id = ? OR pq.doctor_id IS NULL
           ORDER BY pq.status ASC, pq.created_at DESC""",
        [doc_id]
    )

    return render_template("doctor_queries.html", queries=incoming)


@doctor_bp.route("/queries/<int:query_id>/respond", methods=["POST"])
@login_required
def respond_query(query_id):
    profile = _require_verified_doctor()
    if not profile:
        abort(403)

    response_text = request.form.get("response", "").strip()
    if not response_text:
        flash("Please enter a medical response.", "error")
        return redirect(url_for("doctor.queries"))

    execute_db(
        """UPDATE patient_queries 
           SET doctor_response = ?, status = 'answered', answered_at = CURRENT_TIMESTAMP, doctor_id = ?
           WHERE id = ?""",
        [response_text, session["user_id"], query_id]
    )

    flash("Response and clinical instructions sent to the patient.", "success")
    return redirect(url_for("doctor.queries"))


# ==============================================================
# E. Create Digital Prescription
# ==============================================================
@doctor_bp.route("/prescriptions/create", methods=["GET", "POST"])
@login_required
def create_prescription():
    profile = _require_verified_doctor()
    if not profile:
        abort(403)

    if request.method == "POST":
        patient_id = request.form.get("patient_id", type=int)
        med_names = request.form.getlist("med_name")
        dosages = request.form.getlist("dosage")
        frequencies = request.form.getlist("frequency")
        instructions = request.form.getlist("instructions")
        notes = request.form.get("notes", "").strip()

        if not patient_id or not med_names or not med_names[0].strip():
            flash("Please choose a patient and enter at least one medicine.", "error")
            return redirect(url_for("doctor.create_prescription"))

        medicines_data = []
        for i in range(len(med_names)):
            m = med_names[i].strip()
            if m:
                d = dosages[i].strip() if i < len(dosages) else "Standard"
                f = frequencies[i].strip() if i < len(frequencies) else "Daily"
                inst = instructions[i].strip() if i < len(instructions) else "Take as directed"
                medicines_data.append({
                    "name": m, "dosage": d, "frequency": f, "instructions": inst
                })

                # Direct add to patient medicines
                m_id = execute_db(
                    """INSERT INTO medicines 
                       (user_id, name, dosage, form, active_ingredients, purpose, warnings, quantity, source, verified, before_after_food)
                       VALUES (?, ?, ?, 'Tablet', ?, ?, ?, 30, 'doctor', 1, ?)""",
                    [patient_id, m, d, json.dumps([m]), notes or "Prescribed by Doctor", inst, inst]
                )

                # Add schedule
                execute_db(
                    """INSERT INTO schedules 
                       (user_id, medicine_id, time_of_day, scheduled_time, dosage_amount, instructions, start_date, is_active)
                       VALUES (?, ?, 'morning', '09:00', '1 Tablet', ?, DATE('now'), 1)""",
                    [patient_id, m_id, inst]
                )

        rx_data = json.dumps({
            "doctor_name": session["full_name"],
            "specialty": profile["specialty"],
            "notes": notes,
            "medicines": medicines_data
        })

        execute_db(
            """INSERT INTO prescriptions 
               (user_id, image_path, raw_ocr_text, extracted_data, doctor_name, status, assigned_doctor_id, approved_at, verified)
               VALUES (?, 'digital_prescription', 'Digital prescription created by verified doctor', ?, ?, 'approved', ?, CURRENT_TIMESTAMP, 1)""",
            [patient_id, rx_data, session["full_name"], session["user_id"]]
        )

        run_safety_checks(patient_id)
        flash("Digital prescription created and medicines added directly to patient schedule!", "success")
        return redirect(url_for("doctor.patients"))

    patients = query_db("SELECT id, full_name, email FROM users WHERE role = 'patient' ORDER BY full_name")
    master_medicines = query_db("SELECT name, standard_strength, before_after_food FROM medicine_database ORDER BY name")
    return render_template("doctor_create_prescription.html", patients=patients, master_medicines=master_medicines)


# ==============================================================
# F. Medication Safety & Adherence Monitoring
# ==============================================================
@doctor_bp.get("/safety")
@login_required
def safety():
    profile = _require_verified_doctor()
    if not profile:
        abort(403)

    alerts = query_db(
        """SELECT sa.*, u.full_name AS patient_name, u.email AS patient_email
           FROM safety_alerts sa
           JOIN users u ON u.id = sa.user_id
           WHERE sa.is_dismissed = 0
           ORDER BY CASE sa.severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END"""
    )

    adherence_stats = query_db(
        """SELECT u.id, u.full_name,
                  COUNT(CASE WHEN dl.status = 'taken' THEN 1 END) AS taken,
                  COUNT(CASE WHEN dl.status = 'missed' THEN 1 END) AS missed,
                  ROUND(COUNT(CASE WHEN dl.status = 'taken' THEN 1 END) * 100.0 / NULLIF(COUNT(dl.id), 0), 1) AS adherence
           FROM users u
           JOIN dose_logs dl ON dl.user_id = u.id
           GROUP BY u.id
           ORDER BY adherence ASC"""
    )

    return render_template("doctor_safety.html", alerts=alerts, adherence_stats=adherence_stats)
