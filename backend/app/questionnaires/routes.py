from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Questionnaire
from app.auth.auth_decorator import (
    CASE_DELETE_ROLES,
    CASE_WRITE_ROLES,
    roles_required,
    token_required,
)
from app.auth.tenant import get_case_for_user, get_case_record_for_user


questionnaires_bp = Blueprint("questionnaires", __name__)


def questionnaire_to_dict(questionnaire):
    return {
        "id": questionnaire.id,
        "case_id": questionnaire.case_id,
        "question": questionnaire.question,
        "client_answer": questionnaire.client_answer,
        "status": questionnaire.status,
        "asked_date": questionnaire.asked_date,
        "answered_date": questionnaire.answered_date,
        "follow_up_needed": questionnaire.follow_up_needed,
        "notes": questionnaire.notes,
        "created_at": questionnaire.created_at.isoformat() if questionnaire.created_at else None,
        "updated_at": questionnaire.updated_at.isoformat() if questionnaire.updated_at else None
    }


@questionnaires_bp.route("/cases/<int:case_id>/questionnaires", methods=["GET"])
@token_required
def get_case_questionnaires(current_user, case_id):
    case = get_case_for_user(current_user, case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    questionnaires = Questionnaire.query.filter_by(case_id=case_id).all()

    return jsonify({
        "count": len(questionnaires),
        "questionnaires": [
            questionnaire_to_dict(questionnaire)
            for questionnaire in questionnaires
        ]
    }), 200


@questionnaires_bp.route("/cases/<int:case_id>/questionnaires", methods=["POST"])
@roles_required(*CASE_WRITE_ROLES)
def create_questionnaire(current_user, case_id):
    case = get_case_for_user(current_user, case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    question = data.get("question")

    if not question:
        return jsonify({"message": "Question is required"}), 400

    allowed_statuses = [
        "Not Asked",
        "Asked",
        "Answered",
        "Unclear",
        "Still Missing",
        "Confirmed"
    ]

    status = data.get("status", "Not Asked")

    if status not in allowed_statuses:
        return jsonify({"message": "Invalid questionnaire status"}), 400

    questionnaire = Questionnaire(
        case_id=case_id,
        question=question,
        client_answer=data.get("client_answer"),
        status=status,
        asked_date=data.get("asked_date"),
        answered_date=data.get("answered_date"),
        follow_up_needed=data.get("follow_up_needed", False),
        notes=data.get("notes")
    )

    db.session.add(questionnaire)
    db.session.commit()

    return jsonify({
        "message": "Questionnaire item added successfully",
        "questionnaire": questionnaire_to_dict(questionnaire)
    }), 201


@questionnaires_bp.route("/questionnaires/<int:questionnaire_id>", methods=["GET"])
@token_required
def get_questionnaire(current_user, questionnaire_id):
    questionnaire = get_case_record_for_user(
        current_user,
        Questionnaire,
        questionnaire_id
    )

    if not questionnaire:
        return jsonify({"message": "Questionnaire item not found"}), 404

    return jsonify(questionnaire_to_dict(questionnaire)), 200


@questionnaires_bp.route("/questionnaires/<int:questionnaire_id>", methods=["PUT"])
@roles_required(*CASE_WRITE_ROLES)
def update_questionnaire(current_user, questionnaire_id):
    questionnaire = get_case_record_for_user(
        current_user,
        Questionnaire,
        questionnaire_id
    )

    if not questionnaire:
        return jsonify({"message": "Questionnaire item not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    allowed_statuses = [
        "Not Asked",
        "Asked",
        "Answered",
        "Unclear",
        "Still Missing",
        "Confirmed"
    ]

    if "status" in data and data["status"] not in allowed_statuses:
        return jsonify({"message": "Invalid questionnaire status"}), 400

    questionnaire.question = data.get("question", questionnaire.question)
    questionnaire.client_answer = data.get(
        "client_answer",
        questionnaire.client_answer
    )
    questionnaire.status = data.get("status", questionnaire.status)
    questionnaire.asked_date = data.get("asked_date", questionnaire.asked_date)
    questionnaire.answered_date = data.get(
        "answered_date",
        questionnaire.answered_date
    )
    questionnaire.follow_up_needed = data.get(
        "follow_up_needed",
        questionnaire.follow_up_needed
    )
    questionnaire.notes = data.get("notes", questionnaire.notes)

    db.session.commit()

    return jsonify({
        "message": "Questionnaire item updated successfully",
        "questionnaire": questionnaire_to_dict(questionnaire)
    }), 200


@questionnaires_bp.route("/questionnaires/<int:questionnaire_id>", methods=["DELETE"])
@roles_required(*CASE_DELETE_ROLES)
def delete_questionnaire(current_user, questionnaire_id):
    questionnaire = get_case_record_for_user(
        current_user,
        Questionnaire,
        questionnaire_id
    )

    if not questionnaire:
        return jsonify({"message": "Questionnaire item not found"}), 404

    db.session.delete(questionnaire)
    db.session.commit()

    return jsonify({"message": "Questionnaire item deleted successfully"}), 200
