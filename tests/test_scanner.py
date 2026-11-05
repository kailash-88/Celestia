"""
Unit tests for scanner and OCR extraction services.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ocr_service import extract_prescription_data


def test_ocr_unavailable_path():
    result = extract_prescription_data("non_existent_image.png", "/invalid/path/tesseract")
    assert isinstance(result, dict)
    assert "raw_text" in result
    assert "fields" in result


def test_ocr_result_structure():
    result = extract_prescription_data("", "")
    assert "fields" in result
    expected_fields = ["name", "generic_name", "dosage", "form", "purpose", "expiry_date"]
    for field in expected_fields:
        assert field in result["fields"]
