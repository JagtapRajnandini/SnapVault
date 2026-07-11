"""
Centralized Flask configuration.

This file contains only Flask and application configuration.
Application constants (categories, keywords, etc.) belong in
SnapVault/utils/constants.py.
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()


class Config:
    # ---------------- Security ----------------

    # Used by Flask to secure sessions and CSRF protection.
    # Uses the value from .env. The fallback is only for development.
    SECRET_KEY: str = (
        os.environ.get("SECRET_KEY")
        or "INSECURE-FALLBACK-KEY-SET-SECRET_KEY-IN-DOT-ENV"
    )

    # ---------------- Database ----------------

    # Database connection string.
    # Uses SQLite by default and can be replaced with PostgreSQL later.
    SQLALCHEMY_DATABASE_URI: str = (
        os.environ.get("DATABASE_URI")
        or "sqlite:///app.db"
    )

    # Disable modification tracking to improve performance.
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # ---------------- File Uploads ----------------

    # Absolute path to the uploads folder.
    UPLOAD_FOLDER: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "uploads",
    )

    # Maximum allowed upload size (16 MB).
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024