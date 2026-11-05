"""Focused role separation and caregiver consent checks for the Flask prototype."""
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class RoleAccessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory(dir=PROJECT_ROOT)
        os.environ["DATABASE_PATH"] = os.path.join(cls.tempdir.name, "roles.sqlite")
        from app import create_app
        cls.app = create_app()
        cls.app.config.update(TESTING=True)
        from database.db import execute_db
        from werkzeug.security import generate_password_hash
        cls.execute_db = execute_db
        cls.user_ids = {}
        for role in ("patient", "caregiver", "doctor", "admin", "pharmacist"):
            uid = execute_db(
                "INSERT INTO users (username,email,password_hash,full_name,role) VALUES (?,?,?,?,?)",
                [role, f"{role}@example.test", generate_password_hash("test-password"), role.title(), role],
            )
            cls.user_ids[role] = uid
        execute_db("INSERT INTO doctor_profiles(user_id,specialty,license_number,verification_status) VALUES(?,?,?,'verified')", [cls.user_ids["doctor"], "General Medicine", "DOC-TEST"])
        execute_db("INSERT INTO pharmacy_profiles(user_id,pharmacy_name,license_number) VALUES(?,?,?)", [cls.user_ids["pharmacist"], "Test Pharmacy", "PHARM-TEST"])

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()
        os.environ.pop("DATABASE_PATH", None)

    def client_for(self, role):
        client = self.app.test_client()
        with client.session_transaction() as sess:
            sess["user_id"] = self.user_ids[role]
            sess["role"] = role
            sess["username"] = role
        return client

    def test_role_templates_compile(self):
        for name in self.app.jinja_env.list_templates():
            self.app.jinja_env.get_template(name)

    def test_patient_tools_are_role_restricted(self):
        self.assertEqual(self.client_for("patient").get("/scanner").status_code, 200)
        for role in ("caregiver", "doctor", "admin", "pharmacist"):
            self.assertEqual(self.client_for(role).get("/scanner").status_code, 403)

    def test_dashboards_route_to_role_workspace(self):
        expected = {"doctor": "/doctor", "admin": "/admin", "caregiver": "/caregiver", "pharmacist": "/pharmacy"}
        for role, target in expected.items():
            response = self.client_for(role).get("/dashboard")
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith(target), (role, response.location))

    def test_each_role_workspace_loads(self):
        for role, path in (("patient", "/dashboard"), ("caregiver", "/caregiver"), ("doctor", "/doctor"), ("admin", "/admin"), ("pharmacist", "/pharmacy")):
            response = self.client_for(role).get(path)
            self.assertEqual(response.status_code, 200, (role, response.status_code))

    def test_caregiver_requires_patient_consent(self):
        caregiver = self.client_for("caregiver")
        response = caregiver.post("/caregiver/link", data={"identifier": "patient"}, follow_redirects=True)
        self.assertIn(b"must approve access", response.data)
        from database.db import query_db
        link = query_db("SELECT * FROM caregiver_links WHERE caregiver_id=? AND patient_id=?", [self.user_ids["caregiver"], self.user_ids["patient"]], one=True)
        self.assertEqual(link["status"], "pending")
        patient = self.client_for("patient")
        response = patient.post(f"/caregiver/requests/{link['id']}/approve", follow_redirects=True)
        self.assertIn(b"Caregiver access approved", response.data)
        updated = query_db("SELECT status FROM caregiver_links WHERE id=?", [link["id"]], one=True)
        self.assertEqual(updated["status"], "active")

    def test_pharmacy_application_is_pending_until_admin_verifies(self):
        client = self.app.test_client()
        response = client.post("/register", data={
            "full_name": "New Pharmacist", "username": "new-pharmacist", "email": "new-pharmacist@example.test",
            "password": "secret123", "confirm_password": "secret123", "role": "pharmacist",
            "pharmacy_name": "New Pharmacy", "pharmacy_license": "NEW-PHARM-123",
        })
        self.assertEqual(response.status_code, 302)
        from database.db import query_db
        account = query_db("SELECT id FROM users WHERE username='new-pharmacist'", one=True)
        profile = query_db("SELECT verification_status FROM pharmacy_profiles WHERE user_id=?", [account["id"]], one=True)
        self.assertEqual(profile["verification_status"], "pending")

    def test_ocr_noise_is_not_presented_as_a_medicine_and_placeholder_key_is_clear(self):
        from services.ai_service import extract_medicine_info
        with patch("services.ai_service.dotenv_values", return_value={}), patch.dict(os.environ, {"VISION_API_KEY": "paste-your-key-here", "OPENAI_API_KEY": "", "AI_API_KEY": ""}):
            result = extract_medicine_info("tae tablets 650 mg")
        self.assertEqual(result["source"], "ocr_only")
        self.assertEqual(result["extracted_facts"]["name"], "")
        self.assertIn("replace the placeholder", result["notice"])

    def test_vision_service_reads_dotenv_key_and_calls_provider(self):
        import json
        from services.ai_service import extract_medicine_info
        response = Mock()
        response.json.return_value = {"choices": [{"message": {"content": json.dumps({
            "extracted_facts": {"name": "Test medicine"}, "confidence": {"name": "medium"},
        })}}]}
        response.raise_for_status.return_value = None
        with patch.dict(os.environ, {"VISION_API_KEY": "", "OPENAI_API_KEY": "", "AI_API_KEY": ""}), \
             patch("services.ai_service.dotenv_values", return_value={"VISION_API_KEY": "test-key", "AI_MODEL": "test-model"}), \
             patch("requests.post", return_value=response) as post:
            result = extract_medicine_info("visible label text")
        self.assertEqual(result["source"], "vision_ai")
        self.assertEqual(result["extracted_facts"]["name"], "Test medicine")
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer test-key")

    def test_429_quota_error_is_explained(self):
        import requests
        from services.ai_service import extract_medicine_info
        response = Mock(status_code=429)
        response.json.return_value = {"error": {"code": "insufficient_quota"}}
        response.raise_for_status.side_effect = requests.HTTPError("quota", response=response)
        with patch.dict(os.environ, {"VISION_API_KEY": "test-key", "OPENAI_API_KEY": "", "AI_API_KEY": ""}), \
             patch("services.ai_service.dotenv_values", return_value={}), \
             patch("requests.post", return_value=response):
            result = extract_medicine_info("label text")
        self.assertIn("no available credits", result["notice"])

    def test_gemini_provider_uses_its_own_key_endpoint_and_model(self):
        import json
        from services.ai_service import extract_medicine_info
        response = Mock()
        response.json.return_value = {"choices": [{"message": {"content": json.dumps({
            "extracted_facts": {"name": "Test strip"}, "confidence": {"name": "medium"},
        })}}]}
        response.raise_for_status.return_value = None
        with patch.dict(os.environ, {"AI_PROVIDER": "gemini", "GEMINI_API_KEY": "test-gemini-key", "GEMINI_MODEL": "gemini-test", "VISION_API_KEY": "openai-key-must-not-be-used", "OPENAI_API_KEY": ""}), \
             patch("services.ai_service.dotenv_values", return_value={}), \
             patch("requests.post", return_value=response) as post:
            result = extract_medicine_info("visible label text")
        self.assertEqual(result["source"], "vision_ai")
        self.assertEqual(post.call_args.args[0], "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions")
        self.assertEqual(post.call_args.kwargs["json"]["model"], "gemini-test")
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer test-gemini-key")

    def test_gemini_does_not_fall_back_to_openai_key(self):
        from services.ai_service import extract_medicine_info
        with patch.dict(os.environ, {"AI_PROVIDER": "gemini", "GEMINI_API_KEY": "", "VISION_API_KEY": "openai-key-must-not-be-used", "OPENAI_API_KEY": ""}), \
             patch("services.ai_service.dotenv_values", return_value={}), \
             patch("requests.post") as post:
            result = extract_medicine_info("visible label text")
        self.assertEqual(result["source"], "ocr_only")
        self.assertIn("GEMINI_API_KEY", result["notice"])
        post.assert_not_called()

    def test_failed_ai_does_not_keep_ocr_fragment_as_drug_name(self):
        from routes.scanner import _analyze_image
        ocr = {"raw_text": "tae tablet 650 mg", "fields": {"name": "tae", "ocr_confidence": 30}}
        fallback = {"source": "ocr_only", "extracted_facts": {"name": "", "strength": "650 mg", "form": "tablet"}, "confidence": {}}
        with self.app.app_context(), \
             patch("routes.scanner.extract_prescription_data", return_value=ocr), \
             patch("routes.scanner.extract_medicine_info", return_value=fallback):
            _, fields = _analyze_image("unused-image.jpg")
        self.assertEqual(fields["name"], "")


if __name__ == "__main__":
    unittest.main()
