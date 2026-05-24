from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Client, Case
from app.auth.auth_decorator import token_required


clients_bp = Blueprint("clients", __name__)


def case_to_dict(case):
    return {
        "id": case.id,
        "client_id": case.client_id,
        "application_type": case.application_type,
        "case_status": case.case_status,
        "assigned_lawyer": case.assigned_lawyer,
        "assigned_staff": case.assigned_staff,
        "home_office_reference": case.home_office_reference,
        "main_deadline": case.main_deadline,
        "priority": case.priority,
        "file_location": case.file_location,
        "solicitor_review_status": case.solicitor_review_status,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None
    }


def client_to_dict(client):
    return {
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
        "cases": [case_to_dict(case) for case in client.cases]
    }


@clients_bp.route("", methods=["GET"])
@token_required
def get_clients(current_user):
    clients = Client.query.order_by(Client.created_at.desc()).all()

    return jsonify({
        "count": len(clients),
        "clients": [client_to_dict(client) for client in clients]
    }), 200


@clients_bp.route("", methods=["POST"])
@token_required
def create_client(current_user):
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    full_name = data.get("full_name")
    application_type = data.get("application_type")

    if not full_name:
        return jsonify({"message": "Client full name is required"}), 400

    if not application_type:
        return jsonify({"message": "Application type is required"}), 400

    client = Client(
        full_name=full_name,
        date_of_birth=data.get("date_of_birth"),
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address"),
        preferred_contact_method=data.get("preferred_contact_method"),
        whatsapp_number=data.get("whatsapp_number")
    )

    db.session.add(client)
    db.session.flush()

    case = Case(
        client_id=client.id,
        application_type=application_type,
        case_status=data.get("case_status", "New Consultation"),
        assigned_lawyer=data.get("assigned_lawyer"),
        assigned_staff=data.get("assigned_staff"),
        home_office_reference=data.get("home_office_reference"),
        main_deadline=data.get("main_deadline"),
        priority=data.get("priority", "Normal"),
        file_location=data.get("file_location"),
        solicitor_review_status=data.get(
            "solicitor_review_status",
            "Not Reviewed"
        )
    )

    db.session.add(case)
    db.session.commit()

    return jsonify({
        "message": "Client and case created successfully",
        "client": client_to_dict(client)
    }), 201


@clients_bp.route("/<int:client_id>", methods=["GET"])
@token_required
def get_client(current_user, client_id):
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"message": "Client not found"}), 404

    return jsonify(client_to_dict(client)), 200


@clients_bp.route("/<int:client_id>", methods=["PUT"])
@token_required
def update_client(current_user, client_id):
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"message": "Client not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    client.full_name = data.get("full_name", client.full_name)
    client.date_of_birth = data.get("date_of_birth", client.date_of_birth)
    client.phone = data.get("phone", client.phone)
    client.email = data.get("email", client.email)
    client.address = data.get("address", client.address)
    client.preferred_contact_method = data.get(
        "preferred_contact_method",
        client.preferred_contact_method
    )
    client.whatsapp_number = data.get(
        "whatsapp_number",
        client.whatsapp_number
    )

    db.session.commit()

    return jsonify({
        "message": "Client updated successfully",
        "client": client_to_dict(client)
    }), 200


@clients_bp.route("/<int:client_id>", methods=["DELETE"])
@token_required
def delete_client(current_user, client_id):
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"message": "Client not found"}), 404

    db.session.delete(client)
    db.session.commit()

    return jsonify({"message": "Client deleted successfully"}), 200