from collections import Counter
from datetime import datetime

from flask import Blueprint, jsonify

from app.models import (
    Appointment,
    Case,
    Client,
    Deadline,
    Document,
    Payment,
    Questionnaire,
    VisaReminder
)
from app.auth.auth_decorator import token_required


reports_bp = Blueprint("reports", __name__)


def parse_date(date_text):
    if not date_text:
        return None

    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return None


def counter_to_list(counter):
    return [
        {
            "label": label or "Unspecified",
            "count": count
        }
        for label, count in counter.most_common()
    ]


@reports_bp.route("/overview", methods=["GET"])
@token_required
def reports_overview(current_user):
    today = datetime.utcnow().date()

    cases = Case.query.all()
    documents = Document.query.all()
    deadlines = Deadline.query.all()
    payments = Payment.query.all()
    questionnaires = Questionnaire.query.all()
    appointments = Appointment.query.all()
    visa_reminders = VisaReminder.query.all()

    overdue_deadlines = 0

    for deadline in deadlines:
        deadline_date = parse_date(deadline.deadline_date)

        if (
            deadline_date
            and deadline_date < today
            and deadline.status != "Completed"
        ):
            overdue_deadlines += 1

    total_balance_due = sum(
        float(payment.balance_due or 0)
        for payment in payments
    )

    return jsonify({
        "totals": {
            "clients": Client.query.count(),
            "cases": len(cases),
            "documents": len(documents),
            "questionnaires": len(questionnaires),
            "deadlines": len(deadlines),
            "appointments": len(appointments),
            "payments": len(payments),
            "visa_reminders": len(visa_reminders),
            "overdue_deadlines": overdue_deadlines,
            "total_balance_due": total_balance_due
        },
        "cases_by_status": counter_to_list(
            Counter(case.case_status for case in cases)
        ),
        "cases_by_type": counter_to_list(
            Counter(case.application_type for case in cases)
        ),
        "documents_by_status": counter_to_list(
            Counter(document.status for document in documents)
        ),
        "payments_by_status": counter_to_list(
            Counter(payment.payment_status for payment in payments)
        )
    }), 200
