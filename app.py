"""
MediMitra Application Factory
Initializes Flask, registers blueprints, configures extensions and database.
"""

import os
from flask import Flask
from config import get_config
from database.db import init_db, set_db_path


def create_app(config_class=None):
    """Application factory for MediMitra."""
    app = Flask(__name__)

    # Load configuration
    cfg = get_config()
    app.config.from_object(cfg)

    # Set database path
    set_db_path(app.config.get('DATABASE_PATH', 'medimitra.db'))

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize database
    init_db()

    # --- Register blueprints ---
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.scanner import scanner_bp
    from routes.schedule import schedule_bp
    from routes.caregiver import caregiver_bp
    from routes.reports import reports_bp
    from routes.medicines import medicines_bp
    from routes.safety import safety_bp
    from routes.prescriptions import prescriptions_bp
    from routes.doctor import doctor_bp
    from routes.admin import admin_bp
    from routes.pharmacy import pharmacy_bp
    from routes.assistant import assistant_bp
    from routes.queries import queries_bp
    from routes.records import records_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(scanner_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(caregiver_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(medicines_bp)
    app.register_blueprint(safety_bp)
    app.register_blueprint(prescriptions_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pharmacy_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(queries_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(api_bp)

    @app.cli.command("create-admin")
    def create_admin_command():
        """Create an administrator account for doctor verification and assignment."""
        from getpass import getpass
        from werkzeug.security import generate_password_hash
        from database.db import execute_db, query_db
        username = input("Admin username: ").strip()
        full_name = input("Admin full name: ").strip()
        email = input("Admin email: ").strip()
        password = getpass("Admin password (min 10 characters): ")
        if not username or not full_name or "@" not in email or len(password) < 10:
            raise click.ClickException("Enter a username, full name, valid email, and password of at least 10 characters.")
        if query_db("SELECT id FROM users WHERE username=? OR email=?", [username, email], one=True):
            raise click.ClickException("That username or email is already registered.")
        execute_db("INSERT INTO users (username,email,password_hash,full_name,role) VALUES (?,?,?,?, 'admin')",
                   [username,email,generate_password_hash(password),full_name])
        click.echo("Administrator account created.")

    # --- Context processor: inject user into all templates ---
    @app.context_processor
    def inject_globals():
        from routes.auth import get_current_user
        return dict(current_user=get_current_user())

    return app


if __name__ == '__main__':
    import os
    app = create_app()
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(host=host, port=port, debug=True)
