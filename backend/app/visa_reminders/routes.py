from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Case, VisaReminder
from app.auth.auth_decorator import roles_required, token_required


visa_reminders_bp = Blueprint("visa_reminders", __name__)


def visa_reminder_to_dict(reminder):
    return {
        "id": reminder.id,
        "case_id": reminder.case_id,
        "visa_granted_date": reminder.visa_granted_date,
        "visa_expiry_date": reminder.visa_expiry_date,
        "reminder_date": reminder.reminder_date,
        "client_contacted": reminder.client_contacted,
        "notes": reminder.notes,
        "created_at": reminder.created_at.isoformat() if reminder.created_at else None,
        "updated_at": reminder.updated_at.isoformat() if reminder.updated_at else None
    }


@visa_reminders_bp.route("/cases/<int:case_id>/visa-reminders", methods=["GET"])
@token_required
def get_case_visa_reminders(current_user, case_id):
    case = Case.query.get(case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    reminders = VisaReminder.query.filter_by(case_id=case_id).all()

    return jsonify({
        "count": len(reminders),
        "visa_reminders": [
            visa_reminder_to_dict(reminder)
            for reminder in reminders
        ]
    }), 200


@visa_reminders_bp.route("/cases/<int:case_id>/visa-reminders", methods=["POST"])
@token_required
def create_visa_reminder(current_user, case_id):
    case = Case.query.get(case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    visa_expiry_date = data.get("visa_expiry_date")
    reminder_date = data.get("reminder_date")

    if not visa_expiry_date:
        return jsonify({"message": "Visa expiry date is required"}), 400

    if not reminder_date:
        return jsonify({"message": "Reminder date is required"}), 400

    reminder = VisaReminder(
        case_id=case_id,
        visa_granted_date=data.get("visa_granted_date"),
        visa_expiry_date=visa_expiry_date,
        reminder_date=reminder_date,
        client_contacted=data.get("client_contacted", False),
        notes=data.get("notes")
    )

    db.session.add(reminder)
    db.session.commit()

    return jsonify({
        "message": "Visa reminder added successfully",
        "visa_reminder": visa_reminder_to_dict(reminder)
    }), 201


@visa_reminders_bp.route("/visa-reminders/<int:reminder_id>", methods=["GET"])
@token_required
def get_visa_reminder(current_user, reminder_id):
    reminder = VisaReminder.query.get(reminder_id)

    if not reminder:
        return jsonify({"message": "Visa reminder not found"}), 404

    return jsonify(visa_reminder_to_dict(reminder)), 200


@visa_reminders_bp.route("/visa-reminders/<int:reminder_id>", methods=["PUT"])
@token_required
def update_visa_reminder(current_user, reminder_id):
    reminder = VisaReminder.query.get(reminder_id)

    if not reminder:
        return jsonify({"message": "Visa reminder not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    reminder.visa_granted_date = data.get(
        "visa_granted_date",
        reminder.visa_granted_date
    )
    reminder.visa_expiry_date = data.get(
        "visa_expiry_date",
        reminder.visa_expiry_date
    )
    reminder.reminder_date = data.get(
        "reminder_date",
        reminder.reminder_date
    )
    reminder.client_contacted = data.get(
        "client_contacted",
        reminder.client_contacted
    )
    reminder.notes = data.get("notes", reminder.notes)

    db.session.commit()

    return jsonify({
        "message": "Visa reminder updated successfully",
        "visa_reminder": visa_reminder_to_dict(reminder)
    }), 200


@visa_reminders_bp.route("/visa-reminders/<int:reminder_id>", methods=["DELETE"])
@roles_required("admin", "solicitor")
def delete_visa_reminder(current_user, reminder_id):
    reminder = VisaReminder.query.get(reminder_id)

    if not reminder:
        return jsonify({"message": "Visa reminder not found"}), 404

    db.session.delete(reminder)
    db.session.commit()

    return jsonify({"message": "Visa reminder deleted successfully"}), 200
