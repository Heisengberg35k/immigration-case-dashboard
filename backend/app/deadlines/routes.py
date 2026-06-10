from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Case, Deadline
from app.auth.auth_decorator import roles_required, token_required


deadlines_bp = Blueprint("deadlines", __name__)


def deadline_to_dict(deadline):
    return {
        "id": deadline.id,
        "case_id": deadline.case_id,
        "deadline_type": deadline.deadline_type,
        "deadline_date": deadline.deadline_date,
        "status": deadline.status,
        "notes": deadline.notes,
        "created_at": deadline.created_at.isoformat() if deadline.created_at else None,
        "updated_at": deadline.updated_at.isoformat() if deadline.updated_at else None
    }


@deadlines_bp.route("/cases/<int:case_id>/deadlines", methods=["GET"])
@token_required
def get_case_deadlines(current_user, case_id):
    case = Case.query.get(case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    deadlines = Deadline.query.filter_by(case_id=case_id).all()

    return jsonify({
        "count": len(deadlines),
        "deadlines": [deadline_to_dict(deadline) for deadline in deadlines]
    }), 200


@deadlines_bp.route("/cases/<int:case_id>/deadlines", methods=["POST"])
@token_required
def create_deadline(current_user, case_id):
    case = Case.query.get(case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    deadline_type = data.get("deadline_type")
    deadline_date = data.get("deadline_date")

    if not deadline_type:
        return jsonify({"message": "Deadline type is required"}), 400

    if not deadline_date:
        return jsonify({"message": "Deadline date is required"}), 400

    allowed_statuses = [
        "Upcoming",
        "Due Soon",
        "Overdue",
        "Completed"
    ]

    status = data.get("status", "Upcoming")

    if status not in allowed_statuses:
        return jsonify({"message": "Invalid deadline status"}), 400

    deadline = Deadline(
        case_id=case_id,
        deadline_type=deadline_type,
        deadline_date=deadline_date,
        status=status,
        notes=data.get("notes")
    )

    db.session.add(deadline)
    db.session.commit()

    return jsonify({
        "message": "Deadline added successfully",
        "deadline": deadline_to_dict(deadline)
    }), 201


@deadlines_bp.route("/deadlines/<int:deadline_id>", methods=["GET"])
@token_required
def get_deadline(current_user, deadline_id):
    deadline = Deadline.query.get(deadline_id)

    if not deadline:
        return jsonify({"message": "Deadline not found"}), 404

    return jsonify(deadline_to_dict(deadline)), 200


@deadlines_bp.route("/deadlines/<int:deadline_id>", methods=["PUT"])
@token_required
def update_deadline(current_user, deadline_id):
    deadline = Deadline.query.get(deadline_id)

    if not deadline:
        return jsonify({"message": "Deadline not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    allowed_statuses = [
        "Upcoming",
        "Due Soon",
        "Overdue",
        "Completed"
    ]

    if "status" in data and data["status"] not in allowed_statuses:
        return jsonify({"message": "Invalid deadline status"}), 400

    deadline.deadline_type = data.get("deadline_type", deadline.deadline_type)
    deadline.deadline_date = data.get("deadline_date", deadline.deadline_date)
    deadline.status = data.get("status", deadline.status)
    deadline.notes = data.get("notes", deadline.notes)

    db.session.commit()

    return jsonify({
        "message": "Deadline updated successfully",
        "deadline": deadline_to_dict(deadline)
    }), 200


@deadlines_bp.route("/deadlines/<int:deadline_id>", methods=["DELETE"])
@roles_required("admin", "solicitor")
def delete_deadline(current_user, deadline_id):
    deadline = Deadline.query.get(deadline_id)

    if not deadline:
        return jsonify({"message": "Deadline not found"}), 404

    db.session.delete(deadline)
    db.session.commit()

    return jsonify({"message": "Deadline deleted successfully"}), 200
