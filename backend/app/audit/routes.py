from flask import Blueprint, jsonify

from app.extensions import db
from app.models import AuditLog, User
from app.auth.auth_decorator import roles_required


audit_bp = Blueprint("audit", __name__)


def audit_log_to_dict(log):
    user = db.session.get(User, log.user_id) if log.user_id else None

    return {
        "id": log.id,
        "user_id": log.user_id,
        "user_name": user.name if user else None,
        "user_email": user.email if user else None,
        "action": log.action,
        "entity_type": log.entity_type,
        "entity_id": log.entity_id,
        "description": log.description,
        "ip_address": log.ip_address,
        "created_at": (
            log.created_at.isoformat()
            if log.created_at
            else None
        )
    }


@audit_bp.route("/audit-logs", methods=["GET"])
@roles_required("admin", "solicitor")
def get_audit_logs(current_user):
    logs = (
        AuditLog.query
        .order_by(AuditLog.id.desc())
        .limit(200)
        .all()
    )

    return jsonify({
        "count": len(logs),
        "audit_logs": [audit_log_to_dict(log) for log in logs]
    }), 200
