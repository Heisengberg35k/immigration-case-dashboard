from app import create_app
from app.extensions import db
from app.models import (
    User,
    Client,
    Case,
    Document,
    Questionnaire,
    Deadline,
    Appointment,
    Payment,
    VisaReminder,
    Note
)
import bcrypt


app = create_app()


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


with app.app_context():
    print("Clearing old seed data...")

    Note.query.delete()
    VisaReminder.query.delete()
    Payment.query.delete()
    Appointment.query.delete()
    Deadline.query.delete()
    Questionnaire.query.delete()
    Document.query.delete()
    Case.query.delete()
    Client.query.delete()
    User.query.delete()

    db.session.commit()

    print("Creating users...")

    admin = User(
        name="Admin User",
        email="admin@firm.com",
        password_hash=hash_password("Password123"),
        role="admin"
    )

    solicitor = User(
        name="Mr Rahman",
        email="solicitor@firm.com",
        password_hash=hash_password("Password123"),
        role="solicitor"
    )

    staff = User(
        name="Junior Staff 1",
        email="staff@firm.com",
        password_hash=hash_password("Password123"),
        role="staff"
    )

    db.session.add_all([admin, solicitor, staff])
    db.session.commit()

    print("Creating clients and cases...")

    seed_clients = [
        {
            "client": {
                "full_name": "Labib Khan",
                "date_of_birth": "1995-04-12",
                "phone": "07123456789",
                "email": "labib@example.com",
                "address": "Stratford, London",
                "preferred_contact_method": "WhatsApp",
                "whatsapp_number": "07123456789"
            },
            "case": {
                "application_type": "FLR(M)",
                "case_status": "Documents Requested",
                "assigned_lawyer": "Mr Rahman",
                "assigned_staff": "Junior Staff 1",
                "home_office_reference": "HO123456",
                "main_deadline": "2026-06-15",
                "priority": "High",
                "file_location": "SharedDrive/Clients/2026/LabibKhan_FLRM",
                "solicitor_review_status": "Not Reviewed"
            }
        },
        {
            "client": {
                "full_name": "Amina Begum",
                "date_of_birth": "1990-09-22",
                "phone": "07234567890",
                "email": "amina@example.com",
                "address": "Whitechapel, London",
                "preferred_contact_method": "Email",
                "whatsapp_number": "07234567890"
            },
            "case": {
                "application_type": "Skilled Worker",
                "case_status": "Questionnaire Sent",
                "assigned_lawyer": "Mr Rahman",
                "assigned_staff": "Junior Staff 1",
                "home_office_reference": "HO654321",
                "main_deadline": "2026-06-20",
                "priority": "Medium",
                "file_location": "SharedDrive/Clients/2026/AminaBegum_SW",
                "solicitor_review_status": "Not Reviewed"
            }
        },
        {
            "client": {
                "full_name": "Rashid Ali",
                "date_of_birth": "1988-01-15",
                "phone": "07345678901",
                "email": "rashid@example.com",
                "address": "Ilford, London",
                "preferred_contact_method": "WhatsApp",
                "whatsapp_number": "07345678901"
            },
            "case": {
                "application_type": "ILR",
                "case_status": "Solicitor Review",
                "assigned_lawyer": "Mr Rahman",
                "assigned_staff": "Junior Staff 1",
                "home_office_reference": "HO998877",
                "main_deadline": "2026-06-05",
                "priority": "High",
                "file_location": "SharedDrive/Clients/2026/RashidAli_ILR",
                "solicitor_review_status": "Pending Review"
            }
        },
        {
            "client": {
                "full_name": "Sara Ahmed",
                "date_of_birth": "1998-11-03",
                "phone": "07456789012",
                "email": "sara@example.com",
                "address": "Croydon, London",
                "preferred_contact_method": "Email",
                "whatsapp_number": "07456789012"
            },
            "case": {
                "application_type": "Student Visa",
                "case_status": "Ready for Submission",
                "assigned_lawyer": "Mr Rahman",
                "assigned_staff": "Junior Staff 1",
                "home_office_reference": "HO112233",
                "main_deadline": "2026-06-10",
                "priority": "Medium",
                "file_location": "SharedDrive/Clients/2026/SaraAhmed_StudentVisa",
                "solicitor_review_status": "Reviewed"
            }
        },
        {
            "client": {
                "full_name": "Tariq Hussain",
                "date_of_birth": "1985-07-19",
                "phone": "07567890123",
                "email": "tariq@example.com",
                "address": "Barking, London",
                "preferred_contact_method": "WhatsApp",
                "whatsapp_number": "07567890123"
            },
            "case": {
                "application_type": "Citizenship",
                "case_status": "Visa Granted",
                "assigned_lawyer": "Mr Rahman",
                "assigned_staff": "Junior Staff 1",
                "home_office_reference": "HO445566",
                "main_deadline": "2026-05-01",
                "priority": "Low",
                "file_location": "SharedDrive/Clients/2026/TariqHussain_Citizenship",
                "solicitor_review_status": "Reviewed"
            }
        }
    ]

    created_cases = []

    for item in seed_clients:
        client = Client(**item["client"])
        db.session.add(client)
        db.session.flush()

        case = Case(
            client_id=client.id,
            **item["case"]
        )
        db.session.add(case)
        db.session.flush()

        created_cases.append(case)

    db.session.commit()

    print("Creating documents...")

    documents = [
        Document(
            case_id=created_cases[0].id,
            document_name="Passport",
            required=True,
            status="Received",
            source="WhatsApp",
            file_name="LabibKhan_Passport_2026-05-28.pdf",
            file_location="SharedDrive/Clients/2026/LabibKhan_FLRM/01_ID_Documents",
            received_date="2026-05-28",
            checked_by="Junior Staff 1",
            notes="Clear scan received."
        ),
        Document(
            case_id=created_cases[0].id,
            document_name="Signed Letter of Authority",
            required=True,
            status="Missing",
            source="Other",
            notes="Client has not signed yet."
        ),
        Document(
            case_id=created_cases[1].id,
            document_name="Certificate of Sponsorship",
            required=True,
            status="Needs Rescan",
            source="Email",
            file_name="AminaBegum_COS_Blurry.pdf",
            notes="Document is blurry and needs a clearer copy."
        ),
        Document(
            case_id=created_cases[2].id,
            document_name="Life in the UK Test",
            required=True,
            status="Checked",
            source="Physical",
            file_name="RashidAli_LifeInUK_Checked.pdf",
            checked_by="Junior Staff 1",
            notes="Checked and accepted."
        ),
        Document(
            case_id=created_cases[3].id,
            document_name="CAS Letter",
            required=True,
            status="Uploaded",
            source="Email",
            file_name="SaraAhmed_CAS_Uploaded.pdf",
            checked_by="Junior Staff 1",
            notes="Uploaded to application portal."
        )
    ]

    db.session.add_all(documents)

    print("Creating questionnaires...")

    questionnaires = [
        Questionnaire(
            case_id=created_cases[0].id,
            question="Please confirm your current UK address.",
            client_answer="",
            status="Asked",
            asked_date="2026-05-28",
            follow_up_needed=True,
            notes="Required for application form."
        ),
        Questionnaire(
            case_id=created_cases[1].id,
            question="Please provide your employment start date.",
            client_answer="",
            status="Still Missing",
            asked_date="2026-05-27",
            follow_up_needed=True,
            notes="Needed for Skilled Worker application."
        ),
        Questionnaire(
            case_id=created_cases[2].id,
            question="Please provide your travel history for the last 5 years.",
            client_answer="Travelled to Bangladesh in 2023 for 3 weeks.",
            status="Answered",
            asked_date="2026-05-25",
            answered_date="2026-05-27",
            follow_up_needed=False,
            notes="Answer received."
        )
    ]

    db.session.add_all(questionnaires)

    print("Creating deadlines...")

    deadlines = [
        Deadline(
            case_id=created_cases[0].id,
            deadline_type="Upload Deadline",
            deadline_date="2026-06-15",
            status="Upcoming",
            notes="Upload all documents before biometric appointment."
        ),
        Deadline(
            case_id=created_cases[1].id,
            deadline_type="Follow-up Deadline",
            deadline_date="2026-06-03",
            status="Due Soon",
            notes="Follow up for missing employment start date."
        ),
        Deadline(
            case_id=created_cases[2].id,
            deadline_type="Review Deadline",
            deadline_date="2026-06-04",
            status="Due Soon",
            notes="Solicitor review required before submission."
        )
    ]

    db.session.add_all(deadlines)

    print("Creating appointments...")

    appointments = [
        Appointment(
            case_id=created_cases[0].id,
            appointment_date="2026-06-20",
            appointment_time="10:30",
            appointment_location="Croydon UKVCAS Centre",
            appointment_type="Biometric Appointment",
            status="Booked",
            notes="Client must bring passport."
        ),
        Appointment(
            case_id=created_cases[3].id,
            appointment_date="2026-06-08",
            appointment_time="14:00",
            appointment_location="Online",
            appointment_type="Final Review Call",
            status="Booked",
            notes="Review application before submission."
        )
    ]

    db.session.add_all(appointments)

    print("Creating payments...")

    payments = [
        Payment(
            case_id=created_cases[0].id,
            total_fee=1200,
            amount_paid=500,
            balance_due=700,
            payment_status="Payment Plan",
            next_payment_due="2026-06-10",
            notes="Remaining balance to be paid in two instalments."
        ),
        Payment(
            case_id=created_cases[1].id,
            total_fee=1500,
            amount_paid=1500,
            balance_due=0,
            payment_status="Paid",
            next_payment_due=None,
            notes="Paid in full."
        ),
        Payment(
            case_id=created_cases[2].id,
            total_fee=1000,
            amount_paid=400,
            balance_due=600,
            payment_status="Overdue",
            next_payment_due="2026-05-25",
            notes="Payment overdue. Staff to follow up."
        )
    ]

    db.session.add_all(payments)

    print("Creating visa reminders...")

    visa_reminders = [
        VisaReminder(
            case_id=created_cases[4].id,
            visa_granted_date="2026-05-01",
            visa_expiry_date="2029-05-01",
            reminder_date="2028-11-01",
            client_contacted=False,
            notes="Contact client 6 months before expiry."
        )
    ]

    db.session.add_all(visa_reminders)

    print("Creating notes...")

    notes = [
        Note(
            case_id=created_cases[0].id,
            user_id=staff.id,
            note_text="Client sent passport via WhatsApp. LOA still missing."
        ),
        Note(
            case_id=created_cases[1].id,
            user_id=staff.id,
            note_text="Need clearer copy of Certificate of Sponsorship."
        ),
        Note(
            case_id=created_cases[2].id,
            user_id=solicitor.id,
            note_text="Application ready for solicitor review."
        )
    ]

    db.session.add_all(notes)
    db.session.commit()

    print("Seed data created successfully.")
    print("")
    print("Login details:")
    print("Admin: admin@firm.com / Password123")
    print("Solicitor: solicitor@firm.com / Password123")
    print("Staff: staff@firm.com / Password123")