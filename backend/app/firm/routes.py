from flask import Blueprint, jsonify, request

from app.audit.service import record_audit
from app.auth.auth_decorator import roles_required, token_required
from app.extensions import db
from app.models import Firm


firm_bp = Blueprint("firm", __name__)


def firm_to_dict(firm):
    return {
        "id": firm.id,
        "name": firm.name,
        "created_at": (
            firm.created_at.isoformat()
            if firm.created_at
            else None
        )
    }


@firm_bp.route("/firm", methods=["GET"])
@token_required
def get_firm(current_user):
    firm = db.session.get(Firm, current_user.firm_id)

    if not firm:
        return jsonify({"message": "Firm not found"}), 404

    return jsonify({"firm": firm_to_dict(firm)}), 200


@firm_bp.route("/firm", methods=["PUT"])
@roles_required("admin")
def update_firm(current_user):
    firm = db.session.get(Firm, current_user.firm_id)

    if not firm:
        return jsonify({"message": "Firm not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"message": "Firm name is required"}), 400

    old_name = firm.name
    firm.name = name
    db.session.commit()

    record_audit(
        current_user,
        "firm_updated",
        "Firm",
        firm.id,
        f"Changed firm name from {old_name} to {firm.name}"
    )

    return jsonify({
        "message": "Firm updated successfully",
        "firm": firm_to_dict(firm)
    }), 200
