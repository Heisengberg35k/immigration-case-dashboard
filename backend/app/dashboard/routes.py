from datetime import datetime, timedelta
from flask import Blueprint, jsonify

from app.models import (
    Case,
    Document,
    Questionnaire,
    Deadline,
    Appointment,
    Payment,
    VisaReminder
)
from app.auth.auth_decorator import token_required


dashboard_bp = Blueprint("dashboard", __name__)


def parse_date(date_text):
    if not date_text:
        return None

    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return None


@dashboard_bp.route("/summary", methods=["GET"])
@token_required
def dashboard_summary(current_user):
    today = datetime.utcnow().date()
    next_7_days = today + timedelta(days=7)
    next_6_months = today + timedelta(days=183)

    active_cases = Case.query.filter(
        Case.case_status.notin_(["Closed", "Visa Granted", "Visa Refused"])
    ).count()

    waiting_documents = Document.query.filter(
        Document.status.in_(["Requested", "Missing", "Needs Rescan"])
    ).count()

    waiting_client_answers = Questionnaire.query.filter(
        Questionnaire.status.in_(["Asked", "Unclear", "Still Missing"])
    ).count()

    solicitor_review_pending = Case.query.filter(
        Case.case_status == "Solicitor Review"
    ).count()

    all_deadlines = Deadline.query.all()
    upload_deadlines_this_week = 0

    for deadline in all_deadlines:
        deadline_date = parse_date(deadline.deadline_date)

        if (
            deadline_date
            and today <= deadline_date <= next_7_days
            and deadline.deadline_type == "Upload Deadline"
            and deadline.status != "Completed"
        ):
            upload_deadlines_this_week += 1

    all_appointments = Appointment.query.all()
    appointments_this_week = 0

    for appointment in all_appointments:
        appointment_date = parse_date(appointment.appointment_date)

        if (
            appointment_date
            and today <= appointment_date <= next_7_days
            and appointment.status in ["Booked", "Rescheduled"]
        ):
            appointments_this_week += 1

    payments_overdue = Payment.query.filter(
        Payment.payment_status == "Overdue"
    ).count()

    all_visa_reminders = VisaReminder.query.all()
    visa_renewals_due_soon = 0

    for reminder in all_visa_reminders:
        reminder_date = parse_date(reminder.reminder_date)

        if (
            reminder_date
            and today <= reminder_date <= next_6_months
            and reminder.client_contacted is False
        ):
            visa_renewals_due_soon += 1

    return jsonify({
        "active_cases": active_cases,
        "waiting_documents": waiting_documents,
        "waiting_client_answers": waiting_client_answers,
        "solicitor_review_pending": solicitor_review_pending,
        "upload_deadlines_this_week": upload_deadlines_this_week,
        "appointments_this_week": appointments_this_week,
        "payments_overdue": payments_overdue,
        "visa_renewals_due_soon": visa_renewals_due_soon
    }), 200