from flask import request

from app.extensions import db
from app.models import AuditLog


def record_audit(
    user,
    action,
    entity_type=None,
    entity_id=None,
    description=None
):
    audit_log = AuditLog(
        user_id=user.id if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=request.remote_addr
    )

    db.session.add(audit_log)
    db.session.commit()

    return audit_log
