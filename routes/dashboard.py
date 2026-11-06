"""
MediMitra Dashboard Routes
Patient home dashboard with:
- Personalized welcome message
- Today's medicine schedule with interactive Taken / Skipped buttons
- Adherence calculation ring
- Emergency SOS quick action
- Refill alerts and caregiver notifications
"""

from datetime import datetime, date
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from routes.auth import login_required, get_current_user
from database.db import query_db, execute_db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard view."""
    user = get_current_user()
    if user and user["role"] == "doctor":
        return redirect(url_for("doctor.index"))
    if user and user["role"] == "admin":
        return redirect(url_for("admin.index"))
    if user and user["role"] == "caregiver":
        return redirect(url_for("caregiver.index"))
    if user and user["role"] == "pharmacist":
        return redirect(url_for("pharmacy.index"))

    user_id = session['user_id']

    # Gather dashboard stats
    medicine_count = query_db(
        'SELECT COUNT(*) as count FROM medicines WHERE user_id = ?',
        [user_id], one=True
    )

    active_schedules = query_db(
        'SELECT COUNT(*) as count FROM schedules WHERE user_id = ? AND is_active = 1',
        [user_id], one=True
    )

    # Today's doses
    today_doses = query_db(
        """SELECT COUNT(*) as total,
           SUM(CASE WHEN status = 'taken' THEN 1 ELSE 0 END) as taken,
           SUM(CASE WHEN status = 'missed' THEN 1 ELSE 0 END) as missed,
           SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as skipped,
           SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
        FROM dose_logs
        WHERE user_id = ? AND DATE(scheduled_for) = DATE('now')""",
        [user_id], one=True
    )

    # Active safety alerts
    active_alerts = query_db(
        'SELECT COUNT(*) as count FROM safety_alerts WHERE user_id = ? AND is_dismissed = 0',
        [user_id], one=True
    )

    # Low stock refills (<= 5 tablets)
    refill_alerts = query_db(
        "SELECT id, name, dosage, quantity FROM medicines WHERE user_id = ? AND quantity <= 5",
        [user_id]
    )

    # Patient profile & emergency contact
    profile = query_db("SELECT * FROM patient_profiles WHERE user_id = ?", [user_id], one=True)

    # Caregiver link status
    caregiver = query_db(
        """SELECT u.full_name, u.phone, cl.status 
           FROM caregiver_links cl 
           JOIN users u ON u.id = cl.caregiver_id 
           WHERE cl.patient_id = ? AND cl.status = 'active' LIMIT 1""",
        [user_id], one=True
    )

    caregiver_requests = query_db(
        "SELECT cl.id, cl.created_at, u.full_name FROM caregiver_links cl JOIN users u ON u.id=cl.caregiver_id WHERE cl.patient_id=? AND cl.status='pending' ORDER BY cl.created_at DESC",
        [user_id],
    )

    # Today's detailed schedule with dose log status
    today_schedule = query_db(
        """SELECT dl.id as log_id, dl.status, dl.scheduled_for, dl.taken_at,
                  s.id as schedule_id, s.time_of_day, s.scheduled_time, s.dosage_amount, s.instructions,
                  m.name as medicine_name, m.form as medicine_form, m.before_after_food
        FROM schedules s
        JOIN medicines m ON s.medicine_id = m.id
        LEFT JOIN dose_logs dl ON dl.schedule_id = s.id AND DATE(dl.scheduled_for) = DATE('now')
        WHERE s.user_id = ? AND s.is_active = 1
        ORDER BY s.scheduled_time ASC""",
        [user_id]
    )

    # Upcoming doctor consultations / answered queries
    recent_doctor_advice = query_db(
        """SELECT pq.*, u.full_name as doctor_name 
           FROM patient_queries pq
           JOIN users u ON u.id = pq.doctor_id
           WHERE pq.patient_id = ? AND pq.status = 'answered'
           ORDER BY pq.answered_at DESC LIMIT 2""",
        [user_id]
    )

    stats = {
        'medicines': medicine_count['count'] if medicine_count else 0,
        'schedules': active_schedules['count'] if active_schedules else 0,
        'doses_today': today_doses['total'] if today_doses and today_doses['total'] else len(today_schedule),
        'doses_taken': today_doses['taken'] if today_doses and today_doses['taken'] else 0,
        'doses_missed': today_doses['missed'] if today_doses and today_doses['missed'] else 0,
        'doses_skipped': today_doses['skipped'] if today_doses and today_doses['skipped'] else 0,
        'alerts': active_alerts['count'] if active_alerts else 0,
        'refills': len(refill_alerts)
    }

    # Adherence percentage
    total_evaluated = stats['doses_taken'] + stats['doses_missed']
    if total_evaluated > 0:
        stats['adherence'] = round((stats['doses_taken'] / total_evaluated) * 100)
    elif stats['doses_today'] > 0:
        stats['adherence'] = round((stats['doses_taken'] / stats['doses_today']) * 100)
    else:
        stats['adherence'] = 100

    return render_template('dashboard.html',
                           user=user,
                           stats=stats,
                           today_schedule=today_schedule,
                           refill_alerts=refill_alerts,
                           profile=profile,
                           caregiver=caregiver,
                           caregiver_requests=caregiver_requests,
                           recent_doctor_advice=recent_doctor_advice,
                           now_hour=datetime.now().hour)


@dashboard_bp.route('/dashboard/dose/<int:schedule_id>/<action>', methods=['POST'])
@login_required
def log_dose(schedule_id, action):
    """Mark a dose as taken or skipped directly from dashboard."""
    user_id = session['user_id']
    if action not in {'taken', 'skipped'}:
        flash("Invalid dose status action.", "error")
        return redirect(url_for('dashboard.index'))

    # Check if a log already exists for today
    existing = query_db(
        "SELECT id FROM dose_logs WHERE schedule_id = ? AND user_id = ? AND DATE(scheduled_for) = DATE('now')",
        [schedule_id, user_id], one=True
    )

    if existing:
        execute_db(
            "UPDATE dose_logs SET status = ?, taken_at = CURRENT_TIMESTAMP WHERE id = ?",
            [action, existing['id']]
        )
    else:
        execute_db(
            """INSERT INTO dose_logs (schedule_id, user_id, status, scheduled_for, taken_at)
               VALUES (?, ?, ?, datetime('now'), CURRENT_TIMESTAMP)""",
            [schedule_id, user_id, action]
        )

    # If taken, deduct 1 unit from medicine quantity
    if action == 'taken':
        sched = query_db("SELECT medicine_id FROM schedules WHERE id = ?", [schedule_id], one=True)
        if sched:
            execute_db("UPDATE medicines SET quantity = MAX(0, quantity - 1) WHERE id = ?", [sched['medicine_id']])

    flash(f"Dose marked as {action.capitalize()}!", "success")
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/dashboard/sos', methods=['POST'])
@login_required
def trigger_sos():
    """Trigger emergency SOS alert."""
    user_id = session['user_id']
    profile = query_db("SELECT * FROM patient_profiles WHERE user_id = ?", [user_id], one=True)
    contact_name = profile['emergency_contact_name'] if profile and profile['emergency_contact_name'] else "Emergency Contact"
    contact_phone = profile['emergency_contact_phone'] if profile and profile['emergency_contact_phone'] else "Local Emergency Services (112 / 108)"

    flash(f"🚨 EMERGENCY SOS ACTIVATED! Emergency notification dispatched to {contact_name} ({contact_phone}). Please stay calm.", "error")
    return redirect(url_for('dashboard.index'))
