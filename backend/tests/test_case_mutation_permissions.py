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


def make_user(role):
    password_hash = bcrypt.hashpw(
        b"Password123",
        bcrypt.gensalt()
    ).decode("utf-8")
    user = User(
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
def seeded_case():
    client_record = Client(full_name="Test Client")
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
    viewer = make_user("viewer")

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
    staff = make_user("staff")

    response = client.post(
        path_for(seeded_case),
        json=payload,
        headers=auth_headers(app, staff),
    )

    assert response.status_code == 201


def seed_delete_targets(case, user):
    records = [
        ("client", Client(full_name="Delete Client"), "/api/clients/{id}"),
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
    staff = make_user("staff")
    solicitor = make_user("solicitor")
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
