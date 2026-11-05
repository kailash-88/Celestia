"""
MediMitra Medicine Management Routes
Handles listing, adding, viewing, editing, and deleting medicines.
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from routes.auth import role_required
from database.db import query_db, execute_db
from services.safety_engine import run_safety_check

medicines_bp = Blueprint("medicines", __name__, url_prefix="/medicines")


@medicines_bp.route("", methods=["GET"])
@role_required('patient')
def index():
    """List all medicines for the logged-in user with optional search."""
    search_query = request.args.get("q", "").strip()
    user_id = session["user_id"]

    if search_query:
        wildcard = f"%{search_query}%"
        medicines = query_db(
            """SELECT * FROM medicines 
               WHERE user_id = ? AND (name LIKE ? OR generic_name LIKE ? OR purpose LIKE ?)
               ORDER BY created_at DESC""",
            [user_id, wildcard, wildcard, wildcard]
        )
    else:
        medicines = query_db(
            "SELECT * FROM medicines WHERE user_id = ? ORDER BY created_at DESC",
            [user_id]
        )

    return render_template("medicines.html", medicines=medicines, search_query=search_query)


@medicines_bp.route("/new", methods=["GET", "POST"])
@role_required('patient')
def add():
    """Add a new medicine manually."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        generic_name = request.form.get("generic_name", "").strip() or None
        dosage = request.form.get("dosage", "").strip() or None
        form = request.form.get("form", "").strip() or None
        manufacturer = request.form.get("manufacturer", "").strip() or None
        purpose = request.form.get("purpose", "").strip() or None
        warnings = request.form.get("warnings", "").strip() or None
        expiry_date = request.form.get("expiry_date", "").strip() or None
        quantity_str = request.form.get("quantity", "0").strip()
        active_ingredients_raw = request.form.get("active_ingredients", "").strip()

        try:
            quantity = int(quantity_str) if quantity_str else 0
        except ValueError:
            quantity = 0

        # Store active ingredients as JSON list
        active_ingredients = [item.strip() for item in active_ingredients_raw.split(",") if item.strip()]
        active_ingredients_json = json.dumps(active_ingredients) if active_ingredients else None

        if not name:
            flash("Medicine name is required.", "error")
            return render_template("medicines.html", action="add")

        user_id = session["user_id"]
        medicine_id = execute_db(
            """INSERT INTO medicines 
               (user_id, name, generic_name, dosage, form, manufacturer, 
                active_ingredients, purpose, warnings, expiry_date, quantity, source, verified)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'manual', 1)""",
            [
                user_id, name, generic_name, dosage, form, manufacturer,
                active_ingredients_json, purpose, warnings, expiry_date, quantity
            ]
        )

        # Trigger quick safety alert generation if needed
        all_user_meds = query_db("SELECT * FROM medicines WHERE user_id = ?", [user_id])
        safety_payload = []
        for m in all_user_meds:
            # Parse ingredient if present
            ings = json.loads(m["active_ingredients"]) if m["active_ingredients"] else []
            safety_payload.append({
                "name": m["name"],
                "active_ingredient": ings[0] if ings else (m["generic_name"] or m["name"]),
                "expiry_date": m["expiry_date"]
            })
        
        alerts = run_safety_check(safety_payload)
        for alert in alerts:
            if alert["category"] in ("duplicate_ingredient", "interaction", "expired"):
                execute_db(
                    """INSERT INTO safety_alerts (user_id, alert_type, severity, title, description, medicine_ids)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    [
                        user_id,
                        alert["category"],
                        "high" if alert["category"] == "interaction" else "medium",
                        f"Safety Alert: {alert['category'].replace('_', ' ').capitalize()}",
                        alert["explanation"],
                        json.dumps(alert.get("medicines", []))
                    ]
                )

        flash(f"Medicine '{name}' has been added successfully.", "success")
        return redirect(url_for("medicines.index"))

    return render_template("medicines.html", action="add")


@medicines_bp.route("/<int:medicine_id>", methods=["GET"])
@role_required('patient')
def detail(medicine_id):
    """View details of a specific medicine."""
    user_id = session["user_id"]
    medicine = query_db(
        "SELECT * FROM medicines WHERE id = ? AND user_id = ?",
        [medicine_id, user_id],
        one=True
    )
    if not medicine:
        flash("Medicine not found.", "error")
        return redirect(url_for("medicines.index"))

    # Active schedules for this medicine
    schedules = query_db(
        "SELECT * FROM schedules WHERE medicine_id = ? AND user_id = ?",
        [medicine_id, user_id]
    )

    ingredients = []
    if medicine["active_ingredients"]:
        try:
            ingredients = json.loads(medicine["active_ingredients"])
        except (ValueError, TypeError):
            ingredients = [medicine["active_ingredients"]]

    return render_template("medicines.html", action="detail", medicine=medicine, schedules=schedules, ingredients=ingredients)


@medicines_bp.route("/<int:medicine_id>/edit", methods=["GET", "POST"])
@role_required('patient')
def edit(medicine_id):
    """Edit an existing medicine."""
    user_id = session["user_id"]
    medicine = query_db(
        "SELECT * FROM medicines WHERE id = ? AND user_id = ?",
        [medicine_id, user_id],
        one=True
    )
    if not medicine:
        flash("Medicine not found.", "error")
        return redirect(url_for("medicines.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        generic_name = request.form.get("generic_name", "").strip() or None
        dosage = request.form.get("dosage", "").strip() or None
        form = request.form.get("form", "").strip() or None
        manufacturer = request.form.get("manufacturer", "").strip() or None
        purpose = request.form.get("purpose", "").strip() or None
        warnings = request.form.get("warnings", "").strip() or None
        expiry_date = request.form.get("expiry_date", "").strip() or None
        quantity_str = request.form.get("quantity", "0").strip()
        active_ingredients_raw = request.form.get("active_ingredients", "").strip()

        try:
            quantity = int(quantity_str) if quantity_str else 0
        except ValueError:
            quantity = 0

        active_ingredients = [item.strip() for item in active_ingredients_raw.split(",") if item.strip()]
        active_ingredients_json = json.dumps(active_ingredients) if active_ingredients else None

        if not name:
            flash("Medicine name is required.", "error")
            return render_template("medicines.html", action="edit", medicine=medicine)

        execute_db(
            """UPDATE medicines 
               SET name=?, generic_name=?, dosage=?, form=?, manufacturer=?,
                   active_ingredients=?, purpose=?, warnings=?, expiry_date=?, quantity=?
               WHERE id=? AND user_id=?""",
            [
                name, generic_name, dosage, form, manufacturer,
                active_ingredients_json, purpose, warnings, expiry_date, quantity,
                medicine_id, user_id
            ]
        )
        flash(f"Medicine '{name}' updated successfully.", "success")
        return redirect(url_for("medicines.detail", medicine_id=medicine_id))

    ingredients_str = ""
    if medicine["active_ingredients"]:
        try:
            ingredients_str = ", ".join(json.loads(medicine["active_ingredients"]))
        except (ValueError, TypeError):
            ingredients_str = medicine["active_ingredients"]

    return render_template("medicines.html", action="edit", medicine=medicine, ingredients_str=ingredients_str)


@medicines_bp.route("/<int:medicine_id>/delete", methods=["POST"])
@role_required('patient')
def delete(medicine_id):
    """Delete a medicine and its associated schedules."""
    user_id = session["user_id"]
    # Remove associated schedules and dose logs
    schedules = query_db("SELECT id FROM schedules WHERE medicine_id = ? AND user_id = ?", [medicine_id, user_id])
    for s in schedules:
        execute_db("DELETE FROM dose_logs WHERE schedule_id = ?", [s["id"]])
    execute_db("DELETE FROM schedules WHERE medicine_id = ? AND user_id = ?", [medicine_id, user_id])
    execute_db("DELETE FROM medicines WHERE id = ? AND user_id = ?", [medicine_id, user_id])

    flash("Medicine and associated schedules removed.", "info")
    return redirect(url_for("medicines.index"))
