"""
MediMitra Safety Engine Routes
Interactive medicine safety checks, active alerts, and drug interaction verification.
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from routes.auth import role_required
from database.db import query_db, execute_db
from services.safety_engine import (
    run_safety_check,
    check_interactions,
    _load_interactions,
)

safety_bp = Blueprint("safety", __name__, url_prefix="/safety")


def _get_user_cabinet_payload(user_id):
    """Format user's medicines into the payload structure required by safety_engine."""
    medicines = query_db("SELECT * FROM medicines WHERE user_id = ?", [user_id])
    payload = []
    for m in medicines:
        active_ing = m["name"]
        if m["active_ingredients"]:
            try:
                ings = json.loads(m["active_ingredients"])
                if ings and isinstance(ings, list):
                    active_ing = ings[0]
            except (ValueError, TypeError):
                active_ing = m["active_ingredients"]
        elif m["generic_name"]:
            active_ing = m["generic_name"]

        payload.append({
            "id": m["id"],
            "name": m["name"],
            "active_ingredient": active_ing,
            "expiry_date": m["expiry_date"],
            "dosage": m["dosage"],
            "form": m["form"],
        })
    return medicines, payload


@safety_bp.route("", methods=["GET"])
@role_required('patient')
def index():
    """Main safety overview: runs real-time check and lists persistent alerts."""
    user_id = session["user_id"]
    medicines, payload = _get_user_cabinet_payload(user_id)

    # Run real-time safety evaluation
    live_checks = run_safety_check(payload) if payload else []

    # Filter into categories
    interactions = [c for c in live_checks if c["category"] in ("interaction", "interaction_unavailable")]
    duplicates = [c for c in live_checks if c["category"] == "duplicate_ingredient"]
    expiries = [c for c in live_checks if c["category"] == "expired"]
    missing = [c for c in live_checks if c["category"] == "missing_info"]

    # Retrieve logged database alerts that are not yet dismissed
    saved_alerts = query_db(
        "SELECT * FROM safety_alerts WHERE user_id = ? AND is_dismissed = 0 ORDER BY created_at DESC",
        [user_id]
    )

    known_interactions = _load_interactions()

    return render_template(
        "safety.html",
        total_meds=len(medicines),
        live_checks=live_checks,
        interactions=interactions,
        duplicates=duplicates,
        expiries=expiries,
        missing=missing,
        saved_alerts=saved_alerts,
        known_count=len(known_interactions),
    )


@safety_bp.route("/dismiss/<int:alert_id>", methods=["POST"])
@role_required('patient')
def dismiss_alert(alert_id):
    """Dismiss a logged safety alert."""
    user_id = session["user_id"]
    execute_db(
        "UPDATE safety_alerts SET is_dismissed = 1 WHERE id = ? AND user_id = ?",
        [alert_id, user_id]
    )
    flash("Alert dismissed.", "info")
    return redirect(url_for("safety.index"))


@safety_bp.route("/check-pair", methods=["POST"])
@role_required('patient')
def check_pair():
    """Check potential interaction between any two drugs entered by user."""
    drug_a = request.form.get("drug_a", "").strip()
    drug_b = request.form.get("drug_b", "").strip()

    if not drug_a or not drug_b:
        flash("Please enter both medicine or active ingredient names.", "warning")
        return redirect(url_for("safety.index"))

    test_meds = [
        {"name": drug_a, "active_ingredient": drug_a},
        {"name": drug_b, "active_ingredient": drug_b},
    ]
    results = check_interactions(test_meds)

    # Pass result through session or flash
    found_known = [r for r in results if r["category"] == "interaction"]
    if found_known:
        flash(f"⚠️ Interaction Warning: {found_known[0]['explanation']} (Source: {found_known[0]['source']})", "error")
    else:
        flash(f"ℹ️ No known severe interaction recorded in verified database for '{drug_a}' and '{drug_b}'. Please consult your doctor or pharmacist to confirm.", "info")

    return redirect(url_for("safety.index"))
