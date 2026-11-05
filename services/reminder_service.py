"""
MediMitra Reminder Service
Handles daily dose log generation and upcoming medication alerts.
"""

from datetime import date, datetime
from database.db import query_db, execute_db


def generate_today_dose_logs(user_id=None):
    """
    Ensure every active schedule has a dose_log entry for today.
    Can be run per-user or globally across all users.
    """
    today_str = date.today().isoformat()
    query = "SELECT s.* FROM schedules s WHERE s.is_active = 1"
    params = []
    if user_id:
        query += " AND s.user_id = ?"
        params.append(user_id)

    schedules = query_db(query, params)
    created_count = 0

    for s in schedules:
        # Check if log already exists for this schedule today
        existing = query_db(
            """SELECT id FROM dose_logs 
               WHERE schedule_id = ? AND DATE(scheduled_for) = DATE('now')""",
            [s["id"]],
            one=True,
        )
        if not existing:
            scheduled_datetime = f"{today_str} {s['scheduled_time']}:00"
            execute_db(
                """INSERT INTO dose_logs (schedule_id, user_id, status, scheduled_for)
                   VALUES (?, ?, 'pending', ?)""",
                [s["id"], s["user_id"], scheduled_datetime]
            )
            created_count += 1

    return created_count


def get_pending_doses_for_user(user_id):
    """Retrieve all pending doses for today for a given user."""
    return query_db(
        """SELECT dl.*, s.scheduled_time, s.time_of_day, s.dosage_amount, s.instructions,
                  m.name AS medicine_name, m.form AS medicine_form
           FROM dose_logs dl
           JOIN schedules s ON dl.schedule_id = s.id
           JOIN medicines m ON s.medicine_id = m.id
           WHERE dl.user_id = ? AND dl.status = 'pending' AND DATE(dl.scheduled_for) = DATE('now')
           ORDER BY dl.scheduled_for ASC""",
        [user_id]
    )
