from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Case, Note
from app.auth.auth_decorator import roles_required, token_required
from app.audit.service import record_audit


notes_bp = Blueprint("notes", __name__)


def note_to_dict(note):
    return {
        "id": note.id,
        "case_id": note.case_id,
        "user_id": note.user_id,
        "note_text": note.note_text,
        "created_at": (
            note.created_at.isoformat()
            if note.created_at
            else None
        )
    }


@notes_bp.route("/cases/<int:case_id>/notes", methods=["GET"])
@token_required
def get_case_notes(current_user, case_id):
    case = db.session.get(Case, case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    notes = (
        Note.query
        .filter_by(case_id=case_id)
        .order_by(Note.id.desc())
        .all()
    )

    return jsonify({
        "count": len(notes),
        "notes": [note_to_dict(note) for note in notes]
    }), 200


@notes_bp.route("/cases/<int:case_id>/notes", methods=["POST"])
@token_required
def create_note(current_user, case_id):
    case = db.session.get(Case, case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    note_text = data.get("note_text")

    if not note_text:
        return jsonify({"message": "Note text is required"}), 400

    note = Note(
        case_id=case_id,
        user_id=current_user.id,
        note_text=note_text
    )

    db.session.add(note)
    db.session.commit()

    record_audit(
        current_user,
        "note_created",
        "Note",
        note.id,
        f"Created note for case {case_id}"
    )

    return jsonify({
        "message": "Note added successfully",
        "note": note_to_dict(note)
    }), 201


@notes_bp.route("/notes/<int:note_id>", methods=["PUT"])
@token_required
def update_note(current_user, note_id):
    note = db.session.get(Note, note_id)

    if not note:
        return jsonify({"message": "Note not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    note_text = data.get("note_text")

    if not note_text:
        return jsonify({"message": "Note text is required"}), 400

    note.note_text = note_text
    db.session.commit()

    record_audit(
        current_user,
        "note_updated",
        "Note",
        note.id,
        f"Updated note for case {note.case_id}"
    )

    return jsonify({
        "message": "Note updated successfully",
        "note": note_to_dict(note)
    }), 200


@notes_bp.route("/notes/<int:note_id>", methods=["DELETE"])
@roles_required("admin", "solicitor")
def delete_note(current_user, note_id):
    note = db.session.get(Note, note_id)

    if not note:
        return jsonify({"message": "Note not found"}), 404

    note_id = note.id
    case_id = note.case_id

    db.session.delete(note)
    db.session.commit()

    record_audit(
        current_user,
        "note_deleted",
        "Note",
        note_id,
        f"Deleted note from case {case_id}"
    )

    return jsonify({"message": "Note deleted successfully"}), 200
