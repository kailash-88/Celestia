"""Adherence reporting and analytics routes."""

from flask import Blueprint, render_template, session
from routes.auth import role_required
from database.db import query_db

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("", methods=["GET"])
@role_required('patient')
def index():
    uid = session["user_id"]
    logs = query_db("SELECT status FROM dose_logs WHERE user_id=?", [uid])
    taken = sum(1 for l in logs if l["status"] == "taken")
    missed = sum(1 for l in logs if l["status"] == "missed")
    pending = sum(1 for l in logs if l["status"] == "pending")
    completed = taken + missed
    adherence = round((taken / completed * 100), 1) if completed else 100.0

    # Per-medicine breakdown
    medicine_stats = query_db(
        """SELECT m.name AS medicine_name, m.dosage,
                  COUNT(dl.id) AS total_doses,
                  SUM(CASE WHEN dl.status = 'taken' THEN 1 ELSE 0 END) AS taken_doses,
                  SUM(CASE WHEN dl.status = 'missed' THEN 1 ELSE 0 END) AS missed_doses
           FROM medicines m
           JOIN schedules s ON s.medicine_id = m.id
           LEFT JOIN dose_logs dl ON dl.schedule_id = s.id
           WHERE m.user_id = ?
           GROUP BY m.id
           ORDER BY total_doses DESC""",
        [uid]
    )

    return render_template(
        "reports.html",
        taken=taken,
        missed=missed,
        pending=pending,
        total=len(logs),
        adherence=adherence,
        medicine_stats=medicine_stats
    )
