"""
MediMitra Authentication & Settings Routes
Handles user registration, login, logout, role validation,
language preferences (English, Hindi, Tamil), and auto-camera settings.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db, execute_db

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator to require specific role(s) for a route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            user = get_current_user()
            if not user or user['role'] not in roles:
                flash('Camera scanning and access are reserved exclusively for Patient accounts.', 'error')
                if user and user['role'] == 'doctor':
                    return redirect(url_for('doctor.index'))
                if user and user['role'] == 'admin':
                    return redirect(url_for('admin.index'))
                if user and user['role'] == 'caregiver':
                    return redirect(url_for('caregiver.index'))
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user():
    """Get the currently logged-in user from database."""
    if 'user_id' not in session:
        return None
    if not hasattr(g, 'current_user'):
        g.current_user = query_db(
            'SELECT * FROM users WHERE id = ?',
            [session['user_id']], one=True
        )
    return g.current_user


@auth_bp.route('/')
def landing():
    """Public product landing page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('landing.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')

        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session['language'] = user['language'] if ('language' in user.keys() and user['language']) else 'en'
            session['auto_camera'] = user['auto_camera'] if ('auto_camera' in user.keys() and user['auto_camera'] is not None) else 1
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        role = request.form.get('role', 'patient')
        language = request.form.get('language', 'en')
        specialty = request.form.get('specialty', '').strip()
        license_number = request.form.get('license_number', '').strip()
        qualifications = request.form.get('qualifications', '').strip()

        if language not in ('en', 'hi', 'ta'):
            language = 'en'

        # Validation
        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('A valid email is required.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        pharmacy_name = request.form.get('pharmacy_name', '').strip()
        pharmacy_license = request.form.get('pharmacy_license', '').strip()
        if role not in ('patient', 'caregiver', 'doctor', 'pharmacist'):
            errors.append('Invalid role selected.')
        if role == 'doctor' and (not specialty or not license_number):
            errors.append('Doctors must provide a specialty and professional registration number.')
        if role == 'pharmacist' and (not pharmacy_name or not pharmacy_license):
            errors.append('Pharmacists must provide a pharmacy name and registration number.')

        # Check duplicates
        if not errors:
            existing = query_db('SELECT id FROM users WHERE username = ? OR email = ?',
                                [username, email], one=True)
            if existing:
                errors.append('Username or email already exists.')

        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template('register.html')

        # Create user
        password_hash = generate_password_hash(password)
        account_id = execute_db(
            'INSERT INTO users (username, email, password_hash, full_name, role, language, auto_camera) VALUES (?, ?, ?, ?, ?, ?, 1)',
            [username, email, password_hash, full_name, role, language]
        )
        if role == 'patient':
            execute_db('INSERT OR IGNORE INTO patient_profiles (user_id) VALUES (?)', [account_id])
        elif role == 'doctor':
            execute_db(
                'INSERT INTO doctor_profiles (user_id, specialty, license_number, qualifications) VALUES (?, ?, ?, ?)',
                [account_id, specialty, license_number, qualifications or None]
            )
        elif role == 'pharmacist':
            execute_db(
                'INSERT INTO pharmacy_profiles (user_id, pharmacy_name, license_number) VALUES (?, ?, ?)',
                [account_id, pharmacy_name, pharmacy_license]
            )
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/set-language/<lang>', methods=['GET', 'POST'])
def set_language(lang):
    """Switch language (en: English, hi: Hindi, ta: Tamil)."""
    if lang in ('en', 'hi', 'ta'):
        session['language'] = lang
        if 'user_id' in session:
            execute_db('UPDATE users SET language = ? WHERE id = ?', [lang, session['user_id']])
        lang_names = {'en': 'English', 'hi': 'हिन्दी (Hindi)', 'ta': 'தமிழ் (Tamil)'}
        flash(f'Language updated to {lang_names.get(lang, lang)}.', 'info')

    next_url = request.referrer or url_for('dashboard.index')
    return redirect(next_url)


@auth_bp.route('/set-auto-camera', methods=['POST'])
@login_required
def set_auto_camera():
    """Toggle auto-open camera on launch preference."""
    data = request.get_json() or {}
    enabled = 1 if data.get('enabled') else 0
    session['auto_camera'] = enabled
    execute_db('UPDATE users SET auto_camera = ? WHERE id = ?', [enabled, session['user_id']])
    return jsonify({'status': 'success', 'auto_camera': enabled})


@auth_bp.route('/logout')
def logout():
    """Log the user out."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Manage profile and account settings."""
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'profile':
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip() or None
            language = request.form.get('language', 'en')
            auto_cam = 1 if request.form.get('auto_camera') == '1' else 0

            if language not in ('en', 'hi', 'ta'):
                language = 'en'

            if not full_name:
                flash('Full name cannot be empty.', 'error')
            else:
                execute_db(
                    'UPDATE users SET full_name = ?, phone = ?, language = ?, auto_camera = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    [full_name, phone, language, auto_cam, user['id']]
                )
                session['full_name'] = full_name
                session['language'] = language
                session['auto_camera'] = auto_cam
                flash('Profile and preferences updated successfully.', 'success')

        elif action == 'password':
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not check_password_hash(user['password_hash'], old_password):
                flash('Current password is incorrect.', 'error')
            elif len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'error')
            else:
                new_hash = generate_password_hash(new_password)
                execute_db('UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                           [new_hash, user['id']])
                flash('Password changed successfully.', 'success')

        return redirect(url_for('auth.settings'))

    return render_template('settings.html', user=user)
