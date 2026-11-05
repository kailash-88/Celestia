"""
MediMitra Caregiver Dashboard
Enables family members to monitor and support patients:
- Connected family members overview & switching
- Adherence tracking and today's doses
- Smart alerts: repeated missed doses, low medicine stock, expired medicines
- Doctor communication & instructions
- Family health reports
"""

import json
from datetime import datetime, date
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from routes.auth import role_required, get_current_user
from database.db import query_db, execute_db

caregiver_bp = Blueprint("caregiver", __name__, url_prefix="/caregiver")


@caregiver_bp.route("", methods=["GET"])
@role_required('caregiver')
def index():
    user_id = session["user_id"]

    links = query_db(
        """SELECT cl.*, u.full_name, u.email, u.phone,
                  pp.age, pp.gender, pp.blood_group, pp.allergies, pp.conditions,
                  pp.emergency_contact_name, pp.emergency_contact_phone
           FROM caregiver_links cl 
           JOIN users u ON u.id = cl.patient_id 
           LEFT JOIN patient_profiles pp ON pp.user_id = u.id
           WHERE cl.caregiver_id = ? AND cl.status = 'active'""",
        [user_id]
    )

    patients_data = []
    total_missed_alerts = 0
    total_low_stock = 0

    for link in links:
        pid = link["patient_id"]

        # Today's doses
        doses_today = query_db(
            """SELECT dl.*, s.time_of_day, s.scheduled_time, s.dosage_amount, s.instructions, m.name AS medicine_name
               FROM dose_logs dl 
               JOIN schedules s ON s.id = dl.schedule_id 
               JOIN medicines m ON m.id = s.medicine_id
               WHERE dl.user_id = ? AND DATE(dl.scheduled_for) = DATE('now')
               ORDER BY dl.scheduled_for ASC""",
            [pid]
        )

        # Recent missed doses (last 3 days)
        missed_doses = query_db(
            """SELECT dl.*, m.name AS medicine_name, s.time_of_day, dl.scheduled_for
               FROM dose_logs dl
               JOIN schedules s ON s.id = dl.schedule_id
               JOIN medicines m ON m.id = s.medicine_id
               WHERE dl.user_id = ? AND dl.status = 'missed' AND dl.scheduled_for >= datetime('now', '-3 days')
               ORDER BY dl.scheduled_for DESC""",
            [pid]
        )
        total_missed_alerts += len(missed_doses)

        # Low stock medicines (< 5 units)
        low_stock_meds = query_db(
            "SELECT name, dosage, quantity FROM medicines WHERE user_id = ? AND quantity <= 5",
            [pid]
        )
        total_low_stock += len(low_stock_meds)

        # Active safety alerts
        alerts = query_db(
            "SELECT * FROM safety_alerts WHERE user_id = ? AND is_dismissed = 0 ORDER BY created_at DESC",
            [pid]
        )

        # Adherence calculation
        all_doses = query_db("SELECT status FROM dose_logs WHERE user_id = ?", [pid])
        taken = sum(1 for d in all_doses if d["status"] == "taken")
        missed = sum(1 for d in all_doses if d["status"] == "missed")
        total = taken + missed
        adherence = round((taken / total * 100), 1) if total else 100.0

        # Latest doctor instructions from approved prescriptions
        recent_rx = query_db(
            """SELECT p.*, (SELECT comments FROM prescription_reviews r WHERE r.prescription_id=p.id ORDER BY r.created_at DESC LIMIT 1) AS doctor_comment
               FROM prescriptions p 
               WHERE p.user_id = ? AND p.status = 'approved' 
               ORDER BY p.approved_at DESC LIMIT 2""",
            [pid]
        )

        patients_data.append({
            "link": link,
            "doses_today": doses_today,
            "missed_doses": missed_doses,
            "low_stock_meds": low_stock_meds,
            "alerts": alerts,
            "adherence": adherence,
            "taken": taken,
            "missed": missed,
            "recent_rx": recent_rx
        })

    return render_template(
        "caregiver.html",
        patients=patients_data,
        total_missed_alerts=total_missed_alerts,
        total_low_stock=total_low_stock
    )


