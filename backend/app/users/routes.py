from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import User
from app.auth.auth_decorator import roles_required
from app.audit.service import record_audit


users_bp = Blueprint("users", __name__)


def user_to_dict(user):
    return {
        "id": user.id,
        "firm_id": user.firm_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": (
            user.created_at.isoformat()
            if user.created_at
            else None
        )
    }


@users_bp.route("/users", methods=["GET"])
@roles_required("admin")
def get_users(current_user):
    users = (
        User.query
        .filter_by(firm_id=current_user.firm_id)
        .order_by(User.id.asc())
        .all()
    )

    return jsonify({
        "count": len(users),
        "users": [user_to_dict(user) for user in users]
    }), 200


@users_bp.route("/users/<int:user_id>/role", methods=["PUT"])
@roles_required("admin")
def update_user_role(current_user, user_id):
    user = db.session.get(User, user_id)

    if not user or user.firm_id != current_user.firm_id:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    role = data.get("role")
    allowed_roles = ["admin", "solicitor", "staff"]

    if role not in allowed_roles:
        return jsonify({"message": "Invalid role"}), 400

    old_role = user.role
    user.role = role
    db.session.commit()

    record_audit(
        current_user,
        "user_role_updated",
        "User",
        user.id,
        f"Changed {user.email} role from {old_role} to {role}"
    )

    return jsonify({
        "message": "User role updated successfully",
        "user": user_to_dict(user)
    }), 200
