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

        user_columns = {row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
        for name, definition in (("language", "TEXT DEFAULT 'en'"), ("auto_camera", "INTEGER DEFAULT 1")):
            if name not in user_columns:
                conn.execute(f"ALTER TABLE users ADD COLUMN {name} {definition}")

        conn.commit()

        # Seed comprehensive Indian medicine database if needed
        cur = conn.execute("SELECT COUNT(*) FROM medicine_database")
        med_count = cur.fetchone()[0]
        if med_count < 170:
            try:
                from database.seed_indian_medicines import seed_indian_medicines
                seed_indian_medicines(get_db_path())
            except Exception as se:
                print(f"[DB] Supplemental medicine seeding skipped/deferred: {se}")

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
