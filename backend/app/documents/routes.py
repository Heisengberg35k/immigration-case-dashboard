from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Case, Document
from app.auth.auth_decorator import token_required


documents_bp = Blueprint("documents", __name__)


def document_to_dict(document):
    return {
        "id": document.id,
        "case_id": document.case_id,
        "document_name": document.document_name,
        "required": document.required,
        "status": document.status,
        "source": document.source,
        "file_name": document.file_name,
        "file_location": document.file_location,
        "received_date": document.received_date,
        "checked_by": document.checked_by,
        "notes": document.notes,
        "created_at": document.created_at.isoformat() if document.created_at else None,
        "updated_at": document.updated_at.isoformat() if document.updated_at else None
    }


@documents_bp.route("/cases/<int:case_id>/documents", methods=["GET"])
@token_required
def get_case_documents(current_user, case_id):
    case = Case.query.get(case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    documents = Document.query.filter_by(case_id=case_id).all()

    return jsonify({
        "count": len(documents),
        "documents": [document_to_dict(document) for document in documents]
    }), 200


@documents_bp.route("/cases/<int:case_id>/documents", methods=["POST"])
@token_required
def create_document(current_user, case_id):
    case = Case.query.get(case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    document_name = data.get("document_name")

    if not document_name:
        return jsonify({"message": "Document name is required"}), 400

    allowed_statuses = [
        "Requested",
        "Received",
        "Renamed",
        "Checked",
        "Missing",
        "Needs Rescan",
        "Uploaded",
        "Not Required"
    ]

    status = data.get("status", "Requested")

    if status not in allowed_statuses:
        return jsonify({"message": "Invalid document status"}), 400

    document = Document(
        case_id=case_id,
        document_name=document_name,
        required=data.get("required", True),
        status=status,
        source=data.get("source"),
        file_name=data.get("file_name"),
        file_location=data.get("file_location"),
        received_date=data.get("received_date"),
        checked_by=data.get("checked_by"),
        notes=data.get("notes")
    )

    db.session.add(document)
    db.session.commit()

    return jsonify({
        "message": "Document added successfully",
        "document": document_to_dict(document)
    }), 201


@documents_bp.route("/documents/<int:document_id>", methods=["GET"])
@token_required
def get_document(current_user, document_id):
    document = Document.query.get(document_id)

    if not document:
        return jsonify({"message": "Document not found"}), 404

    return jsonify(document_to_dict(document)), 200


@documents_bp.route("/documents/<int:document_id>", methods=["PUT"])
@token_required
def update_document(current_user, document_id):
    document = Document.query.get(document_id)

    if not document:
        return jsonify({"message": "Document not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    allowed_statuses = [
        "Requested",
        "Received",
        "Renamed",
        "Checked",
        "Missing",
        "Needs Rescan",
        "Uploaded",
        "Not Required"
    ]

    if "status" in data and data["status"] not in allowed_statuses:
        return jsonify({"message": "Invalid document status"}), 400

    document.document_name = data.get("document_name", document.document_name)
    document.required = data.get("required", document.required)
    document.status = data.get("status", document.status)
    document.source = data.get("source", document.source)
    document.file_name = data.get("file_name", document.file_name)
    document.file_location = data.get("file_location", document.file_location)
    document.received_date = data.get("received_date", document.received_date)
    document.checked_by = data.get("checked_by", document.checked_by)
    document.notes = data.get("notes", document.notes)

    db.session.commit()

    return jsonify({
        "message": "Document updated successfully",
        "document": document_to_dict(document)
    }), 200


@documents_bp.route("/documents/<int:document_id>", methods=["DELETE"])
@token_required
def delete_document(current_user, document_id):
    document = Document.query.get(document_id)

    if not document:
        return jsonify({"message": "Document not found"}), 404

    db.session.delete(document)
    db.session.commit()

    return jsonify({"message": "Document deleted successfully"}), 200