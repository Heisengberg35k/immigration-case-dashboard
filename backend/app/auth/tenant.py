from app.extensions import db
from app.models import Case, Client


def get_client_for_user(current_user, client_id):
    client = db.session.get(Client, client_id)

    if not client or client.firm_id != current_user.firm_id:
        return None

    return client


def client_query_for_user(current_user):
    return Client.query.filter_by(firm_id=current_user.firm_id)


def case_query_for_user(current_user):
    return (
        Case.query
        .join(Client, Case.client_id == Client.id)
        .filter(Client.firm_id == current_user.firm_id)
    )


def get_case_for_user(current_user, case_id):
    return (
        case_query_for_user(current_user)
        .filter(Case.id == case_id)
        .first()
    )


def get_case_record_for_user(current_user, model, record_id):
    record = db.session.get(model, record_id)

    if not record:
        return None

    case = get_case_for_user(current_user, record.case_id)

    if not case:
        return None

    return record
