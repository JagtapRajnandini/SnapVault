import sqlite3 as _sqlite3

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

from SnapVault.config import Config

# ── 1. Create the Flask application ──────────────────────────────────────────
app = Flask(__name__)

# ── 2. Load configuration ─────────────────────────────────────────────────────
app.config.from_object(Config)

# ── 3. Initialise extensions ──────────────────────────────────────────────────
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = 'login_page'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# ── 4. SQLite foreign-key enforcement ─────────────────────────────────────────
# SQLite ignores FK constraints by default.  This event listener runs
# PRAGMA foreign_keys=ON on every new connection so that:
#   ondelete='CASCADE'  (User -> Document, User -> Reminder)  actually deletes
#   ondelete='SET NULL' (Document -> Reminder.document_id)    actually nullifies
# The isinstance guard makes this a no-op for PostgreSQL in a future version.

@event.listens_for(Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, _sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


# ── 5. Import models ──────────────────────────────────────────────────────────
# noqa comments suppress "imported but unused" linter warnings; these imports
# are intentional — they register the model classes with SQLAlchemy's metadata.
from SnapVault.models.user import User          # noqa: F401, E402
from SnapVault.models.document import Document  # noqa: F401, E402
from SnapVault.models.reminder import Reminder  # noqa: F401, E402

# ── 6. Register user_loader with Flask-Login ──────────────────────────────────
# Flask-Login requires user_loader to be registered before ANY template that
# references current_user is rendered — including public pages — because the
# current_user context processor fires on every single request.
#
# Day 1 behaviour: returns None so current_user is always Flask-Login's
# AnonymousUserMixin (is_authenticated=False).  Correct: no login routes exist.
#
# Day 2 change: replace `return None` with:
#     return User.query.get(int(user_id))
# AND add UserMixin to the User model class in app/models/user.py so
# Flask-Login can call .is_authenticated on the returned object.

@login_manager.user_loader
def load_user(user_id):
    # Day 1 stub — treats every request as unauthenticated.
    return None


# ── 7. Create database tables ─────────────────────────────────────────────────
# db.create_all() is idempotent — safe on every startup; skips existing tables.
# Flask auto-creates the instance/ folder (where SQLite writes app.db).
with app.app_context():
    db.create_all()

# ── 8. Import routes ──────────────────────────────────────────────────────────
# Must be last to avoid circular imports (routes do `from app import app`).
from SnapVault.routes import auth_routes  # noqa: F401, E402
# Day 4: from app.routes import dashboard_routes
# Day 3: from app.routes import document_routes
# Day 5: from app.routes import reminder_routes