"""Prescription and medicine scanning routes."""

import json
import os
import uuid

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, send_from_directory, session, url_for, Response
from werkzeug.utils import secure_filename

from database.db import execute_db, query_db
from routes.auth import role_required
from services.ocr_service import extract_prescription_data
from services.ai_service import extract_medicine_info
from services.safety_engine import run_safety_checks
from services.voice_service import generate_medicine_voice_scripts, LANGUAGES


scanner_bp = Blueprint("scanner", __name__, url_prefix="/scanner")


@scanner_bp.get("/<int:prescription_id>/image")
@role_required('patient')
def prescription_image(prescription_id):
    """Serve only the current user's uploaded prescription image."""
    prescription = query_db(
        "SELECT image_path FROM prescriptions WHERE id=? AND user_id=?",
        [prescription_id, session["user_id"]], one=True
    )
    if not prescription:
        return "Not found", 404
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        os.path.basename(prescription["image_path"]),
        as_attachment=False,
    )


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def _analyze_image(image_path):
    """Run local OCR/CV and optional vision AI for an uploaded image."""
    ocr_result = extract_prescription_data(image_path, current_app.config["TESSERACT_CMD"])
    fields = dict(ocr_result["fields"])
    analysis = extract_medicine_info(ocr_result["raw_text"], image_path=image_path)
    facts = analysis.get("extracted_facts", {})
    for target, source in {
        "name": "name", "generic_name": "active_ingredient", "active_ingredient": "active_ingredient",
        "manufacturer": "manufacturer", "batch_number": "batch_number", "manufacturing_date": "manufacturing_date",
        "dosage": "strength", "form": "form", "purpose": "purpose", "expiry_date": "expiry_date",
        "prescription_date": "prescription_date", "doctor_name": "doctor_name", "specialty": "specialty",
        "patient_name": "patient_name", "frequency": "frequency", "route": "route", "duration": "duration",
        "prescription_instructions": "prescription_instructions", "document_type": "document_type",
        "prescription_summary": "prescription_summary", "before_after_food": "before_after_food",
        "side_effects": "side_effects", "warnings": "warnings",
    }.items():
        if facts.get(source):
            fields[target] = facts[source]

    # Ensure medicine name is never cleared out
    if facts.get("name"):
        fields["name"] = facts["name"]
    elif not fields.get("name") and facts.get("active_ingredient"):
        fields["name"] = facts["active_ingredient"]

    if facts.get("medicines"):
        fields["medicines"] = facts["medicines"]

    fields["voice_scripts"] = generate_medicine_voice_scripts(fields)
    fields["voice_scripts_json"] = json.dumps(fields["voice_scripts"])
    fields["confidence"] = analysis.get("confidence", {})
    fields["uncertain_fields"] = analysis.get("uncertain_fields", [])
    fields["analysis_source"] = analysis.get("source", "smart_nlp")
    fields["analysis_notice"] = analysis.get("notice", "Check every suggestion against the uploaded image.")
    return ocr_result["raw_text"], fields


