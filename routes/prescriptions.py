"""Patient prescription status and review history."""
import json
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from database.db import execute_db, query_db
from routes.auth import role_required

prescriptions_bp = Blueprint("prescriptions", __name__, url_prefix="/prescriptions")


@prescriptions_bp.get("")
@role_required('patient')
def index():
    rows = query_db(
        "SELECT id, image_path, status, scan_date, patient_confirmed_at, approved_at, doctor_name, extracted_data, "
        "(SELECT comments FROM prescription_reviews r WHERE r.prescription_id=prescriptions.id ORDER BY r.created_at DESC LIMIT 1) AS review_comments "
        "FROM prescriptions WHERE user_id=? ORDER BY scan_date DESC",
        [session["user_id"]],
    )
    items = []
    for row in rows:
        item = dict(row)
        item["fields"] = json.loads(item.pop("extracted_data") or "{}")
        items.append(item)
    return render_template("prescriptions.html", prescriptions=items)


@prescriptions_bp.post("/<int:prescription_id>/respond")
@role_required('patient')
def respond(prescription_id):
    prescription = query_db("SELECT extracted_data,status FROM prescriptions WHERE id=? AND user_id=?", [prescription_id, session["user_id"]], one=True)
    response = request.form.get("response", "").strip()
    if not prescription or prescription["status"] != "clarification_requested":
        flash("This prescription is not awaiting clarification.", "warning")
    elif not response:
        flash("Enter a response before resubmitting.", "error")
    else:
        fields = json.loads(prescription["extracted_data"] or "{}")
        fields["patient_response"] = response
        execute_db("UPDATE prescriptions SET extracted_data=?, status='pending_doctor_assignment', assigned_doctor_id=NULL WHERE id=? AND user_id=?", [json.dumps(fields), prescription_id, session["user_id"]])
        flash("Your response was saved and returned for doctor assignment.", "success")
    return redirect(url_for("prescriptions.index"))
