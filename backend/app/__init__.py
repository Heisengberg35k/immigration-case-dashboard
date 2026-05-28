from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db

from .auth.routes import auth_bp
from .clients.routes import clients_bp
from .dashboard.routes import dashboard_bp
from .documents.routes import documents_bp
from .questionnaires.routes import questionnaires_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(clients_bp, url_prefix="/api/clients")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(documents_bp, url_prefix="/api")
    app.register_blueprint(questionnaires_bp, url_prefix="/api")
    
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "running"}), 200

    with app.app_context():
        from . import models
        db.create_all()

    return app