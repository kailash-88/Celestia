"""
MediMitra Report Service
Calculates adherence statistics, streak counts, and medication compliance metrics.
"""

from database.db import query_db


def get_adherence_summary(user_id):
    """Calculate overall taken vs missed doses and adherence percentage."""
    logs = query_db("SELECT status FROM dose_logs WHERE user_id = ?", [user_id])
    taken = sum(1 for l in logs if l["status"] == "taken")
    missed = sum(1 for l in logs if l["status"] == "missed")
    pending = sum(1 for l in logs if l["status"] == "pending")
    total_completed = taken + missed
    total = len(logs)

    adherence = round((taken / total_completed * 100), 1) if total_completed > 0 else 100.0

    return {
        "total": total,
        "taken": taken,
        "missed": missed,
        "pending": pending,
        "adherence": adherence,
    }
