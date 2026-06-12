from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Case, Appointment
from app.auth.auth_decorator import (
    CASE_DELETE_ROLES,
    CASE_WRITE_ROLES,
    roles_required,
    token_required,
)


appointments_bp = Blueprint("appointments", __name__)


def appointment_to_dict(appointment):
    return {
        "id": appointment.id,
        "case_id": appointment.case_id,
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
        "appointment_location": appointment.appointment_location,
        "appointment_type": appointment.appointment_type,
        "status": appointment.status,
        "notes": appointment.notes,
        "created_at": appointment.created_at.isoformat() if appointment.created_at else None,
        "updated_at": appointment.updated_at.isoformat() if appointment.updated_at else None
    }


@appointments_bp.route("/cases/<int:case_id>/appointments", methods=["GET"])
@token_required
def get_case_appointments(current_user, case_id):
    case = db.session.get(Case, case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    appointments = Appointment.query.filter_by(case_id=case_id).all()

    return jsonify({
        "count": len(appointments),
        "appointments": [
            appointment_to_dict(appointment)
            for appointment in appointments
        ]
    }), 200


@appointments_bp.route("/cases/<int:case_id>/appointments", methods=["POST"])
@roles_required(*CASE_WRITE_ROLES)
def create_appointment(current_user, case_id):
    case = db.session.get(Case, case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    appointment_date = data.get("appointment_date")

    if not appointment_date:
        return jsonify({"message": "Appointment date is required"}), 400

    allowed_statuses = [
        "Booked",
        "Completed",
        "Cancelled",
        "Rescheduled",
        "Missed"
    ]

    status = data.get("status", "Booked")

    if status not in allowed_statuses:
        return jsonify({"message": "Invalid appointment status"}), 400

    appointment = Appointment(
        case_id=case_id,
        appointment_date=appointment_date,
        appointment_time=data.get("appointment_time"),
        appointment_location=data.get("appointment_location"),
        appointment_type=data.get("appointment_type"),
        status=status,
        notes=data.get("notes")
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        "message": "Appointment added successfully",
        "appointment": appointment_to_dict(appointment)
    }), 201


@appointments_bp.route("/appointments/<int:appointment_id>", methods=["GET"])
@token_required
def get_appointment(current_user, appointment_id):
    appointment = db.session.get(Appointment, appointment_id)

    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404

    return jsonify(appointment_to_dict(appointment)), 200


@appointments_bp.route("/appointments/<int:appointment_id>", methods=["PUT"])
@roles_required(*CASE_WRITE_ROLES)
def update_appointment(current_user, appointment_id):
    appointment = db.session.get(Appointment, appointment_id)

    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    allowed_statuses = [
        "Booked",
        "Completed",
        "Cancelled",
        "Rescheduled",
        "Missed"
    ]

    if "status" in data and data["status"] not in allowed_statuses:
        return jsonify({"message": "Invalid appointment status"}), 400

    appointment.appointment_date = data.get(
        "appointment_date",
        appointment.appointment_date
    )
    appointment.appointment_time = data.get(
        "appointment_time",
        appointment.appointment_time
    )
    appointment.appointment_location = data.get(
        "appointment_location",
        appointment.appointment_location
    )
    appointment.appointment_type = data.get(
        "appointment_type",
        appointment.appointment_type
    )
    appointment.status = data.get("status", appointment.status)
    appointment.notes = data.get("notes", appointment.notes)

    db.session.commit()

    return jsonify({
        "message": "Appointment updated successfully",
        "appointment": appointment_to_dict(appointment)
    }), 200


@appointments_bp.route("/appointments/<int:appointment_id>", methods=["DELETE"])
@roles_required(*CASE_DELETE_ROLES)
def delete_appointment(current_user, appointment_id):
    appointment = db.session.get(Appointment, appointment_id)

    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment deleted successfully"}), 200
