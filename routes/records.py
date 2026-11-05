"""
MediMitra Health Records
Provides patient health timeline, medical conditions, allergies,
emergency contacts, and exportable medical history report.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import role_required, get_current_user
from database.db import query_db, execute_db

records_bp = Blueprint('records', __name__, url_prefix='/records')


@records_bp.route('', methods=['GET', 'POST'])
@role_required('patient')
def index():
    user_id = session['user_id']

    if request.method == 'POST':
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        allergies = request.form.get('allergies', '').strip()
        conditions = request.form.get('conditions', '').strip()
        contact_name = request.form.get('emergency_contact_name', '').strip()
        contact_phone = request.form.get('emergency_contact_phone', '').strip()
        contact_relation = request.form.get('emergency_contact_relation', '').strip()

        # Update or insert into patient_profiles
        existing = query_db("SELECT user_id FROM patient_profiles WHERE user_id = ?", [user_id], one=True)
        if existing:
            execute_db(
                """UPDATE patient_profiles 
                   SET age=?, gender=?, blood_group=?, allergies=?, conditions=?, 
                       emergency_contact_name=?, emergency_contact_phone=?, emergency_contact_relation=?
                   WHERE user_id=?""",
                [age, gender, blood_group, allergies, conditions, contact_name, contact_phone, contact_relation, user_id]
            )
        else:
            execute_db(
                """INSERT INTO patient_profiles 
                   (user_id, age, gender, blood_group, allergies, conditions, emergency_contact_name, emergency_contact_phone, emergency_contact_relation)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [user_id, age, gender, blood_group, allergies, conditions, contact_name, contact_phone, contact_relation]
            )
        flash('Health profile and emergency contact updated successfully.', 'success')
        return redirect(url_for('records.index'))

    # GET: Load profile, medicines, prescriptions, consultations
    profile = query_db("SELECT * FROM patient_profiles WHERE user_id = ?", [user_id], one=True)
    medicines = query_db("SELECT * FROM medicines WHERE user_id = ? ORDER BY created_at DESC", [user_id])
    prescriptions = query_db("SELECT * FROM prescriptions WHERE user_id = ? ORDER BY scan_date DESC", [user_id])
    consultations = query_db(
        """SELECT pq.*, u.full_name AS doctor_name 
           FROM patient_queries pq
           LEFT JOIN users u ON u.id = pq.doctor_id
           WHERE pq.patient_id = ? AND pq.status = 'answered'
           ORDER BY pq.answered_at DESC""",
        [user_id]
    )

    return render_template(
        'health_records.html',
        profile=profile,
        medicines=medicines,
        prescriptions=prescriptions,
        consultations=consultations
    )
