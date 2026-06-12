from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Client, Case
from app.auth.auth_decorator import (
    CASE_DELETE_ROLES,
    CASE_WRITE_ROLES,
    roles_required,
    token_required,
)
from app.auth.tenant import client_query_for_user, get_client_for_user


clients_bp = Blueprint("clients", __name__)


def case_to_client_summary(case):
    if not case:
        return {
            "case_id": None,
            "application_type": None,
            "case_type": None,
            "case_status": None,
            "status": None,
            "assigned_lawyer": None,
            "assigned_staff": None,
            "main_deadline": None,
            "priority": None,
        }

    return {
        "case_id": case.id,
        "application_type": case.application_type,
        "case_type": case.application_type,
        "case_status": case.case_status,
        "status": case.case_status,
        "assigned_lawyer": case.assigned_lawyer,
        "assigned_staff": case.assigned_staff,
        "main_deadline": case.main_deadline,
        "priority": case.priority,
    }


def client_to_dict(client):
    linked_case = (
        Case.query
        .filter_by(client_id=client.id)
        .order_by(Case.id.desc())
        .first()
    )

    data = {
        "id": client.id,
        "full_name": client.full_name,
        "date_of_birth": client.date_of_birth,
        "phone": client.phone,
        "email": client.email,
        "address": client.address,
        "preferred_contact_method": client.preferred_contact_method,
        "whatsapp_number": client.whatsapp_number,
        "created_at": client.created_at.isoformat() if client.created_at else None,
        "updated_at": client.updated_at.isoformat() if client.updated_at else None,
    }

    data.update(case_to_client_summary(linked_case))
    return data


@clients_bp.route("/clients", methods=["GET"])
@token_required
def get_clients(current_user):
    clients = (
        client_query_for_user(current_user)
        .order_by(Client.id.desc())
        .all()
    )

    return jsonify({
        "count": len(clients),
        "clients": [client_to_dict(client) for client in clients]
    }), 200


@clients_bp.route("/clients/<int:client_id>", methods=["GET"])
@token_required
def get_client(current_user, client_id):
    client = get_client_for_user(current_user, client_id)

    if not client:
        return jsonify({"message": "Client not found"}), 404

    return jsonify({"client": client_to_dict(client)}), 200


@clients_bp.route("/clients", methods=["POST"])
@roles_required(*CASE_WRITE_ROLES)
def create_client(current_user):
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    full_name = data.get("full_name")

    if not full_name:
        return jsonify({"message": "Client full name is required"}), 400

    application_type = data.get("application_type") or data.get("case_type")

    if not application_type:
        return jsonify({"message": "Application type / case type is required"}), 400

    client = Client(
        firm_id=current_user.firm_id,
        full_name=full_name,
        date_of_birth=data.get("date_of_birth"),
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address"),
        preferred_contact_method=data.get("preferred_contact_method"),
        whatsapp_number=data.get("whatsapp_number"),
    )

    db.session.add(client)
    db.session.flush()

    case = Case(
        client_id=client.id,
        application_type=application_type,
        case_status=data.get("case_status") or data.get("status") or "New Consultation",
        assigned_lawyer=data.get("assigned_lawyer"),
        assigned_staff=data.get("assigned_staff"),
        home_office_reference=data.get("home_office_reference"),
        main_deadline=data.get("main_deadline"),
        priority=data.get("priority", "Normal"),
        file_location=data.get("file_location"),
        solicitor_review_status=data.get("solicitor_review_status", "Not Reviewed"),
    )

    db.session.add(case)
    db.session.commit()

    return jsonify({
        "message": "Client and case created successfully",
        "client": client_to_dict(client)
    }), 201


@clients_bp.route("/clients/<int:client_id>", methods=["PUT"])
@roles_required(*CASE_WRITE_ROLES)
def update_client(current_user, client_id):
    client = get_client_for_user(current_user, client_id)

    if not client:
        return jsonify({"message": "Client not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    for field in [
        "full_name",
        "date_of_birth",
        "phone",
        "email",
        "address",
        "preferred_contact_method",
        "whatsapp_number",
    ]:
        if field in data:
            setattr(client, field, data.get(field))

    linked_case = (
        Case.query
        .filter_by(client_id=client.id)
        .order_by(Case.id.desc())
        .first()
    )

    if linked_case:
        if "application_type" in data or "case_type" in data:
            linked_case.application_type = (
                data.get("application_type")
                or data.get("case_type")
            )

        if "case_status" in data or "status" in data:
            linked_case.case_status = (
                data.get("case_status")
                or data.get("status")
            )

        for field in [
            "assigned_lawyer",
            "assigned_staff",
            "home_office_reference",
            "main_deadline",
            "priority",
            "file_location",
            "solicitor_review_status",
        ]:
            if field in data:
                setattr(linked_case, field, data.get(field))

    db.session.commit()

    return jsonify({
        "message": "Client updated successfully",
        "client": client_to_dict(client)
    }), 200


@clients_bp.route("/clients/<int:client_id>", methods=["DELETE"])
@roles_required(*CASE_DELETE_ROLES)
def delete_client(current_user, client_id):
    client = get_client_for_user(current_user, client_id)

    if not client:
        return jsonify({"message": "Client not found"}), 404

    db.session.delete(client)
    db.session.commit()

    return jsonify({"message": "Client deleted successfully"}), 200
