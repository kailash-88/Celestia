"""
MediMitra Medicine Service
Business logic for managing medicine records, active ingredients, and stock.
"""

import json
from database.db import query_db, execute_db


def get_user_medicines(user_id):
    """Retrieve all medicines belonging to a specific user."""
    return query_db("SELECT * FROM medicines WHERE user_id = ? ORDER BY name ASC", [user_id])


def get_medicine_by_id(medicine_id, user_id):
    """Get single medicine by ID verified against user_id."""
    return query_db("SELECT * FROM medicines WHERE id = ? AND user_id = ?", [medicine_id, user_id], one=True)


def get_medicine_ingredients(medicine):
    """Parse JSON or string active ingredients into a clean list."""
    if not medicine or not medicine.get("active_ingredients"):
        return []
    try:
        raw = medicine["active_ingredients"]
        if isinstance(raw, list):
            return raw
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else [str(parsed)]
    except (ValueError, TypeError):
        return [str(medicine["active_ingredients"])]


def update_medicine_quantity(medicine_id, delta):
    """Adjust stock quantity for a medicine (e.g. decrement on dose taken)."""
    return execute_db(
        "UPDATE medicines SET quantity = MAX(0, quantity + ?) WHERE id = ?",
        [delta, medicine_id]
    )
