"""
MediMitra Authentication Routes
Handles login, registration, and logout.
"""

from flask import Blueprint, request, render_template, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database.db import query_db, execute_db

auth_bp = Blueprint('auth', __name__)


# --- Decorators ---

def login_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Restrict a route to the listed account roles after authentication."""
    def decorate(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to continue.', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('role') not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorate


def get_current_user():
    """Get the currently logged-in user from the database."""
    if 'user_id' in session:
        return query_db('SELECT * FROM users WHERE id = ?', [session['user_id']], one=True)
    return None


# --- Routes ---

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
        specialty = request.form.get('specialty', '').strip()
        license_number = request.form.get('license_number', '').strip()
        qualifications = request.form.get('qualifications', '').strip()

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
            'INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)',
            [username, email, password_hash, full_name, role]
        )
        if role == 'doctor':
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

            if not full_name:
                flash('Full name cannot be empty.', 'error')
            else:
                execute_db('UPDATE users SET full_name = ?, phone = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                           [full_name, phone, user['id']])
                session['full_name'] = full_name
                flash('Profile updated successfully.', 'success')

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
