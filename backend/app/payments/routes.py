from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Case, Payment
from app.auth.auth_decorator import token_required


payments_bp = Blueprint("payments", __name__)


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


def calculate_balance(total_fee, amount_paid):
    return float(total_fee or 0) - float(amount_paid or 0)


@payments_bp.route("/cases/<int:case_id>/payments", methods=["GET"])
@token_required
def get_case_payments(current_user, case_id):
    case = Case.query.get(case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    payments = Payment.query.filter_by(case_id=case_id).all()

    return jsonify({
        "count": len(payments),
        "payments": [payment_to_dict(payment) for payment in payments]
    }), 200


@payments_bp.route("/cases/<int:case_id>/payments", methods=["POST"])
@token_required
def create_payment(current_user, case_id):
    case = Case.query.get(case_id)

    if not case:
        return jsonify({"message": "Case not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    allowed_statuses = [
        "Paid",
        "Part Paid",
        "Overdue",
        "Payment Plan",
        "No Payment Required"
    ]

    total_fee = data.get("total_fee", 0)
    amount_paid = data.get("amount_paid", 0)
    balance_due = calculate_balance(total_fee, amount_paid)

    payment_status = data.get("payment_status")

    if not payment_status:
        if balance_due <= 0 and float(total_fee or 0) > 0:
            payment_status = "Paid"
        elif float(total_fee or 0) == 0:
            payment_status = "No Payment Required"
        else:
            payment_status = "Part Paid"

    if payment_status not in allowed_statuses:
        return jsonify({"message": "Invalid payment status"}), 400

    payment = Payment(
        case_id=case_id,
        total_fee=total_fee,
        amount_paid=amount_paid,
        balance_due=balance_due,
        payment_status=payment_status,
        next_payment_due=data.get("next_payment_due"),
        notes=data.get("notes")
    )

    db.session.add(payment)
    db.session.commit()

    return jsonify({
        "message": "Payment added successfully",
        "payment": payment_to_dict(payment)
    }), 201


@payments_bp.route("/payments/<int:payment_id>", methods=["GET"])
@token_required
def get_payment(current_user, payment_id):
    payment = Payment.query.get(payment_id)

    if not payment:
        return jsonify({"message": "Payment not found"}), 404

    return jsonify(payment_to_dict(payment)), 200


@payments_bp.route("/payments/<int:payment_id>", methods=["PUT"])
@token_required
def update_payment(current_user, payment_id):
    payment = Payment.query.get(payment_id)

    if not payment:
        return jsonify({"message": "Payment not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    allowed_statuses = [
        "Paid",
        "Part Paid",
        "Overdue",
        "Payment Plan",
        "No Payment Required"
    ]

    total_fee = data.get("total_fee", payment.total_fee)
    amount_paid = data.get("amount_paid", payment.amount_paid)

    payment.total_fee = total_fee
    payment.amount_paid = amount_paid
    payment.balance_due = calculate_balance(total_fee, amount_paid)

    if "payment_status" in data:
        if data["payment_status"] not in allowed_statuses:
            return jsonify({"message": "Invalid payment status"}), 400

        payment.payment_status = data["payment_status"]
    else:
        if payment.balance_due <= 0 and float(payment.total_fee or 0) > 0:
            payment.payment_status = "Paid"
        elif float(payment.total_fee or 0) == 0:
            payment.payment_status = "No Payment Required"
        elif payment.payment_status == "Paid":
            payment.payment_status = "Part Paid"

    payment.next_payment_due = data.get(
        "next_payment_due",
        payment.next_payment_due
    )
    payment.notes = data.get("notes", payment.notes)

    db.session.commit()

    return jsonify({
        "message": "Payment updated successfully",
        "payment": payment_to_dict(payment)
    }), 200


@payments_bp.route("/payments/<int:payment_id>", methods=["DELETE"])
@token_required
def delete_payment(current_user, payment_id):
    payment = Payment.query.get(payment_id)

    if not payment:
        return jsonify({"message": "Payment not found"}), 404

    db.session.delete(payment)
    db.session.commit()

    return jsonify({"message": "Payment deleted successfully"}), 200