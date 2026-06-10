import os
import uuid

from flask import Blueprint, current_app, request, jsonify, send_file
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Case, Document
from app.auth.auth_decorator import roles_required, token_required
from app.audit.service import record_audit


documents_bp = Blueprint("documents", __name__)


ALLOWED_MIME_TYPES = {
    ".pdf": {"application/pdf"},
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png": {"image/png"},
}


def get_upload_root():
    return os.path.abspath(current_app.config["UPLOAD_FOLDER"])


def get_case_upload_folder(case_id):
    return os.path.join(
        get_upload_root(),
        "cases",
        str(case_id)
    )


def get_document_extension(filename):
    return os.path.splitext(filename or "")[1].lower()


def has_valid_file_signature(file_storage, extension):
    position = file_storage.stream.tell()
    header = file_storage.stream.read(16)
    file_storage.stream.seek(position)

    if extension == ".pdf":
        return header.startswith(b"%PDF")

    if extension in [".jpg", ".jpeg"]:
        return header.startswith(b"\xff\xd8\xff")

    if extension == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")

    return False


def validate_uploaded_file(file_storage):
    if not file_storage or not file_storage.filename:
        return "A file is required."

    original_filename = secure_filename(file_storage.filename)

    if not original_filename:
        return "The uploaded file name is invalid."

    extension = get_document_extension(original_filename)
    allowed_extensions = current_app.config["ALLOWED_DOCUMENT_EXTENSIONS"]

    if extension not in allowed_extensions:
        return "Only PDF, JPG, JPEG and PNG files are allowed."

    allowed_mime_types = ALLOWED_MIME_TYPES.get(extension, set())

    if file_storage.mimetype not in allowed_mime_types:
        return "The uploaded file type does not match the allowed formats."

    if not has_valid_file_signature(file_storage, extension):
        return "The uploaded file content is not a valid allowed document."

    return None


def resolve_private_upload_path(relative_path):
    if not relative_path:
        return None

    normalized_relative_path = relative_path.replace("\\", os.sep)
    absolute_path = os.path.abspath(
        os.path.join(
            os.path.dirname(get_upload_root()),
            normalized_relative_path
        )
    )

    upload_root = get_upload_root()

    if (
        absolute_path != upload_root
        and not absolute_path.startswith(upload_root + os.sep)
    ):
        return None

    return absolute_path


def document_to_dict(document):
    has_uploaded_file = bool(
        document.file_location
        and document.file_location.startswith("uploads/")
    )

    return {
        "id": document.id,
        "case_id": document.case_id,
        "document_name": document.document_name,
        "required": document.required,
        "status": document.status,
        "source": document.source,
        "file_name": document.file_name,
        "file_location": document.file_location,
        "has_uploaded_file": has_uploaded_file,
        "download_url": (
            f"/api/documents/{document.id}/download"
            if has_uploaded_file
            else None
        ),
        "received_date": document.received_date,
        "checked_by": document.checked_by,
        "notes": document.notes,
        "created_at": (
            document.created_at.isoformat()
            if document.created_at
            else None
        ),
        "updated_at": (
            document.updated_at.isoformat()
            if document.updated_at
            else None
        ),
    }


@documents_bp.route(
    "/cases/<int:case_id>/documents",
    methods=["GET"]
)
@token_required
def get_case_documents(current_user, case_id):
    case = db.session.get(Case, case_id)

    if not case:
        return jsonify({
            "message": "Case not found"
        }), 404

    documents = (
        Document.query
        .filter_by(case_id=case_id)
        .order_by(Document.id.desc())
        .all()
    )

    return jsonify({
        "count": len(documents),
        "documents": [
            document_to_dict(document)
            for document in documents
        ]
    }), 200


