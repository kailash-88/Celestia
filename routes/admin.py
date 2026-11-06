"""
MediMitra Administrator Dashboard
Handles:
1. Platform Overview & System Statistics
2. User Management (Activate, Deactivate, Filter by Role)
3. Doctor Verification (Review Credentials, Approve/Reject)
4. Master Medicine Database Management (Add, Edit, Maintain interaction data)
5. AI & Security Audit Logs
"""

import json
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from database.db import execute_db, query_db
from routes.auth import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ==============================================================
# A. Admin Overview
# ==============================================================
@admin_bp.get("")
@role_required("admin")
def index():
    # User stats
    stats = query_db(
        """SELECT COUNT(*) AS total_users,
                  SUM(role = 'patient') AS patients,
                  SUM(role = 'doctor') AS doctors,
                  SUM(role = 'caregiver') AS caregivers,
                  SUM(is_active = 1) AS active_users
           FROM users""",
        one=True
    )

    # Verification status
    doctor_status = query_db(
        """SELECT SUM(verification_status = 'pending') AS pending,
                  SUM(verification_status = 'verified') AS verified
           FROM doctor_profiles""",
        one=True
    )

    # Prescriptions processed
    rx_stats = query_db(
        """SELECT COUNT(*) AS total,
                  SUM(status = 'approved') AS approved,
                  SUM(status = 'under_review') AS under_review,
                  SUM(status = 'pending_doctor_assignment') AS pending_assignment
           FROM prescriptions""",
        one=True
    )

    # Master medicine count
    med_db_count = query_db("SELECT COUNT(*) as count FROM medicine_database", one=True)["count"]

    # Pending doctor verifications
    pending_doctors = query_db(
        """SELECT u.id, u.full_name, u.email, u.phone, d.specialty, d.license_number, d.qualifications, d.verification_status
           FROM doctor_profiles d 
           JOIN users u ON u.id = d.user_id 
           WHERE d.verification_status = 'pending'
           ORDER BY u.created_at DESC"""
    )

    # Recent system logs
    recent_logs = query_db(
        """SELECT sl.*, u.full_name as user_name 
           FROM system_logs sl
           LEFT JOIN users u ON u.id = sl.user_id
           ORDER BY sl.created_at DESC LIMIT 10"""
    )

    # Pending prescription assignments
    pending_assignments = query_db(
        """SELECT p.id, p.user_id, p.scan_date, p.patient_confirmed_at, u.full_name 
           FROM prescriptions p 
           JOIN users u ON u.id = p.user_id 
           WHERE p.status = 'pending_doctor_assignment' 
           ORDER BY p.scan_date"""
    )

    verified_doctors = query_db(
        """SELECT u.id, u.full_name, d.specialty 
           FROM doctor_profiles d 
           JOIN users u ON u.id = d.user_id 
           WHERE d.verification_status = 'verified' 
           ORDER BY u.full_name"""
    )

    return render_template(
        "admin_dashboard.html",
        stats=stats,
        doctor_status=doctor_status,
        rx_stats=rx_stats,
        med_db_count=med_db_count,
        pending_doctors=pending_doctors,
        recent_logs=recent_logs,
        pending_assignments=pending_assignments,
        verified_doctors=verified_doctors
    )


# ==============================================================
# B. User Management
# ==============================================================
@admin_bp.route("/users", methods=["GET"])
@role_required("admin")
def users():
    role_filter = request.args.get("role", "").strip()
    search = request.args.get("q", "").strip()

    sql = "SELECT id, username, email, full_name, role, phone, is_active, created_at FROM users WHERE 1=1"
    params = []

    if role_filter:
        sql += " AND role = ?"
        params.append(role_filter)

    if search:
        sql += " AND (full_name LIKE ? OR username LIKE ? OR email LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    sql += " ORDER BY created_at DESC"
    all_users = query_db(sql, params)

    return render_template("admin_users.html", users=all_users, role_filter=role_filter, search=search)


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@role_required("admin")
def toggle_user_status(user_id):
    user = query_db("SELECT id, is_active, full_name FROM users WHERE id = ?", [user_id], one=True)
    if not user:
        abort(404)

    new_status = 0 if user["is_active"] else 1
    execute_db("UPDATE users SET is_active = ? WHERE id = ?", [new_status, user_id])

    status_label = "activated" if new_status == 1 else "deactivated"
    execute_db(
        "INSERT INTO system_logs (user_id, event_type, status, details) VALUES (?, 'user_status_change', 'success', ?)",
        [session["user_id"], f"Administrator {status_label} account for user {user['full_name']} (ID {user_id})"]
    )

    flash(f"User account for '{user['full_name']}' has been {status_label}.", "success")
    return redirect(url_for("admin.users"))


# ==============================================================
# C. Doctor Verification
# ==============================================================
@admin_bp.post("/doctors/<int:doctor_id>/verify")
@role_required("admin")
def verify_doctor(doctor_id):
    status = request.form.get("status")
    if status not in {"verified", "rejected"}:
        abort(400)

    execute_db(
        """UPDATE doctor_profiles 
           SET verification_status = ?, 
               verified_at = CASE WHEN ? = 'verified' THEN CURRENT_TIMESTAMP ELSE NULL END 
           WHERE user_id = ?""",
        [status, status, doctor_id]
    )

    execute_db(
        "INSERT INTO system_logs (user_id, event_type, status, details) VALUES (?, 'doctor_verification', 'success', ?)",
        [session["user_id"], f"Doctor ID {doctor_id} application was {status} by admin"]
    )

    flash(f"Doctor credentials have been {status}.", "success")
    return redirect(url_for("admin.index"))


