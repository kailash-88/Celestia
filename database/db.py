"""
MediMitra Database Module
Handles SQLite connection, initialization, and query helpers.
"""

import sqlite3
import os

DATABASE_PATH = None


def get_db_path():
    """Get the database file path."""
    global DATABASE_PATH
    if DATABASE_PATH is None:
        DATABASE_PATH = os.getenv('DATABASE_PATH', 'medimitra.db')
    return DATABASE_PATH


def set_db_path(path):
    """Set the database file path (called from app.py)."""
    global DATABASE_PATH
    DATABASE_PATH = path


def get_connection():
    """Create and return a new database connection."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Return rows as dicts
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database by running schema.sql."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    conn = get_connection()
    try:
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        # Add workflow fields to existing prototype databases without discarding user data.
        existing = {row[1] for row in conn.execute("PRAGMA table_info(prescriptions)").fetchall()}
        for name, definition in (
            ("status", "TEXT NOT NULL DEFAULT 'uploaded'"),
            ("assigned_doctor_id", "INTEGER"),
            ("patient_confirmed_at", "TIMESTAMP"),
            ("approved_at", "TIMESTAMP"),
        ):
            if name not in existing:
                conn.execute(f"ALTER TABLE prescriptions ADD COLUMN {name} {definition}")
        medicine_columns = {row[1] for row in conn.execute("PRAGMA table_info(medicines)").fetchall()}
        for name, definition in (("prescription_id", "INTEGER"), ("batch_number", "TEXT"), ("manufacturing_date", "DATE")):
            if name not in medicine_columns:
                conn.execute(f"ALTER TABLE medicines ADD COLUMN {name} {definition}")
        conn.commit()

        # Ensure core demo users always exist (Render, local, Docker)
        try:
            from werkzeug.security import generate_password_hash
            pw_hash = generate_password_hash("password123")

            p = conn.execute("SELECT id FROM users WHERE username = 'patient_demo'").fetchone()
            if not p:
                conn.execute(
                    "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, 'patient')",
                    ("patient_demo", "patient@example.com", pw_hash, "Ramesh Sharma")
                )
                pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.execute(
                    """INSERT OR IGNORE INTO patient_profiles 
                       (user_id, age, gender, blood_group, allergies, conditions, emergency_contact_name, emergency_contact_phone)
                       VALUES (?, 64, 'Male', 'B+', 'Penicillin', 'Type 2 Diabetes, Hypertension', 'Priya Sharma (Daughter)', '+91 98765 43211')""",
                    (pid,)
                )
            else:
                pid = p[0]

            d = conn.execute("SELECT id FROM users WHERE username = 'doctor_demo'").fetchone()
            if not d:
                conn.execute(
                    "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, 'doctor')",
                    ("doctor_demo", "doctor@example.com", pw_hash, "Dr. Ananya Roy")
                )
                did = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.execute(
                    """INSERT OR IGNORE INTO doctor_profiles 
                       (user_id, specialty, license_number, qualifications, verification_status)
                       VALUES (?, 'Cardiology & Internal Medicine', 'MCI-2018-847291', 'MBBS, MD, DM', 'verified')""",
                    (did,)
                )

            a = conn.execute("SELECT id FROM users WHERE username = 'admin_demo'").fetchone()
            if not a:
                conn.execute(
                    "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, 'admin')",
                    ("admin_demo", "admin@example.com", pw_hash, "MediMitra Administrator")
                )

            c = conn.execute("SELECT id FROM users WHERE username = 'caregiver_demo'").fetchone()
            if not c:
                conn.execute(
                    "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, 'caregiver')",
                    ("caregiver_demo", "caregiver@example.com", pw_hash, "Priya Sharma")
                )

            # Ensure patient_demo has sample schedule so dashboard loads with full stats
            med_cnt = conn.execute("SELECT COUNT(*) FROM medicines WHERE user_id = ?", (pid,)).fetchone()[0]
            if med_cnt == 0:
                conn.execute(
                    """INSERT INTO medicines (user_id, name, generic_name, dosage, form, frequency, instructions, quantity, verified)
                       VALUES (?, 'Metformin 500', 'Metformin Hydrochloride', '500mg', 'Tablet', '1-0-1', 'Take after food with water', 30, 1)""",
                    (pid,)
                )
                m1_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.execute(
                    """INSERT INTO schedules (user_id, medicine_id, scheduled_time, time_of_day, dosage_amount, instructions)
                       VALUES (?, ?, '08:00', 'morning', '1 Tablet', 'Take after breakfast')""",
                    (pid, m1_id)
                )

            conn.commit()
        except Exception as ue:
            print(f"[DB] Demo user init notice: {ue}")

        print("[DB] Database initialized successfully.")
    except Exception as e:
        print(f"[DB] Error initializing database: {e}")
        raise
    finally:
        conn.close()


def query_db(query, args=(), one=False):
    """Execute a SELECT query and return results."""
    conn = get_connection()
    try:
        cur = conn.execute(query, args)
        results = cur.fetchall()
        return (results[0] if results else None) if one else results
    finally:
        conn.close()


def execute_db(query, args=()):
    """Execute an INSERT/UPDATE/DELETE query and return lastrowid."""
    conn = get_connection()
    try:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
