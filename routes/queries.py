"""
MediMitra Patient Health Queries
Handles communication between patients and their assigned doctors,
including query submissions, image attachments, and AI escalation.
"""

import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, abort
from werkzeug.utils import secure_filename
from routes.auth import role_required, get_current_user
from database.db import query_db, execute_db

queries_bp = Blueprint('queries', __name__, url_prefix='/queries')


@queries_bp.route('', methods=['GET', 'POST'])
@role_required('patient')
def patient_queries():
    user_id = session['user_id']
    
    # Check if form was submitted
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        question = request.form.get('question', '').strip()
        doctor_id = request.form.get('doctor_id', type=int)

        if not subject or not question:
            flash('Please provide both a subject and your question.', 'error')
            return redirect(url_for('queries.patient_queries'))

        # Handle image attachment if uploaded
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    filename = f"query_{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_path = filepath

        # If no specific doctor was selected, assign the first verified doctor or doctor assigned to patient's prescription
        if not doctor_id:
            assigned = query_db(
                "SELECT assigned_doctor_id FROM prescriptions WHERE user_id=? AND assigned_doctor_id IS NOT NULL ORDER BY approved_at DESC LIMIT 1",
                [user_id], one=True
            )
            if assigned and assigned['assigned_doctor_id']:
                doctor_id = assigned['assigned_doctor_id']
            else:
                first_doc = query_db("SELECT user_id FROM doctor_profiles WHERE verification_status='verified' LIMIT 1", one=True)
                doctor_id = first_doc['user_id'] if first_doc else None

        execute_db(
            """INSERT INTO patient_queries (patient_id, doctor_id, subject, question, image_path, status)
               VALUES (?, ?, ?, ?, ?, 'pending')""",
            [user_id, doctor_id, subject, question, image_path]
        )

        flash('Your health query has been submitted to the doctor for review.', 'success')
        return redirect(url_for('queries.patient_queries'))

    # GET: List all queries for current patient
    queries = query_db(
        """SELECT pq.*, u.full_name AS doctor_name, dp.specialty
           FROM patient_queries pq
           LEFT JOIN users u ON u.id = pq.doctor_id
           LEFT JOIN doctor_profiles dp ON dp.user_id = pq.doctor_id
           WHERE pq.patient_id = ?
           ORDER BY pq.created_at DESC""",
        [user_id]
    )

    doctors = query_db(
        """SELECT u.id, u.full_name, dp.specialty
           FROM users u
           JOIN doctor_profiles dp ON dp.user_id = u.id
           WHERE dp.verification_status = 'verified'
           ORDER BY u.full_name"""
    )

    return render_template('patient_queries.html', queries=queries, doctors=doctors)
