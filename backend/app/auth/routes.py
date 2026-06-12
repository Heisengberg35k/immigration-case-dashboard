from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, current_app
import bcrypt
import jwt

from app.extensions import db
from app.models import User
from app.audit.service import record_audit
from .auth_decorator import roles_required, token_required


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@roles_required("admin")
def register(current_user):
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "staff")

    if not name or not email or not password:
        return jsonify({"message": "Name, email and password are required"}), 400

    allowed_roles = ["admin", "solicitor", "staff"]

    if role not in allowed_roles:
        return jsonify({"message": "Invalid role"}), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"message": "Email already registered"}), 409

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    new_user = User(
        firm_id=current_user.firm_id,
        name=name,
        email=email,
        password_hash=password_hash,
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    record_audit(
        current_user,
        "user_created",
        "User",
        new_user.id,
        f"Created user {new_user.email} with role {new_user.role}"
    )

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    password_valid = bcrypt.checkpw(
        password.encode("utf-8"),
        user.password_hash.encode("utf-8")
    )

    if not password_valid:
        return jsonify({"message": "Invalid email or password"}), 401

    token = jwt.encode(
        {
            "user_id": user.id,
            "firm_id": user.firm_id,
            "email": user.email,
            "role": user.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=8)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    record_audit(
        user,
        "login",
        "User",
        user.id,
        "User logged in"
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "firm_id": user.firm_id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200


@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile(current_user):
    return jsonify({
        "id": current_user.id,
        "firm_id": current_user.firm_id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }), 200
