from flask import Blueprint, jsonify

from app.models import (
    Case,
    Document,
    Questionnaire,
    Deadline,
    Appointment,
    Payment,
    VisaReminder,
    Note
)
from app.auth.auth_decorator import token_required


cases_bp = Blueprint("cases", __name__)


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
        "updated_at": client.updated_at.isoformat() if client.updated_at else None
    }


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


def payment_to_dict(payment):
    return {
        "id": payment.id,
        "case_id": payment.case_id,
        "total_fee": payment.total_fee,
        "amount_paid": payment.amount_paid,
        "balance_due": payment.balance_due,
        "payment_status": payment.payment_status,
        "next_payment_due": payment.next_payment_due,
        "notes": payment.notes,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "updated_at": payment.updated_at.isoformat() if payment.updated_at else None
    }


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


def note_to_dict(note):
    return {
        "id": note.id,
        "case_id": note.case_id,
        "user_id": note.user_id,
        "note_text": note.note_text,
        "created_at": note.created_at.isoformat() if note.created_at else None
    }


@cases_bp.route("/<int:case_id>/full-profile", methods=["GET"])
@token_required
def get_case_full_profile(current_user, case_id):
    case = Case.query.get(case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    documents = Document.query.filter_by(case_id=case_id).all()
    questionnaires = Questionnaire.query.filter_by(case_id=case_id).all()
    deadlines = Deadline.query.filter_by(case_id=case_id).all()
    appointments = Appointment.query.filter_by(case_id=case_id).all()
    payments = Payment.query.filter_by(case_id=case_id).all()
    visa_reminders = VisaReminder.query.filter_by(case_id=case_id).all()
    notes = Note.query.filter_by(case_id=case_id).all()

    return jsonify({
        "client": client_to_dict(case.client),
        "case": case_to_dict(case),
        "documents": [document_to_dict(document) for document in documents],
        "questionnaires": [
            questionnaire_to_dict(questionnaire)
            for questionnaire in questionnaires
        ],
        "deadlines": [deadline_to_dict(deadline) for deadline in deadlines],
        "appointments": [
            appointment_to_dict(appointment)
            for appointment in appointments
        ],
        "payments": [payment_to_dict(payment) for payment in payments],
        "visa_reminders": [
            visa_reminder_to_dict(reminder)
            for reminder in visa_reminders
        ],
        "notes": [note_to_dict(note) for note in notes]
    }), 200