# ==============================================================
# 1. AI Medicine Strip Scanner (Strips, blister packs, boxes)
# ==============================================================
@scanner_bp.route("/medicine", methods=["GET", "POST"])
@role_required('patient')
def medicine_scan():
    """Scan medicine strip using camera or image upload to extract details, usage, food timing, and side effects."""
    user_id = session["user_id"]
    result = None

    if request.method == "POST":
        image = request.files.get("image")
        if not image or not image.filename:
            flash("Choose or take a photo of a medicine strip/box.", "error")
            return render_template("medicine_scanner.html")
        if not _allowed_file(image.filename):
            flash("Unsupported image format. Please use JPG, PNG or WEBP.", "error")
            return render_template("medicine_scanner.html")

        filename = f"strip_{uuid.uuid4().hex[:8]}_{secure_filename(image.filename)}"
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)
        relative_path = os.path.relpath(image_path, current_app.root_path)

        raw_ocr, fields = _analyze_image(image_path)
        med_name = fields.get("name", "").strip() or "Identified Medicine"
        generic_name = fields.get("generic_name", "").strip() or fields.get("active_ingredient", "").strip()
        dosage = fields.get("dosage", "").strip() or "Standard dose"
        form = fields.get("form", "").strip() or "Tablet"
        mfg_date = fields.get("manufacturing_date", "").strip()
        exp_date = fields.get("expiry_date", "").strip()

        # Look up verified knowledgebase with progressive search
        first_token = med_name.split()[0].lower() if med_name else ""
        db_match = query_db(
            "SELECT * FROM medicine_database WHERE LOWER(name) = ? LIMIT 1",
            [med_name.lower()], one=True
        )
        if not db_match and first_token and len(first_token) >= 3:
            db_match = query_db(
                "SELECT * FROM medicine_database WHERE LOWER(name) LIKE ? LIMIT 1",
                [f"{first_token}%"], one=True
            )
        if not db_match and generic_name:
            gen_token = generic_name.split()[0].lower()
            if len(gen_token) >= 3:
                db_match = query_db(
                    "SELECT * FROM medicine_database WHERE LOWER(generic_name) LIKE ? LIMIT 1",
                    [f"%{gen_token}%"], one=True
                )

        before_after_food = (
            (db_match["before_after_food"] if db_match and db_match["before_after_food"] else None)
            or fields.get("before_after_food")
            or "Take after meals with water."
        )
        common_uses = (
            (db_match["common_uses"] if db_match and db_match["common_uses"] else None)
            or fields.get("purpose")
            or "Therapeutic medication."
        )
        side_effects = (
            (db_match["side_effects"] if db_match and db_match["side_effects"] else None)
            or fields.get("side_effects")
            or "Mild nausea, headache, stomach upset."
        )
        warnings = (
            (db_match["warnings"] if db_match and db_match["warnings"] else None)
            or fields.get("warnings")
            or "Take as directed by doctor. Do not exceed prescribed dose."
        )

        # Check safety against patient's active medicines
        patient_meds = query_db("SELECT name, active_ingredients FROM medicines WHERE user_id = ?", [user_id])
        safety_notice = None
        for pm in patient_meds:
            if pm["name"].lower() in (db_match["known_interactions"].lower() if db_match and db_match["known_interactions"] else ""):
                safety_notice = f"Potential interaction detected with your active medicine: {pm['name']}. Consult doctor before taking together."

        # Check allergy against patient profile
        profile = query_db("SELECT allergies FROM patient_profiles WHERE user_id = ?", [user_id], one=True)
        allergy_warning = None
        if profile and profile["allergies"]:
            user_allergies = [a.strip().lower() for a in profile["allergies"].split(",") if a.strip()]
            for ua in user_allergies:
                if ua in med_name.lower() or ua in generic_name.lower():
                    allergy_warning = f"CRITICAL ALLERGY ALERT: This medicine matches your documented allergy to '{ua}'!"

        result = {
            "name": med_name,
            "generic_name": generic_name,
            "dosage": dosage,
            "form": form,
            "manufacturing_date": mfg_date,
            "expiry_date": exp_date,
            "before_after_food": before_after_food,
            "common_uses": common_uses,
            "side_effects": side_effects,
            "warnings": warnings,
            "safety_notice": safety_notice,
            "allergy_warning": allergy_warning,
            "analysis_source": fields.get("analysis_source", "smart_nlp"),
            "analysis_notice": fields.get("analysis_notice", ""),
            "image_path": relative_path,
            "raw_ocr": raw_ocr
        }

        # Generate natural spoken scripts across 9 Indian languages
        voice_scripts = generate_medicine_voice_scripts(result)
        result["voice_scripts"] = voice_scripts
        result["voice_scripts_json"] = json.dumps(voice_scripts)
        result["languages"] = LANGUAGES

    return render_template("medicine_scanner.html", result=result, languages=LANGUAGES)


