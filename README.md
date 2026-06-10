# Immigration Case Dashboard

Internal case management dashboard for a UK immigration law practice.

The app currently includes staff authentication, clients, cases, document tracking with secure uploads, questionnaires, deadlines and reminders, appointments, payments, visa reminders, notes, reports, audit logs, and basic role-based access.

## Stack

- Backend: Flask, Flask-SQLAlchemy, Flask-Migrate, PostgreSQL, JWT, bcrypt
- Frontend: Angular standalone components
- Storage: PostgreSQL for metadata, private local filesystem for uploaded files in development

## Security Notes

- Never commit `backend/.env`.
- Use a strong random `JWT_SECRET_KEY` of at least 32 bytes.
- Do not expose `backend/uploads` as a public static directory.
- Run migrations with Flask-Migrate instead of relying on automatic table creation.
- Use HTTPS, private object storage, backups, and audit monitoring before real client use.
- Rotate all development secrets before production.

## Backend Setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` with your local PostgreSQL password and a private `JWT_SECRET_KEY`.

Create or upgrade the database:

```powershell
$env:FLASK_APP="run.py"
flask db upgrade
```

Seed test data:

```powershell
python seed_data.py
```

Run the backend:

```powershell
python run.py
```

Backend URL:

```text
http://127.0.0.1:5000
```

Health check:

```text
http://127.0.0.1:5000/api/health
```

## Frontend Setup

```powershell
cd frontend\frontend
npm install
npm start
```

Frontend URL:

```text
http://127.0.0.1:4200
```

## Test Login Details

These are development seed users only:

```text
Admin:            admin@firm.com / Password123
Solicitor:        solicitor@firm.com / Password123
Senior solicitor: senior@firm.com / Password123
Staff:            staff@firm.com / Password123
Caseworker:       caseworker@firm.com / Password123
```

Access expectations:

- Admin can access Users and Audit Log.
- Solicitor can access Audit Log and delete protected records.
- Staff can work on cases but cannot access Users/Audit Log or delete protected records.

## Migrations

Create a new migration after model changes:

```powershell
cd backend
$env:FLASK_APP="run.py"
flask db migrate -m "Describe change"
flask db upgrade
```

For an existing database that already has the current schema but no migration version table, use care. In development you can reseed from scratch. In production, back up first and use Alembic stamping only after confirming the schema matches the migration.

## Environment Variables

See [backend/.env.example](backend/.env.example).

Important variables:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`
- `UPLOAD_FOLDER`
- `MAX_UPLOAD_SIZE_BYTES`
- `AUTO_CREATE_TABLES`
- `FLASK_DEBUG`

## Uploaded Documents

Development uploads are stored privately under:

```text
backend/uploads/cases/<case_id>/<uuid>.<ext>
```

Uploaded documents are accessed through protected API download routes, not direct public URLs.
