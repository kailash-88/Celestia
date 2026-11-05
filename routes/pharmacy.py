"""Pharmacist account verification and pharmacy workspace."""
from flask import Blueprint, abort, render_template, session
from database.db import query_db
from routes.auth import role_required

pharmacy_bp = Blueprint("pharmacy", __name__, url_prefix="/pharmacy")


@pharmacy_bp.get("")
@role_required("pharmacist")
def index():
    profile = query_db(
        "SELECT * FROM pharmacy_profiles WHERE user_id=?",
        [session["user_id"]], one=True,
    )
    if not profile:
        abort(403)
    return render_template("pharmacy_dashboard.html", profile=profile)
