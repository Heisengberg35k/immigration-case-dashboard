import os
from dotenv import load_dotenv

load_dotenv()


def parse_bool(value, default=False):
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value != 0

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on"
    }


def parse_csv(value, default=None):
    if not value:
        return default or []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


class Config:
    DEBUG = parse_bool(
        os.getenv("FLASK_DEBUG"),
        default=False
    )

    SECRET_KEY = (
        os.getenv("JWT_SECRET_KEY")
        or os.getenv("SECRET_KEY")
        or "dev-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///immigration.db",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTO_CREATE_TABLES = parse_bool(
        os.getenv("AUTO_CREATE_TABLES"),
        default=False
    )
    CORS_ORIGINS = parse_csv(
        os.getenv("CORS_ORIGINS"),
        [
            "http://localhost:4200",
            "http://127.0.0.1:4200"
        ]
    )

    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "uploads"
        )
    )
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_UPLOAD_SIZE_BYTES", 10 * 1024 * 1024)
    )
    ALLOWED_DOCUMENT_EXTENSIONS = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
    }
