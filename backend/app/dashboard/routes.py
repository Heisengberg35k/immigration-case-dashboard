from flask import Blueprint, jsonify

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/summary", methods=["GET"])
def dashboard_summary():
    return jsonify({
        "active_cases": 0,
        "waiting_documents": 0,
        "waiting_client_answers": 0,
        "solicitor_review_pending": 0,
        "upload_deadlines_this_week": 0,
        "appointments_this_week": 0,
        "payments_overdue": 0,
        "visa_renewals_due_soon": 0
    }), 200