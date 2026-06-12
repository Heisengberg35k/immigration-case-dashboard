from datetime import datetime, timezone
from .extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="staff")
    created_at = db.Column(db.DateTime, default=utc_now)


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(150), nullable=False)
    date_of_birth = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(150))
    address = db.Column(db.Text)
    preferred_contact_method = db.Column(db.String(50))
    whatsapp_number = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    cases = db.relationship(
        "Case",
        backref="client",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=False
    )

    application_type = db.Column(db.String(100), nullable=False)
    case_status = db.Column(db.String(100), default="New Consultation")

    assigned_lawyer = db.Column(db.String(120))
    assigned_staff = db.Column(db.String(120))

    home_office_reference = db.Column(db.String(120))
    main_deadline = db.Column(db.String(50))
    priority = db.Column(db.String(50), default="Normal")

    file_location = db.Column(db.Text)
    solicitor_review_status = db.Column(db.String(100), default="Not Reviewed")

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False
    )

    document_name = db.Column(db.String(150), nullable=False)
    required = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(80), default="Requested")
    source = db.Column(db.String(80))
    file_name = db.Column(db.String(255))
    file_location = db.Column(db.Text)
    received_date = db.Column(db.String(50))
    checked_by = db.Column(db.String(120))
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )


class Questionnaire(db.Model):
    __tablename__ = "questionnaires"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False
    )

    question = db.Column(db.Text, nullable=False)
    client_answer = db.Column(db.Text)
    status = db.Column(db.String(80), default="Not Asked")
    asked_date = db.Column(db.String(50))
    answered_date = db.Column(db.String(50))
    follow_up_needed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )


class Deadline(db.Model):
    __tablename__ = "deadlines"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False
    )

    deadline_type = db.Column(db.String(100), nullable=False)
    deadline_date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(80), default="Upcoming")
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False
    )

    appointment_date = db.Column(db.String(50), nullable=False)
    appointment_time = db.Column(db.String(50))
    appointment_location = db.Column(db.Text)
    appointment_type = db.Column(db.String(100))
    status = db.Column(db.String(80), default="Booked")
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False
    )

    total_fee = db.Column(db.Float, default=0)
    amount_paid = db.Column(db.Float, default=0)
    balance_due = db.Column(db.Float, default=0)
    payment_status = db.Column(db.String(80), default="Part Paid")
    next_payment_due = db.Column(db.String(50))
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )


class VisaReminder(db.Model):
    __tablename__ = "visa_reminders"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False
    )

    visa_granted_date = db.Column(db.String(50))
    visa_expiry_date = db.Column(db.String(50))
    reminder_date = db.Column(db.String(50))
    client_contacted = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    note_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    action = db.Column(db.String(120), nullable=False)
    entity_type = db.Column(db.String(120))
    entity_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=utc_now)