@caregiver_bp.route("/link", methods=["POST"])
@role_required('caregiver')
def link_patient():
    caregiver_id = session["user_id"]
    identifier = request.form.get("identifier", "").strip()

    if not identifier:
        flash("Enter the patient's username, email, or Patient ID.", "error")
        return redirect(url_for("caregiver.index"))

    patient = query_db(
        "SELECT id, full_name FROM users WHERE (username = ? OR email = ? OR id = ?) AND role = 'patient'",
        [identifier, identifier, identifier if identifier.isdigit() else -1], one=True
    )

    if not patient:
        flash("No patient found matching that username, email, or ID.", "error")
        return redirect(url_for("caregiver.index"))

    existing = query_db(
        "SELECT id, status FROM caregiver_links WHERE caregiver_id = ? AND patient_id = ?",
        [caregiver_id, patient["id"]], one=True
    )

    if existing:
        if existing["status"] == "active":
            flash(f"You are already linked to {patient['full_name']}.", "warning")
        else:
            execute_db("UPDATE caregiver_links SET status = 'active' WHERE id = ?", [existing["id"]])
            flash(f"Link with {patient['full_name']} reactivated successfully!", "success")
    else:
        execute_db(
            "INSERT INTO caregiver_links (caregiver_id, patient_id, status) VALUES (?, ?, 'active')",
            [caregiver_id, patient["id"]]
        )
        flash(f"Successfully connected to {patient['full_name']}! You can now monitor their medicines and receive adherence alerts.", "success")

    return redirect(url_for("caregiver.index"))


@caregiver_bp.route("/contact-doctor", methods=["POST"])
@role_required('caregiver')
def contact_doctor():
    patient_id = request.form.get("patient_id", type=int)
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()

    if not patient_id or not subject or not message:
        flash("Please provide all required fields.", "error")
        return redirect(url_for("caregiver.index"))

    # Find doctor assigned to patient
    assigned = query_db(
        "SELECT assigned_doctor_id FROM prescriptions WHERE user_id = ? AND assigned_doctor_id IS NOT NULL ORDER BY approved_at DESC LIMIT 1",
        [patient_id], one=True
    )
    doc_id = assigned["assigned_doctor_id"] if assigned else None
    if not doc_id:
        doc = query_db("SELECT user_id FROM doctor_profiles WHERE verification_status='verified' LIMIT 1", one=True)
        doc_id = doc["user_id"] if doc else None

    caregiver_name = session["full_name"]
    formatted_msg = f"[Caregiver Note from {caregiver_name}]: {message}"

    execute_db(
        """INSERT INTO patient_queries (patient_id, doctor_id, subject, question, status)
           VALUES (?, ?, ?, ?, 'pending')""",
        [patient_id, doc_id, f"[Caregiver Alert] {subject}", formatted_msg]
    )

    flash("Your message was sent to the patient's assigned doctor.", "success")
    return redirect(url_for("caregiver.index"))


@caregiver_bp.route("/unlink/<int:link_id>", methods=["POST"])
@role_required('caregiver')
def unlink_patient(link_id):
    execute_db("DELETE FROM caregiver_links WHERE id = ? AND caregiver_id = ?", [link_id, session["user_id"]])
    flash("Disconnected monitoring for this patient.", "info")
    return redirect(url_for("caregiver.index"))


@caregiver_bp.route("/respond/<int:link_id>/<decision>", methods=["POST"])
def respond_to_request(link_id, decision):
    status = "active" if decision == "approve" else "revoked"
    execute_db("UPDATE caregiver_links SET status = ? WHERE id = ? AND patient_id = ?", [status, link_id, session["user_id"]])
    flash(f"Caregiver access request was {decision}d.", "success")
    return redirect(url_for("dashboard.index"))
