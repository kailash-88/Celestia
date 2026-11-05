"""
Unit tests for authentication and user management in MediMitra.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.db import init_db, set_db_path, execute_db, query_db
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    set_db_path(db_path)

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass


def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign In" in response.data or b"Login" in response.data or b"login" in response.data


def test_register_and_login_flow(client):
    # Register a new patient
    reg_response = client.post("/register", data={
        "username": "tester1",
        "email": "tester1@example.com",
        "full_name": "Test User",
        "password": "securepassword123",
        "confirm": "securepassword123",
        "role": "patient",
    }, follow_redirects=True)
    assert reg_response.status_code == 200

    # User should now be in DB
    user = query_db("SELECT * FROM users WHERE username = ?", ["tester1"], one=True)
    assert user is not None
    assert user["full_name"] == "Test User"

    # Login with valid credentials
    login_response = client.post("/login", data={
        "username": "tester1",
        "password": "securepassword123",
    }, follow_redirects=True)
    assert login_response.status_code == 200
    assert b"Test User" in login_response.data or b"Dashboard" in login_response.data


def test_login_invalid_password(client):
    execute_db(
        "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)",
        ["tester2", "tester2@example.com", generate_password_hash("correctpass"), "Tester Two", "patient"]
    )
    res = client.post("/login", data={
        "username": "tester2",
        "password": "wrongpassword",
    }, follow_redirects=True)
    assert b"Invalid username or password" in res.data


def test_unauthenticated_dashboard_redirect(client):
    res = client.get("/dashboard")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]
