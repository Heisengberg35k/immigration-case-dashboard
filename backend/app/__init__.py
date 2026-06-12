from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate

from .auth.routes import auth_bp
from .clients.routes import clients_bp
from .dashboard.routes import dashboard_bp
from .documents.routes import documents_bp
from .questionnaires.routes import questionnaires_bp
from .deadlines.routes import deadlines_bp
from .appointments.routes import appointments_bp
from .payments.routes import payments_bp
from .visa_reminders.routes import visa_reminders_bp
from .notes.routes import notes_bp
from .audit.routes import audit_bp
from .reports.routes import reports_bp
from .users.routes import users_bp
from .cases.routes import cases_bp
from .firm.routes import firm_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"]
            }
        },
        supports_credentials=True,
    )

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # clients.routes.py already defines /clients.
    # So this must be /api, not /api/clients.
    app.register_blueprint(clients_bp, url_prefix="/api")

    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(cases_bp, url_prefix="/api/cases")
    app.register_blueprint(documents_bp, url_prefix="/api")
    app.register_blueprint(questionnaires_bp, url_prefix="/api")
    app.register_blueprint(deadlines_bp, url_prefix="/api")
    app.register_blueprint(appointments_bp, url_prefix="/api")
    app.register_blueprint(payments_bp, url_prefix="/api")
    app.register_blueprint(visa_reminders_bp, url_prefix="/api")
    app.register_blueprint(notes_bp, url_prefix="/api")
    app.register_blueprint(audit_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(firm_bp, url_prefix="/api")

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "running"}), 200

    from . import models  # noqa: F401

    if app.config["AUTO_CREATE_TABLES"]:
        with app.app_context():
            db.create_all()

    return app
