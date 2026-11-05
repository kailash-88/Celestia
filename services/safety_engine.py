"""Medicine safety checks based on verified data only."""

import json
import os
from datetime import date, datetime


def _load_interactions():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "interactions.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


def check_duplicates(medicines):
    seen = {}
    results = []
    for m in medicines:
        ing = (m.get("active_ingredient") or m.get("name") or "").lower().strip()
        if not ing:
            continue
        if ing in seen:
            results.append({
                "category": "duplicate_ingredient",
                "medicines": [seen[ing], m.get("name", "")],
                "explanation": "Same active ingredient detected in multiple medicines.",
                "source": "MediMitra safety engine",
                "verification_status": "verified",
            })
        else:
            seen[ing] = m.get("name", "")
    return results


def check_interactions(medicines):
    interactions = _load_interactions()
    results = []
    names = [(m.get("active_ingredient") or m.get("name") or "").lower().strip() for m in medicines]
    for entry in interactions:
        a = entry["ingredient_a"].lower()
        b = entry["ingredient_b"].lower()
        if a in names and b in names:
            results.append({
                "category": "interaction",
                "medicines": [entry["ingredient_a"], entry["ingredient_b"]],
                "explanation": entry["explanation"],
                "source": entry["source"],
                "verification_status": "verified",
            })
    # Not covered => unavailable, never safe
    covered_pairs = {(e["ingredient_a"].lower(), e["ingredient_b"].lower()) for e in interactions}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pair = (names[i], names[j])
            rev = (names[j], names[i])
            if pair not in covered_pairs and rev not in covered_pairs and names[i] and names[j] and names[i] != names[j]:
                results.append({
                    "category": "interaction_unavailable",
                    "medicines": [medicines[i].get("name", ""), medicines[j].get("name", "")],
                    "explanation": "Interaction information unavailable for this medicine.",
                    "source": "MediMitra safety engine",
                    "verification_status": "unverified",
                })
    return results


def check_expiry(medicines):
    today = date.today()
    results = []
    for m in medicines:
        expiry = m.get("expiry_date")
        if not expiry:
            results.append({
                "category": "unverified_expiry",
                "medicines": [m.get("name", "")],
                "explanation": "Expiry date unverified.",
                "source": "MediMitra safety engine",
                "verification_status": "unverified",
            })
            continue
        try:
            d = datetime.strptime(expiry, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            results.append({
                "category": "unverified_expiry",
                "medicines": [m.get("name", "")],
                "explanation": "Expiry date unverified.",
                "source": "MediMitra safety engine",
                "verification_status": "unverified",
            })
            continue
        if d < today:
            results.append({"category": "expired", "medicines": [m.get("name", "")], "explanation": "Medicine expired.", "source": "MediMitra safety engine", "verification_status": "verified"})
        elif (d - today).days <= 30:
            results.append({"category": "near_expiry", "medicines": [m.get("name", "")], "explanation": "Medicine near expiry.", "source": "MediMitra safety engine", "verification_status": "verified"})
    return results


def check_missing(medicines):
    results = []
    for m in medicines:
        if not m.get("name") or not m.get("active_ingredient"):
            results.append({
                "category": "missing_information",
                "medicines": [m.get("name", "")],
                "explanation": "Missing medicine information.",
                "source": "MediMitra safety engine",
                "verification_status": "unverified",
            })
    return results


def run_safety_check(medicines):
    out = []
    out += check_duplicates(medicines)
    out += check_interactions(medicines)
    out += check_expiry(medicines)
    out += check_missing(medicines)
    return out



def run_safety_checks(user_id):
    """Run comprehensive safety checks for a user ID and return identified issues."""
    from database.db import query_db, execute_db
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
    return run_safety_check(payload)
