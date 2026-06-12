from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify

from app.models import (
    Document,
    Questionnaire,
    Deadline,
    Appointment,
    Payment,
    VisaReminder
)
from app.auth.auth_decorator import token_required
from app.auth.tenant import case_query_for_user, get_case_for_user


dashboard_bp = Blueprint("dashboard", __name__)


def parse_date(date_text):
    if not date_text:
        return None

    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return None


def deadline_alert_to_dict(current_user, deadline, deadline_date, today):
    case = get_case_for_user(current_user, deadline.case_id)
    client = case.client if case else None
    days_until_due = (deadline_date - today).days

    if days_until_due < 0:
        alert_status = "Overdue"
    elif days_until_due == 0:
        alert_status = "Due Today"
    else:
        alert_status = "Due Soon"

    return {
        "id": deadline.id,
        "case_id": deadline.case_id,
        "client_id": client.id if client else None,
        "client_name": client.full_name if client else "Unknown client",
        "case_type": case.application_type if case else None,
        "deadline_type": deadline.deadline_type,
        "deadline_date": deadline.deadline_date,
        "status": deadline.status,
        "alert_status": alert_status,
        "days_until_due": days_until_due,
        "notes": deadline.notes
    }


@dashboard_bp.route("/summary", methods=["GET"])
@token_required
def dashboard_summary(current_user):
    today = datetime.now(timezone.utc).date()
    next_7_days = today + timedelta(days=7)
    next_6_months = today + timedelta(days=183)
    scoped_cases = case_query_for_user(current_user).all()
    case_ids = [case.id for case in scoped_cases]

    active_cases = sum(
        1
        for case in scoped_cases
        if case.case_status not in ["Closed", "Visa Granted", "Visa Refused"]
    )

    waiting_documents = (
        Document.query
        .filter(
            Document.case_id.in_(case_ids),
            Document.status.in_(["Requested", "Missing", "Needs Rescan"])
        )
        .count()
        if case_ids
        else 0
    )

    waiting_client_answers = (
        Questionnaire.query
        .filter(
            Questionnaire.case_id.in_(case_ids),
            Questionnaire.status.in_(["Asked", "Unclear", "Still Missing"])
        )
        .count()
        if case_ids
        else 0
    )

    solicitor_review_pending = sum(
        1
        for case in scoped_cases
        if case.case_status == "Solicitor Review"
    )

    all_deadlines = (
        Deadline.query.filter(Deadline.case_id.in_(case_ids)).all()
        if case_ids
        else []
    )
    upload_deadlines_this_week = 0
    due_deadlines_today = 0
    overdue_deadlines = 0
    deadline_alerts = []

    for deadline in all_deadlines:
        deadline_date = parse_date(deadline.deadline_date)

        if deadline_date and deadline.status != "Completed":
            if deadline_date == today:
                due_deadlines_today += 1
                deadline_alerts.append(
                    deadline_alert_to_dict(
                        current_user,
                        deadline,
                        deadline_date,
                        today
                    )
                )
            elif deadline_date < today:
                overdue_deadlines += 1
                deadline_alerts.append(
                    deadline_alert_to_dict(
                        current_user,
                        deadline,
                        deadline_date,
                        today
                    )
                )

        if (
            deadline_date
            and today <= deadline_date <= next_7_days
            and deadline.deadline_type == "Upload Deadline"
            and deadline.status != "Completed"
        ):
            upload_deadlines_this_week += 1

    all_appointments = (
        Appointment.query.filter(Appointment.case_id.in_(case_ids)).all()
        if case_ids
        else []
    )
    appointments_this_week = 0

    for appointment in all_appointments:
        appointment_date = parse_date(appointment.appointment_date)

        if (
            appointment_date
            and today <= appointment_date <= next_7_days
            and appointment.status in ["Booked", "Rescheduled"]
        ):
            appointments_this_week += 1

    payments_overdue = (
        Payment.query
        .filter(
            Payment.case_id.in_(case_ids),
            Payment.payment_status == "Overdue"
        )
        .count()
        if case_ids
        else 0
    )

    all_visa_reminders = (
        VisaReminder.query
        .filter(VisaReminder.case_id.in_(case_ids))
        .all()
        if case_ids
        else []
    )
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
        "due_deadlines_today": due_deadlines_today,
        "overdue_deadlines": overdue_deadlines,
        "deadline_alerts": sorted(
            deadline_alerts,
            key=lambda item: (
                item["days_until_due"],
                item["deadline_date"],
                item["client_name"]
            )
        ),
        "appointments_this_week": appointments_this_week,
        "payments_overdue": payments_overdue,
        "visa_renewals_due_soon": visa_renewals_due_soon
    }), 200
