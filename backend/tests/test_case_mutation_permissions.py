from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import pytest

from app import create_app
from app.extensions import db
from app.models import (
    Appointment,
    Case,
    Client,
    Deadline,
    Document,
    Firm,
    Note,
    Payment,
    Questionnaire,
    User,
    VisaReminder,
)


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTO_CREATE_TABLES", "false")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("UPLOAD_FOLDER", str(tmp_path / "uploads"))

    test_app = create_app()
    test_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret-key-that-is-long-enough",
    )

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def make_firm(name="Test Firm"):
    firm = Firm(name=name)
    db.session.add(firm)
    db.session.commit()
    return firm


@pytest.fixture
def firm():
    return make_firm()


def make_user(role, firm):
    password_hash = bcrypt.hashpw(
        b"Password123",
        bcrypt.gensalt()
    ).decode("utf-8")
    user = User(
        firm_id=firm.id,
        name=f"{role.title()} User",
        email=f"{role}@firm.test",
        password_hash=password_hash,
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


def auth_headers(app, user):
    token = jwt.encode(
        {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seeded_case(firm):
    client_record = Client(firm_id=firm.id, full_name="Test Client")
    db.session.add(client_record)
    db.session.flush()

    case = Case(
        client_id=client_record.id,
        application_type="Skilled Worker",
        case_status="New Consultation",
    )
    db.session.add(case)
    db.session.commit()
    return case


WRITE_REQUESTS = [
    (
        "POST",
        lambda case: "/api/clients",
        {"full_name": "New Client", "application_type": "Student Visa"},
    ),
    (
        "PUT",
        lambda case: "/api/clients/1",
        {"full_name": "Updated Client"},
    ),
    (
        "POST",
        lambda case: f"/api/cases/{case.id}/documents",
        {"document_name": "Passport"},
    ),
    (
        "PUT",
        lambda case: "/api/documents/1",
        {"document_name": "Updated Passport"},
    ),
    (
        "POST",
        lambda case: f"/api/cases/{case.id}/questionnaires",
        {"question": "Current address?"},
    ),
    (
        "PUT",
        lambda case: "/api/questionnaires/1",
        {"question": "Updated question?"},
    ),
    (
        "POST",
        lambda case: f"/api/cases/{case.id}/deadlines",
        {"deadline_type": "Biometrics", "deadline_date": "2026-07-01"},
    ),
    (
        "PUT",
        lambda case: "/api/deadlines/1",
        {"status": "Completed"},
    ),
    (
        "POST",
        lambda case: f"/api/cases/{case.id}/appointments",
        {"appointment_date": "2026-07-02"},
    ),
    (
        "PUT",
        lambda case: "/api/appointments/1",
        {"status": "Completed"},
    ),
    (
        "POST",
        lambda case: f"/api/cases/{case.id}/payments",
        {"total_fee": 1200, "amount_paid": 200},
    ),
    (
        "PUT",
        lambda case: "/api/payments/1",
        {"amount_paid": 500},
    ),
    (
        "POST",
        lambda case: f"/api/cases/{case.id}/visa-reminders",
        {"visa_expiry_date": "2027-01-01", "reminder_date": "2026-12-01"},
    ),
    (
        "PUT",
        lambda case: "/api/visa-reminders/1",
        {"client_contacted": True},
    ),
    (
        "POST",
        lambda case: f"/api/cases/{case.id}/notes",
        {"note_text": "Client called."},
    ),
    (
        "PUT",
        lambda case: "/api/notes/1",
        {"note_text": "Updated note."},
    ),
]


@pytest.mark.parametrize(("method", "path_for", "payload"), WRITE_REQUESTS)
def test_unknown_roles_cannot_create_or_update_case_data(
    app,
    client,
    seeded_case,
    method,
    path_for,
    payload,
):
    viewer = make_user("viewer", seeded_case.client.firm)

    response = client.open(
        path_for(seeded_case),
        method=method,
        json=payload,
        headers=auth_headers(app, viewer),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("path_for", "payload"),
    [
        (
            lambda case: "/api/clients",
            {"full_name": "Staff Client", "application_type": "Family Visa"},
        ),
        (
            lambda case: f"/api/cases/{case.id}/documents",
            {"document_name": "Passport"},
        ),
        (
            lambda case: f"/api/cases/{case.id}/questionnaires",
            {"question": "Previous refusals?"},
        ),
        (
            lambda case: f"/api/cases/{case.id}/deadlines",
            {"deadline_type": "Submission", "deadline_date": "2026-07-01"},
        ),
        (
            lambda case: f"/api/cases/{case.id}/appointments",
            {"appointment_date": "2026-07-02"},
        ),
        (
            lambda case: f"/api/cases/{case.id}/payments",
            {"total_fee": 1000, "amount_paid": 100},
        ),
        (
            lambda case: f"/api/cases/{case.id}/visa-reminders",
            {"visa_expiry_date": "2027-01-01", "reminder_date": "2026-12-01"},
        ),
        (
            lambda case: f"/api/cases/{case.id}/notes",
            {"note_text": "Staff note."},
        ),
    ],
)
def test_staff_can_create_case_workflow_data(
    app,
    client,
    seeded_case,
    path_for,
    payload,
):
    staff = make_user("staff", seeded_case.client.firm)

    response = client.post(
        path_for(seeded_case),
        json=payload,
        headers=auth_headers(app, staff),
    )

    assert response.status_code == 201


def seed_delete_targets(case, user):
    records = [
        (
            "client",
            Client(firm_id=case.client.firm_id, full_name="Delete Client"),
            "/api/clients/{id}",
        ),
        (
            "document",
            Document(case_id=case.id, document_name="Passport"),
            "/api/documents/{id}",
        ),
        (
            "questionnaire",
            Questionnaire(case_id=case.id, question="Address?"),
            "/api/questionnaires/{id}",
        ),
        (
            "deadline",
            Deadline(
                case_id=case.id,
                deadline_type="Submission",
                deadline_date="2026-07-01",
            ),
            "/api/deadlines/{id}",
        ),
        (
            "appointment",
            Appointment(case_id=case.id, appointment_date="2026-07-02"),
            "/api/appointments/{id}",
        ),
        (
            "payment",
            Payment(case_id=case.id, total_fee=1000, amount_paid=100),
            "/api/payments/{id}",
        ),
        (
            "visa_reminder",
            VisaReminder(
                case_id=case.id,
                visa_expiry_date="2027-01-01",
                reminder_date="2026-12-01",
            ),
            "/api/visa-reminders/{id}",
        ),
        (
            "note",
            Note(case_id=case.id, user_id=user.id, note_text="Delete note."),
            "/api/notes/{id}",
        ),
    ]
    for _, record, _ in records:
        db.session.add(record)
    db.session.commit()
    return records


def test_staff_cannot_delete_but_solicitor_can(
    app,
    client,
    seeded_case,
):
    staff = make_user("staff", seeded_case.client.firm)
    solicitor = make_user("solicitor", seeded_case.client.firm)
    records = seed_delete_targets(seeded_case, staff)

    for _, record, path_template in records:
        response = client.delete(
            path_template.format(id=record.id),
            headers=auth_headers(app, staff),
        )
        assert response.status_code == 403

        response = client.delete(
            path_template.format(id=record.id),
            headers=auth_headers(app, solicitor),
        )
        assert response.status_code == 200


def create_case_for_firm(firm, full_name):
    client_record = Client(firm_id=firm.id, full_name=full_name)
    db.session.add(client_record)
    db.session.flush()

    case = Case(
        client_id=client_record.id,
        application_type="Skilled Worker",
        case_status="Active",
    )
    db.session.add(case)
    db.session.commit()
    return case


def test_clients_are_scoped_to_user_firm(app, client):
    firm_a = make_firm("Firm A")
    firm_b = make_firm("Firm B")
    user_a = make_user("staff", firm_a)
    case_a = create_case_for_firm(firm_a, "Firm A Client")
    case_b = create_case_for_firm(firm_b, "Firm B Client")

    response = client.get(
        "/api/clients",
        headers=auth_headers(app, user_a),
    )

    payload = response.get_json()
    client_names = [item["full_name"] for item in payload["clients"]]
    assert response.status_code == 200
    assert "Firm A Client" in client_names
    assert "Firm B Client" not in client_names

    response = client.get(
        f"/api/clients/{case_b.client_id}",
        headers=auth_headers(app, user_a),
    )
    assert response.status_code == 404

    response = client.get(
        f"/api/cases/{case_a.id}/full-profile",
        headers=auth_headers(app, user_a),
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/cases/{case_b.id}/full-profile",
        headers=auth_headers(app, user_a),
    )
    assert response.status_code == 404


def test_case_child_records_are_scoped_to_user_firm(app, client):
    firm_a = make_firm("Firm A")
    firm_b = make_firm("Firm B")
    user_a = make_user("staff", firm_a)
    case_b = create_case_for_firm(firm_b, "Firm B Client")
    document = Document(case_id=case_b.id, document_name="Other Firm Passport")
    db.session.add(document)
    db.session.commit()

    response = client.get(
        f"/api/documents/{document.id}",
        headers=auth_headers(app, user_a),
    )
    assert response.status_code == 404

    response = client.put(
        f"/api/documents/{document.id}",
        json={"document_name": "Leaked Update"},
        headers=auth_headers(app, user_a),
    )
    assert response.status_code == 404


def test_dashboard_and_reports_only_count_user_firm(app, client):
    firm_a = make_firm("Firm A")
    firm_b = make_firm("Firm B")
    user_a = make_user("staff", firm_a)
    case_a = create_case_for_firm(firm_a, "Firm A Client")
    case_b = create_case_for_firm(firm_b, "Firm B Client")
    db.session.add_all([
        Document(case_id=case_a.id, document_name="A", status="Requested"),
        Document(case_id=case_b.id, document_name="B", status="Requested"),
        Payment(case_id=case_a.id, payment_status="Overdue"),
        Payment(case_id=case_b.id, payment_status="Overdue"),
    ])
    db.session.commit()

    response = client.get(
        "/api/dashboard/summary",
        headers=auth_headers(app, user_a),
    )
    dashboard = response.get_json()
    assert response.status_code == 200
    assert dashboard["active_cases"] == 1
    assert dashboard["waiting_documents"] == 1
    assert dashboard["payments_overdue"] == 1

    response = client.get(
        "/api/reports/overview",
        headers=auth_headers(app, user_a),
    )
    reports = response.get_json()
    assert response.status_code == 200
    assert reports["totals"]["clients"] == 1
    assert reports["totals"]["cases"] == 1
    assert reports["totals"]["documents"] == 1
    assert reports["totals"]["payments"] == 1
