import os
from dotenv import load_dotenv

load_dotenv()


class Config:
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

    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "uploads"
    )
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ALLOWED_DOCUMENT_EXTENSIONS = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
    }
