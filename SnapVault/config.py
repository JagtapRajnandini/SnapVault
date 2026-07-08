"""
app/config.py — Centralised application configuration.

All uppercase attributes on Config are loaded into app.config by
app/__init__.py via app.config.from_object(Config).

Domain-level constants (CATEGORY_KEYWORDS, ALLOWED_EXTENSIONS, etc.)
live in app/utils/constants.py, not here. This file contains only
infrastructure / framework configuration values.
"""
import os
from dotenv import load_dotenv

# Load variables from .env into os.environ before anything reads them.
# Has no effect if .env does not exist (safe for production environments
# that inject secrets via the shell rather than a file).
load_dotenv()


class Config:
    # ── Security ────────────────────────────────────────────────────────────
    # Flask uses SECRET_KEY to sign session cookies and CSRF tokens.
    # The fallback string is only reached if .env is missing entirely;
    # it is intentionally ugly so it is obvious in logs that it is wrong.
    SECRET_KEY: str = (
        os.environ.get('SECRET_KEY')
        or 'INSECURE-FALLBACK-KEY-SET-SECRET_KEY-IN-DOT-ENV'
    )

    # ── Database ─────────────────────────────────────────────────────────────
    # sqlite:///app.db (three slashes = relative to Flask's instance/ folder).
    # Flask auto-creates the instance/ folder at startup.
    # Swap for a PostgreSQL URI in the future without touching anything else.
    SQLALCHEMY_DATABASE_URI: str = (
        os.environ.get('DATABASE_URI')
        or 'sqlite:///app.db'
    )

    # Disable modification tracking — saves memory, not needed for this project.
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # ── File uploads ─────────────────────────────────────────────────────────
    # Absolute path to the uploads/ directory at the project root.
    # __file__ is app/config.py → dirname once = app/ → dirname twice = project root.
    UPLOAD_FOLDER: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'uploads'
    )

    # Flask rejects any request body larger than this with HTTP 413.
    # 16 MB covers essentially every real screenshot or photo.
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB