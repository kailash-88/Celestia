"""Schedule and reminder routes."""

from datetime import date, datetime
from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from routes.auth import role_required
from database.db import query_db, execute_db

schedule_bp = Blueprint("schedule", __name__, url_prefix="/schedule")


@schedule_bp.route("", methods=["GET"])
@role_required('patient')
def index():
    user_id = session["user_id"]
    schedules = query_db(
        """SELECT s.*, m.name AS medicine_name, m.dosage AS med_dosage 
           FROM schedules s 
           JOIN medicines m ON m.id = s.medicine_id 
           WHERE s.user_id = ? AND s.is_active = 1
           ORDER BY s.scheduled_time ASC""",
        [user_id],
    )
    grouped = {"morning": [], "afternoon": [], "evening": [], "night": []}
    for s in schedules:
        slot = s["time_of_day"].lower() if s["time_of_day"] else "morning"
        grouped.setdefault(slot, []).append(s)

    logs = query_db(
        """SELECT dl.*, m.name AS medicine_name, s.time_of_day
           FROM dose_logs dl 
           LEFT JOIN schedules s ON s.id = dl.schedule_id 
           LEFT JOIN medicines m ON m.id = s.medicine_id 
           WHERE dl.user_id = ? 
           ORDER BY dl.scheduled_for DESC LIMIT 20""",
        [user_id],
    )

    user_meds = query_db("SELECT id, name, dosage, form FROM medicines WHERE user_id = ? ORDER BY name ASC", [user_id])
    return render_template("schedule.html", grouped=grouped, logs=logs, user_meds=user_meds, today=date.today().isoformat())


@schedule_bp.route("/add", methods=["POST"])
@role_required('patient')
def add():
    user_id = session["user_id"]
    medicine_id = request.form.get("medicine_id", type=int)
    time_of_day = request.form.get("time_of_day", "morning").strip().lower()
    scheduled_time = request.form.get("scheduled_time", "").strip()
    dosage_amount = request.form.get("dosage_amount", "").strip() or None
    instructions = request.form.get("instructions", "").strip() or None
    start_date = request.form.get("start_date", "").strip() or date.today().isoformat()
    end_date = request.form.get("end_date", "").strip() or None

    owned_medicine = query_db(
        "SELECT id FROM medicines WHERE id = ? AND user_id = ?",
        [medicine_id, user_id], one=True
    ) if medicine_id else None
    try:
        datetime.strptime(scheduled_time, "%H:%M")
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date) if end_date else None
        valid = not end or end >= start
    except ValueError:
        valid = False
    if (not owned_medicine or time_of_day not in {"morning", "afternoon", "evening", "night"}
            or not valid):
        flash("Choose one of your medicines and enter a valid time and date range.", "error")
        return redirect(url_for("schedule.index"))

    schedule_id = execute_db(
        """INSERT INTO schedules 
           (user_id, medicine_id, time_of_day, scheduled_time, dosage_amount, instructions, start_date, end_date, is_active)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
        [user_id, medicine_id, time_of_day, scheduled_time, dosage_amount, instructions, start_date, end_date]
    )

    # Record the first scheduled occurrence using the selected start date and time.
    execute_db(
        """INSERT INTO dose_logs (schedule_id, user_id, status, scheduled_for)
           VALUES (?, ?, 'pending', ?)""",
        [schedule_id, user_id, f"{start_date} {scheduled_time}:00"]
    )

    flash("Schedule created successfully.", "success")
    return redirect(url_for("schedule.index"))


@schedule_bp.route("/<int:schedule_id>/delete", methods=["POST"])
@role_required('patient')
def delete(schedule_id):
    user_id = session["user_id"]
    execute_db("DELETE FROM dose_logs WHERE schedule_id = ? AND user_id = ?", [schedule_id, user_id])
    execute_db("DELETE FROM schedules WHERE id = ? AND user_id = ?", [schedule_id, user_id])
    flash("Schedule removed.", "info")
    return redirect(url_for("schedule.index"))


@schedule_bp.route("/dose/<int:log_id>/<status>", methods=["POST"])
@role_required('patient')
def mark_dose(log_id, status):
    if status not in ("taken", "missed"):
        return redirect(url_for("schedule.index"))
    execute_db(
        "UPDATE dose_logs SET status=?, taken_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?",
        [status, log_id, session["user_id"]],
    )
    flash(f"Dose marked as {status}.", "success" if status == "taken" else "warning")
    return redirect(url_for("schedule.index"))
