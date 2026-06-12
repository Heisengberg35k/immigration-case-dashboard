from app import create_app
from app.extensions import db
from app.models import (
    User,
    Firm,
    Client,
    Case,
    Document,
    Questionnaire,
    Deadline,
    Appointment,
    Payment,
    VisaReminder,
    Note,
    AuditLog
)
import bcrypt


app = create_app()


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def make_client(
    full_name,
    date_of_birth,
    phone,
    email,
    address,
    contact_method,
    application_type,
    case_status,
    lawyer,
    staff,
    reference,
    deadline,
    priority,
    review_status
):
    slug = full_name.replace(" ", "")

    return {
        "client": {
            "full_name": full_name,
            "date_of_birth": date_of_birth,
            "phone": phone,
            "email": email,
            "address": address,
            "preferred_contact_method": contact_method,
            "whatsapp_number": phone
        },
        "case": {
            "application_type": application_type,
            "case_status": case_status,
            "assigned_lawyer": lawyer,
            "assigned_staff": staff,
            "home_office_reference": reference,
            "main_deadline": deadline,
            "priority": priority,
            "file_location": f"SharedDrive/Clients/2026/{slug}",
            "solicitor_review_status": review_status
        }
    }


with app.app_context():
    print("Clearing old seed data...")

    AuditLog.query.delete()
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
    Firm.query.delete()

    db.session.commit()

    print("Creating firm and users...")

    firm = Firm(name="Demo Immigration Firm")
    db.session.add(firm)
    db.session.commit()

    users = [
        User(
            firm_id=firm.id,
            name="Admin User",
            email="admin@firm.com",
            password_hash=hash_password("Password123"),
            role="admin"
        ),
        User(
            firm_id=firm.id,
            name="Mr Rahman",
            email="solicitor@firm.com",
            password_hash=hash_password("Password123"),
            role="solicitor"
        ),
        User(
            firm_id=firm.id,
            name="Junior Staff 1",
            email="staff@firm.com",
            password_hash=hash_password("Password123"),
            role="staff"
        ),
        User(
            firm_id=firm.id,
            name="Caseworker Test",
            email="caseworker@firm.com",
            password_hash=hash_password("Password123"),
            role="staff"
        ),
        User(
            firm_id=firm.id,
            name="Senior Solicitor",
            email="senior@firm.com",
            password_hash=hash_password("Password123"),
            role="solicitor"
        )
    ]

    db.session.add_all(users)
    db.session.commit()

    admin, solicitor, staff, caseworker, senior = users

    print("Creating clients and cases...")

    seed_clients = [
        make_client(
            "Labib Khan",
            "1995-04-12",
            "07123456789",
            "labib@example.com",
            "Stratford, London",
            "WhatsApp",
            "FLR(M)",
            "Documents Requested",
            "Mr Rahman",
            "Junior Staff 1",
            "HO123456",
            "2026-06-15",
            "High",
            "Not Reviewed"
        ),
        make_client(
            "Amina Begum",
            "1990-09-22",
            "07234567890",
            "amina@example.com",
            "Whitechapel, London",
            "Email",
            "Skilled Worker",
            "Questionnaire Sent",
            "Mr Rahman",
            "Caseworker Test",
            "HO654321",
            "2026-06-20",
            "Medium",
            "Not Reviewed"
        ),
        make_client(
            "Rashid Ali",
            "1988-01-15",
            "07345678901",
            "rashid@example.com",
            "Ilford, London",
            "WhatsApp",
            "ILR",
            "Solicitor Review",
            "Senior Solicitor",
            "Junior Staff 1",
            "HO998877",
            "2026-06-05",
            "High",
            "Pending Review"
        ),
        make_client(
            "Sara Ahmed",
            "1998-11-03",
            "07456789012",
            "sara@example.com",
            "Croydon, London",
            "Email",
            "Student Visa",
            "Ready for Submission",
            "Mr Rahman",
            "Caseworker Test",
            "HO112233",
            "2026-06-10",
            "Medium",
            "Reviewed"
        ),
        make_client(
            "Tariq Hussain",
            "1985-07-19",
            "07567890123",
            "tariq@example.com",
            "Barking, London",
            "WhatsApp",
            "Citizenship",
            "Visa Granted",
            "Senior Solicitor",
            "Junior Staff 1",
            "HO445566",
            "2026-05-01",
            "Low",
            "Reviewed"
        ),
        make_client(
            "Maya Patel",
            "1992-02-18",
            "07678901234",
            "maya@example.com",
            "Harrow, London",
            "Email",
            "Spouse Visa",
            "Waiting Documents",
            "Mr Rahman",
            "Junior Staff 1",
            "HO778899",
            "2026-06-12",
            "High",
            "Not Reviewed"
        ),
        make_client(
            "Omar Farooq",
            "1983-12-01",
            "07789012345",
            "omar@example.com",
            "East Ham, London",
            "WhatsApp",
            "Asylum Support",
            "Active",
            "Senior Solicitor",
            "Caseworker Test",
            "HO121212",
            "2026-06-30",
            "High",
            "Pending Review"
        ),
        make_client(
            "Nadia Islam",
            "1996-08-26",
            "07890123456",
            "nadia@example.com",
            "Tower Hamlets, London",
            "Email",
            "Graduate Visa",
            "New Consultation",
            "Mr Rahman",
            "Junior Staff 1",
            "HO343434",
            "2026-07-04",
            "Normal",
            "Not Reviewed"
        ),
        make_client(
            "Chen Wei",
            "1991-03-09",
            "07901234567",
            "chen@example.com",
            "Canary Wharf, London",
            "Email",
            "Global Talent",
            "Documents Requested",
            "Senior Solicitor",
            "Caseworker Test",
            "HO565656",
            "2026-06-18",
            "Medium",
            "Not Reviewed"
        ),
        make_client(
            "Elena Popescu",
            "1989-10-30",
            "07012345678",
            "elena@example.com",
            "Wembley, London",
            "WhatsApp",
            "EU Settlement Scheme",
            "Completed",
            "Mr Rahman",
            "Junior Staff 1",
            "HO787878",
            "2026-05-20",
            "Low",
            "Reviewed"
        )
    ]

    created_cases = []

    for item in seed_clients:
        client = Client(firm_id=firm.id, **item["client"])
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
            file_location="SharedDrive/Clients/2026/LabibKhan/01_ID_Documents",
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
        ),
        Document(
            case_id=created_cases[5].id,
            document_name="Marriage Certificate",
            required=True,
            status="Requested",
            source="Other",
            notes="Required for spouse visa evidence."
        ),
        Document(
            case_id=created_cases[8].id,
            document_name="Endorsement Letter",
            required=True,
            status="Received",
            source="Email",
            file_name="ChenWei_Endorsement.pdf",
            checked_by="Caseworker Test",
            notes="Needs solicitor review."
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
        ),
        Questionnaire(
            case_id=created_cases[6].id,
            question="Please list all current dependants.",
            client_answer="",
            status="Unclear",
            asked_date="2026-06-01",
            follow_up_needed=True,
            notes="Need complete dependant details."
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
        ),
        Deadline(
            case_id=created_cases[5].id,
            deadline_type="Upload Deadline",
            deadline_date="2026-06-10",
            status="Overdue",
            notes="Spouse visa bundle still incomplete."
        ),
        Deadline(
            case_id=created_cases[8].id,
            deadline_type="Solicitor Review",
            deadline_date="2026-06-10",
            status="Due Soon",
            notes="Review endorsement evidence today."
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
            appointment_date="2026-06-12",
            appointment_time="14:00",
            appointment_location="Online",
            appointment_type="Final Review Call",
            status="Booked",
            notes="Review application before submission."
        ),
        Appointment(
            case_id=created_cases[7].id,
            appointment_date="2026-06-18",
            appointment_time="11:00",
            appointment_location="Office",
            appointment_type="Initial Consultation",
            status="Booked",
            notes="New consultation follow-up."
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
        ),
        Payment(
            case_id=created_cases[5].id,
            total_fee=1800,
            amount_paid=900,
            balance_due=900,
            payment_status="Part Paid",
            next_payment_due="2026-06-21",
            notes="Second instalment due after document review."
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
        ),
        VisaReminder(
            case_id=created_cases[9].id,
            visa_granted_date="2025-12-10",
            visa_expiry_date="2026-12-10",
            reminder_date="2026-06-10",
            client_contacted=False,
            notes="Reminder due today for EUSS follow-up."
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
            user_id=caseworker.id,
            note_text="Need clearer copy of Certificate of Sponsorship."
        ),
        Note(
            case_id=created_cases[2].id,
            user_id=solicitor.id,
            note_text="Application ready for solicitor review."
        ),
        Note(
            case_id=created_cases[8].id,
            user_id=senior.id,
            note_text="Global Talent evidence should be reviewed before upload."
        )
    ]

    db.session.add_all(notes)
    db.session.commit()

    print("Seed data created successfully.")
    print("")
    print("Login details:")
    print("Admin: admin@firm.com / Password123")
    print("Solicitor: solicitor@firm.com / Password123")
    print("Senior solicitor: senior@firm.com / Password123")
    print("Staff: staff@firm.com / Password123")
    print("Caseworker: caseworker@firm.com / Password123")
    print("")
    print("Access testing notes:")
    print("Admin can access Users and Audit Log.")
    print("Solicitor can access Audit Log and delete protected records.")
    print("Staff can work on cases but cannot access Users/Audit Log or delete protected records.")
