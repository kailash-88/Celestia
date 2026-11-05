"""End-to-end smoke test for patient confirmation and verified doctor approval."""
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image


class PrescriptionWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.dirname(__file__)))
        os.environ["DATABASE_PATH"] = os.path.join(self.tempdir.name, "workflow.sqlite")
        os.environ["VISION_API_KEY"] = ""
        from app import create_app
        from database.db import execute_db
        from werkzeug.security import generate_password_hash
        self.execute_db = execute_db
        self.app = create_app()
        self.app.config.update(TESTING=True, UPLOAD_FOLDER=self.tempdir.name)
        self.client = self.app.test_client()
        self._register("patient_one", "patient@example.test", "patient")
        self._register("doctor_one", "doctor@example.test", "doctor", specialty="General Medicine", license_number="REG-TEST-001")
        self.execute_db(
            "INSERT INTO users (username,email,password_hash,full_name,role) VALUES (?,?,?,?, 'admin')",
            ["admin_one", "admin@example.test", generate_password_hash("test-password-123"), "Test Admin"],
        )

    def tearDown(self):
        self.client = None
        self.tempdir.cleanup()

    def _register(self, username, email, role, **extra):
        data = {
            "full_name": username.title(), "username": username, "email": email,
            "password": "test-password-123", "confirm_password": "test-password-123", "role": role,
        }
        data.update(extra)
        response = self.client.post("/register", data=data)
        self.assertEqual(response.status_code, 302)

    def _login(self, username):
        return self.client.post("/login", data={"username": username, "password": "test-password-123"})

    def test_confirm_assign_approve_and_patient_tracking(self):
        from database.db import query_db

        self._login("patient_one")
        image = Image.new("RGB", (320, 180), "white")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        uploaded = self.client.post(
            "/scanner", data={"image": (io.BytesIO(buffer.getvalue()), "label.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(uploaded.status_code, 302)
        prescription_id = query_db("SELECT MAX(id) AS id FROM prescriptions", one=True)["id"]
        extraction_review = self.client.get(f"/scanner/{prescription_id}/confirm")
        self.assertEqual(extraction_review.status_code, 200)
        self.assertIn(b"AI and OCR suggestions", extraction_review.data)
        refreshed = self.client.post(f"/scanner/{prescription_id}/confirm", data={"reanalyze": "yes"}, follow_redirects=True)
        self.assertIn(b"Analysis refreshed", refreshed.data)
        confirmed = self.client.post(f"/scanner/{prescription_id}/confirm", data={
            "name": "Example Medicine", "generic_name": "Example ingredient",
            "active_ingredient": "Example ingredient", "dosage": "10 mg", "form": "tablet",
            "purpose": "", "expiry_date": "", "prescription_instructions": "Take as prescribed",
            "confirm_details": "yes",
        })
        self.assertEqual(confirmed.status_code, 302)
        status = query_db("SELECT status FROM prescriptions WHERE id=?", [prescription_id], one=True)["status"]
        self.assertEqual(status, "pending_doctor_assignment")

        self.client.get("/logout")
        self._login("admin_one")
        doctor_id = query_db("SELECT id FROM users WHERE username='doctor_one'", one=True)["id"]
        verified = self.client.post(f"/admin/doctors/{doctor_id}/verify", data={"status": "verified"})
        self.assertEqual(verified.status_code, 302)
        assigned = self.client.post(f"/admin/prescriptions/{prescription_id}/assign", data={"doctor_id": str(doctor_id)})
        self.assertEqual(assigned.status_code, 302)
        self.client.get("/logout")

        self._login("doctor_one")
        doctor_page = self.client.get(f"/doctor/prescriptions/{prescription_id}")
        self.assertEqual(doctor_page.status_code, 200)
        self.assertIn(b"Original patient prescription", doctor_page.data)
        review = self.client.post(f"/doctor/prescriptions/{prescription_id}", data={
            "action": "approve", "name": "Example Medicine", "generic_name": "Example ingredient",
            "active_ingredient": "Example ingredient", "dosage": "10 mg", "form": "tablet",
            "purpose": "", "expiry_date": "", "prescription_instructions": "Take as prescribed",
        })
        self.assertEqual(review.status_code, 302)
        status = query_db("SELECT status FROM prescriptions WHERE id=?", [prescription_id], one=True)["status"]
        self.assertEqual(status, "approved")
        medicine = query_db("SELECT name,verified,prescription_id FROM medicines WHERE prescription_id=?", [prescription_id], one=True)
        self.assertEqual(medicine["name"], "Example Medicine")
        self.assertEqual(medicine["verified"], 1)

        self.client.get("/logout")
        self._login("patient_one")
        page = self.client.get("/prescriptions")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Approved", page.data)


if __name__ == "__main__":
    unittest.main()
