"""
MediMitra Public API & Legal Blueprint
Handles:
- App Version Check API for Google Play / In-App updates & notifications
- Google Play Store compliant Privacy Policy
- Terms of Service
"""

from flask import Blueprint, jsonify, render_template, request
from database.db import query_db

api_bp = Blueprint('api', __name__)

CURRENT_VERSION_CODE = 1
CURRENT_VERSION_NAME = "1.0.0"


@api_bp.route('/api/app/version', methods=['GET'])
def get_app_version():
    """
    Returns the latest version information for Android app and web clients.
    Clients compare their installed versionCode against latest_version_code.
    """
    latest = query_db(
        "SELECT * FROM app_releases ORDER BY version_code DESC LIMIT 1",
        one=True
    )

    if latest:
        version_code = latest['version_code']
        version_name = latest['version_name']
        release_notes = latest['release_notes']
        force_update = bool(latest['force_update'])
        download_url = latest['download_url'] or "https://play.google.com/store/apps/details?id=com.medimitra.app"
    else:
        version_code = CURRENT_VERSION_CODE
        version_name = CURRENT_VERSION_NAME
        release_notes = "Latest stable version with AI strip scanner, verified doctor review, and multi-role dashboards."
        force_update = False
        download_url = "https://play.google.com/store/apps/details?id=com.medimitra.app"

    return jsonify({
        "status": "success",
        "latest_version_code": version_code,
        "latest_version_name": version_name,
        "min_supported_version": 1,
        "force_update": force_update,
        "release_notes": release_notes,
        "play_store_url": download_url,
        "github_release_url": "https://github.com/kailash-88/Celestia/releases/latest",
        "apk_direct_url": "https://github.com/kailash-88/Celestia/releases/latest/download/MediMitra-release.apk"
    })


@api_bp.route('/privacy-policy')
def privacy_policy():
    """Official Healthcare Privacy Policy compliant with Google Play Console policies."""
    return render_template('privacy_policy.html')


@api_bp.route('/terms')
def terms_of_service():
    """Terms of Service and Medical Disclaimer."""
    return render_template('terms.html')