@documents_bp.route(
    "/cases/<int:case_id>/documents",
    methods=["POST"]
)
@token_required
def create_document(current_user, case_id):
    case = db.session.get(Case, case_id)

    if not case:
        return jsonify({
            "message": "Case not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    document_name = data.get("document_name")

    if not document_name:
        return jsonify({
            "message": "Document name is required"
        }), 400

    document = Document(
        case_id=case_id,
        document_name=document_name,
        required=data.get("required", True),
        status=data.get("status", "Requested"),
        source=data.get("source"),
        file_name=data.get("file_name"),
        file_location=data.get("file_location"),
        received_date=data.get("received_date"),
        checked_by=data.get("checked_by"),
        notes=data.get("notes"),
    )

    db.session.add(document)
    db.session.commit()

    return jsonify({
        "message": "Document created successfully",
        "document": document_to_dict(document)
    }), 201


@documents_bp.route(
    "/cases/<int:case_id>/documents/upload",
    methods=["POST"]
)
@token_required
def upload_document(current_user, case_id):
    case = db.session.get(Case, case_id)

    if not case:
        return jsonify({
            "message": "Case not found"
        }), 404

    file_storage = request.files.get("file")
    validation_error = validate_uploaded_file(file_storage)

    if validation_error:
        return jsonify({
            "message": validation_error
        }), 400

    document_name = request.form.get("document_name")

    if not document_name:
        return jsonify({
            "message": "Document name is required"
        }), 400

    original_filename = secure_filename(file_storage.filename)
    extension = get_document_extension(original_filename)
    stored_filename = f"{uuid.uuid4()}{extension}"

    case_upload_folder = get_case_upload_folder(case_id)
    os.makedirs(case_upload_folder, exist_ok=True)

    absolute_file_path = os.path.join(
        case_upload_folder,
        stored_filename
    )
    file_storage.save(absolute_file_path)

    relative_file_path = os.path.join(
        "uploads",
        "cases",
        str(case_id),
        stored_filename
    ).replace("\\", "/")

    required_raw = request.form.get("required", "true").lower()

    document = Document(
        case_id=case_id,
        document_name=document_name,
        required=required_raw in ["true", "1", "yes", "on"],
        status=request.form.get("status") or "Received",
        source=request.form.get("source"),
        file_name=stored_filename,
        file_location=relative_file_path,
        received_date=request.form.get("received_date"),
        checked_by=request.form.get("checked_by"),
        notes=request.form.get("notes"),
    )

    db.session.add(document)
    db.session.commit()

    record_audit(
        current_user,
        "document_uploaded",
        "Document",
        document.id,
        f"Uploaded document for case {case_id}"
    )

    return jsonify({
        "message": "Document uploaded successfully",
        "document": document_to_dict(document),
        "original_file_name": original_filename
    }), 201


@documents_bp.route(
    "/documents/<int:document_id>",
    methods=["GET"]
)
@token_required
def get_document(current_user, document_id):
    document = db.session.get(Document, document_id)

    if not document:
        return jsonify({
            "message": "Document not found"
        }), 404

    return jsonify({
        "document": document_to_dict(document)
    }), 200


@documents_bp.route(
    "/documents/<int:document_id>/download",
    methods=["GET"]
)
@token_required
def download_document(current_user, document_id):
    document = db.session.get(Document, document_id)

    if not document:
        return jsonify({
            "message": "Document not found"
        }), 404

    absolute_file_path = resolve_private_upload_path(
        document.file_location
    )

    if (
        not absolute_file_path
        or not os.path.isfile(absolute_file_path)
    ):
        return jsonify({
            "message": "Uploaded file not found"
        }), 404

    download_name = document.file_name or os.path.basename(
        absolute_file_path
    )
    disposition = request.args.get("disposition", "attachment")
    as_attachment = disposition != "inline"

    record_audit(
        current_user,
        "document_downloaded",
        "Document",
        document.id,
        f"Downloaded document for case {document.case_id}"
    )

    return send_file(
        absolute_file_path,
        as_attachment=as_attachment,
        download_name=download_name
    )


@documents_bp.route(
    "/documents/<int:document_id>",
    methods=["PUT"]
)
@token_required
def update_document(current_user, document_id):
    document = db.session.get(Document, document_id)

    if not document:
        return jsonify({
            "message": "Document not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    allowed_fields = [
        "document_name",
        "required",
        "status",
        "source",
        "file_name",
        "file_location",
        "received_date",
        "checked_by",
        "notes",
    ]

    for field in allowed_fields:
        if field in data:
            setattr(document, field, data.get(field))

    if not document.document_name:
        return jsonify({
            "message": "Document name is required"
        }), 400

    db.session.commit()

    return jsonify({
        "message": "Document updated successfully",
        "document": document_to_dict(document)
    }), 200


@documents_bp.route(
    "/documents/<int:document_id>",
    methods=["DELETE"]
)
@roles_required("admin", "solicitor")
def delete_document(current_user, document_id):
    document = db.session.get(Document, document_id)

    if not document:
        return jsonify({
            "message": "Document not found"
        }), 404

    absolute_file_path = resolve_private_upload_path(
        document.file_location
    )

    document_id = document.id
    case_id = document.case_id

    db.session.delete(document)
    db.session.commit()

    if absolute_file_path and os.path.isfile(absolute_file_path):
        os.remove(absolute_file_path)

    record_audit(
        current_user,
        "document_deleted",
        "Document",
        document_id,
        f"Deleted document from case {case_id}"
    )

    return jsonify({
        "message": "Document deleted successfully"
    }), 200