@scanner_bp.route("/voice", methods=["POST"])
@role_required('patient')
def get_voice_script():
    """Returns synthesized spoken text for the chosen Indian language."""
    data = request.get_json() or {}
    scripts = generate_medicine_voice_scripts(data)
    lang = data.get("language", "en")
    selected = scripts.get(lang) or scripts.get("en")
    return jsonify({
        "language": lang,
        "locale": selected["locale"],
        "name": selected["name"],
        "text": selected["text"],
        "all_scripts": scripts
    })


@scanner_bp.route("/audio")
def stream_tts_audio():
    """
    Universal streaming audio endpoint:
    Streams natural spoken audio MP3 in 9 Indian languages.
    Plays natively in any mobile browser, WebView, or desktop without Web Speech API.
    """
    import urllib.parse
    import requests

    lang = request.args.get("lang", "en").strip().lower()
    text = request.args.get("text", "").strip()

    if not text:
        return "Missing text parameter", 400

    lang_map = {
        "en": "en",
        "hi": "hi",
        "ta": "ta",
        "te": "te",
        "bn": "bn",
        "mr": "mr",
        "gu": "gu",
        "kn": "kn",
        "ml": "ml"
    }
    tts_lang = lang_map.get(lang, "en")

    import re
    # Clean up symbols that break Google TTS
    cleaned = re.sub(r'[\+\(\)\*\#_:]', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Split text into chunks <= 80 chars on sentence or word boundaries
    parts = re.split(r'([.।\n!?])', cleaned)
    sentences = []
    curr = ''
    for p in parts:
        if p in '.।\n!?':
            curr += p
            if curr.strip():
                sentences.append(curr.strip())
            curr = ''
        else:
            curr += p
    if curr.strip():
        sentences.append(curr.strip())

    chunks = []
    for s in sentences:
        if len(s) > 80:
            words = s.split()
            sub = ''
            for w in words:
                if len(sub) + len(w) + 1 <= 80:
                    sub = (sub + ' ' + w).strip()
                else:
                    if sub:
                        chunks.append(sub)
                    sub = w
            if sub:
                chunks.append(sub)
        else:
            chunks.append(s)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    audio_bytes = b''
    for ch in chunks[:6]:
        ch_clean = ch.strip()
        if not ch_clean:
            continue
        try:
            encoded_text = urllib.parse.quote(ch_clean)
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl={tts_lang}&q={encoded_text}"
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200 and len(resp.content) > 100:
                audio_bytes += resp.content
        except Exception:
            continue

    if audio_bytes:
        return Response(audio_bytes, mimetype="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})

    return "Audio generation failed", 502


@scanner_bp.route("/medicine/add", methods=["POST"])
@role_required('patient')
def add_scanned_medicine():
    """Patient confirms scanned medicine strip and saves it into medicine cabinet."""
    user_id = session["user_id"]
    name = request.form.get("name", "").strip()
    generic_name = request.form.get("generic_name", "").strip()
    dosage = request.form.get("dosage", "").strip()
    form = request.form.get("form", "Tablet").strip()
    expiry_date = request.form.get("expiry_date", "").strip() or None
    before_after_food = request.form.get("before_after_food", "").strip()
    purpose = request.form.get("purpose", "").strip()
    warnings = request.form.get("warnings", "").strip()
    quantity = request.form.get("quantity", type=int) or 10

    if not name:
        flash("Medicine name is required.", "error")
        return redirect(url_for("scanner.medicine_scan"))

    active_ingredients = json.dumps([generic_name] if generic_name else [name])
    execute_db(
        """INSERT INTO medicines 
           (user_id, name, generic_name, dosage, form, active_ingredients, purpose, warnings, 
            expiry_date, quantity, source, verified, before_after_food)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'scan', 1, ?)""",
        [user_id, name, generic_name, dosage, form, active_ingredients, purpose, warnings, expiry_date, quantity, before_after_food]
    )

    # Re-evaluate patient safety alerts
    run_safety_checks(user_id)

    flash(f"'{name}' successfully confirmed and added to your Medicine Cabinet!", "success")
    return redirect(url_for("medicines.index"))


# ==============================================================
# 2. Prescription Scanner (PDF / Image -> Doctor Routing)
# ==============================================================
@scanner_bp.route("", methods=["GET", "POST"])
@role_required('patient')
def scan():
    """Upload prescription image or PDF for AI handwriting/text OCR and doctor review."""
    if request.method == "POST":
        image = request.files.get("image")
        if not image or not image.filename:
            flash("Choose a prescription image or document to scan.", "error")
            return render_template("scanner.html")
        if not _allowed_file(image.filename):
            flash("Unsupported file format. Please upload PNG, JPG, JPEG, WEBP, or PDF.", "error")
            return render_template("scanner.html")

        filename = f"rx_{uuid.uuid4().hex}_{secure_filename(image.filename)}"
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)
        relative_path = os.path.relpath(image_path, current_app.root_path)
        raw_ocr_text, fields = _analyze_image(image_path)

        prescription_id = execute_db(
            """INSERT INTO prescriptions
               (user_id, image_path, raw_ocr_text, extracted_data, status)
               VALUES (?, ?, ?, ?, 'uploaded')""",
            [
                session["user_id"],
                relative_path,
                raw_ocr_text,
                json.dumps(fields),
            ],
        )
        return redirect(url_for("scanner.confirm", prescription_id=prescription_id))

    return render_template("scanner.html")


@scanner_bp.route("/<int:prescription_id>/confirm", methods=["GET", "POST"])
@role_required('patient')
def confirm(prescription_id):
    """Let the patient review and verify AI-extracted prescription before routing to doctor."""
    prescription = query_db(
        "SELECT * FROM prescriptions WHERE id = ? AND user_id = ?",
        [prescription_id, session["user_id"]],
        one=True,
    )
    if not prescription:
        flash("That scan could not be found.", "error")
        return redirect(url_for("scanner.scan"))

    fields = json.loads(prescription["extracted_data"] or "{}")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Please enter or confirm at least one medicine name.", "error")
            return render_template("scanner.html", prescription=prescription, fields=fields)

        medicines_list = fields.get("medicines") or []
        if not medicines_list:
            medicines_list = [
                {
                    "name": name,
                    "dosage": request.form.get("dosage", "").strip(),
                    "frequency": request.form.get("frequency", "").strip(),
                    "instructions": request.form.get("prescription_instructions", "").strip()
                }
            ]

        confirmed_fields = {
            "name": name,
            "generic_name": request.form.get("generic_name", "").strip(),
            "dosage": request.form.get("dosage", "").strip(),
            "form": request.form.get("form", "").strip(),
            "doctor_name": request.form.get("doctor_name", "").strip(),
            "prescription_date": request.form.get("prescription_date", "").strip(),
            "frequency": request.form.get("frequency", "").strip(),
            "prescription_instructions": request.form.get("prescription_instructions", "").strip(),
            "medicines": medicines_list
        }

        # Auto-assign to verified doctor if available
        doc = query_db("SELECT user_id FROM doctor_profiles WHERE verification_status='verified' LIMIT 1", one=True)
        assigned_doc_id = doc["user_id"] if doc else None
        target_status = 'under_review' if assigned_doc_id else 'pending_doctor_assignment'

        execute_db(
            """UPDATE prescriptions 
               SET extracted_data = ?, verified = 1, status = ?, 
                   assigned_doctor_id = ?, patient_confirmed_at = CURRENT_TIMESTAMP
               WHERE id = ? AND user_id = ?""",
            [json.dumps(confirmed_fields), target_status, assigned_doc_id, prescription_id, session["user_id"]],
        )

        flash("Prescription confirmed! It has been forwarded to the verified doctor for clinical review and schedule approval.", "success")
        return redirect(url_for("prescriptions.index"))

    return render_template("scanner.html", prescription=prescription, fields=fields)