# ==============================================================
# D. Master Medicine Database Management
# ==============================================================
@admin_bp.route("/medicines", methods=["GET", "POST"])
@role_required("admin")
def medicines():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        generic_name = request.form.get("generic_name", "").strip()
        category = request.form.get("category", "").strip()
        standard_strength = request.form.get("standard_strength", "").strip()
        before_after_food = request.form.get("before_after_food", "").strip()
        common_uses = request.form.get("common_uses", "").strip()
        side_effects = request.form.get("side_effects", "").strip()
        warnings = request.form.get("warnings", "").strip()
        known_interactions = request.form.get("known_interactions", "").strip()

        if not name:
            flash("Medicine name is required.", "error")
            return redirect(url_for("admin.medicines"))

        execute_db(
            """INSERT INTO medicine_database 
               (name, generic_name, category, dosage_form, standard_strength, before_after_food, common_uses, side_effects, warnings, known_interactions)
               VALUES (?, ?, ?, 'Tablet', ?, ?, ?, ?, ?, ?)""",
            [name, generic_name, category, standard_strength, before_after_food, common_uses, side_effects, warnings, known_interactions]
        )

        execute_db(
            "INSERT INTO system_logs (user_id, event_type, status, details) VALUES (?, 'medicine_db_add', 'success', ?)",
            [session["user_id"], f"Added master medicine entry: {name}"]
        )

        flash(f"Master medicine entry '{name}' added successfully to the knowledgebase.", "success")
        return redirect(url_for("admin.medicines"))

    search = request.args.get("q", "").strip()
    sql = "SELECT * FROM medicine_database"
    params = []
    if search:
        sql += " WHERE name LIKE ? OR generic_name LIKE ? OR category LIKE ?"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    sql += " ORDER BY name ASC"

    meds = query_db(sql, params)
    return render_template("admin_medicines.html", medicines=meds, search=search)


@admin_bp.post("/prescriptions/<int:prescription_id>/assign")
@role_required("admin")
def assign_prescription(prescription_id):
    doctor_id = request.form.get("doctor_id", type=int)
    doctor = query_db("SELECT user_id FROM doctor_profiles WHERE user_id=? AND verification_status='verified'", [doctor_id], one=True) if doctor_id else None
    prescription = query_db("SELECT id FROM prescriptions WHERE id=? AND status='pending_doctor_assignment'", [prescription_id], one=True)

    if not doctor or not prescription:
        flash("Please select a verified doctor and a valid prescription.", "error")
    else:
        execute_db("UPDATE prescriptions SET assigned_doctor_id=?, status='under_review' WHERE id=?", [doctor_id, prescription_id])
        flash("Prescription assigned to doctor for clinical review.", "success")

    return redirect(url_for("admin.index"))


# ==============================================================
# F. App Updates & SMS / Push Broadcast Engine
# ==============================================================
@admin_bp.route("/releases", methods=["GET", "POST"])
@role_required("admin")
def releases():
    if request.method == "POST":
        version_code = request.form.get("version_code", type=int)
        version_name = request.form.get("version_name", "").strip()
        release_notes = request.form.get("release_notes", "").strip()
        force_update = 1 if request.form.get("force_update") == "1" else 0
        download_url = request.form.get("download_url", "").strip() or "https://play.google.com/store/apps/details?id=com.medimitra.app"
        send_sms = request.form.get("send_sms") == "1"

        if not version_code or not version_name:
            flash("Version code and version name are required.", "error")
            return redirect(url_for("admin.releases"))

        # 1. Insert release into database
        execute_db(
            """INSERT INTO app_releases (version_code, version_name, release_notes, force_update, download_url, released_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [version_code, version_name, release_notes, force_update, download_url, session["user_id"]]
        )

        # 2. Broadcast in-app notification to all users
        all_users = query_db("SELECT id, phone, full_name FROM users WHERE is_active = 1")
        sms_count = 0
        title = f"🚀 New MediMitra Update (v{version_name})"
        msg = f"A new version of MediMitra (v{version_name}) is available. {release_notes}"

        for u in all_users:
            execute_db(
                "INSERT INTO notifications (user_id, title, message, notification_type) VALUES (?, ?, ?, 'update')",
                [u["id"], title, msg]
            )
            if send_sms and u["phone"]:
                sms_count += 1

        # 3. Update SMS broadcast count
        execute_db(
            "UPDATE app_releases SET sms_broadcast_count = ? WHERE version_code = ?",
            [sms_count, version_code]
        )

        execute_db(
            "INSERT INTO system_logs (user_id, event_type, status, details) VALUES (?, 'app_update_broadcast', 'success', ?)",
            [session["user_id"], f"Broadcasted v{version_name} (code {version_code}) to {len(all_users)} users ({sms_count} SMS)"]
        )

        flash(f"Update v{version_name} published! In-app alerts sent to {len(all_users)} users and {sms_count} SMS queued.", "success")
        return redirect(url_for("admin.releases"))

    all_releases = query_db("SELECT * FROM app_releases ORDER BY version_code DESC")
    return render_template("admin_releases.html", releases=all_releases)
