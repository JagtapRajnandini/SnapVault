# SnapVault/__init__.py
#
# Creates the Flask application and sets up everything
# needed before the application starts.

import sqlite3 as _sqlite3

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine

from SnapVault.config import Config


# Create the Flask application.
app = Flask(__name__)

# Load settings from config.py.
app.config.from_object(Config)

# Initialize Flask extensions.
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)

# Login configuration.
login_manager.login_view = 'login_page'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


# Enable foreign key support in SQLite.
# SQLite ignores FK constraints by default — this event listener runs
# PRAGMA foreign_keys=ON on every new connection so cascade deletes
# and SET NULL rules defined in the models are actually enforced.
@event.listens_for(Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, _sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


# Import all database models.
# Importing user.py also registers the @login_manager.user_loader callback
# defined at the bottom of that module.
from SnapVault.models.user import User          # noqa: F401, E402
from SnapVault.models.document import Document  # noqa: F401, E402
from SnapVault.models.reminder import Reminder  # noqa: F401, E402


# Create database tables if they do not already exist.
# db.create_all() is idempotent — safe to call on every startup.
with app.app_context():
    db.create_all()


# Custom error handlers for 404 and 500 errors.
from flask import render_template as _rt

@app.errorhandler(404)
def not_found_error(e):
    return _rt('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return _rt('errors/500.html'), 500


# Import routes after everything else is ready.
# Routes must be imported last to avoid circular imports —
# route files do "from SnapVault import app" which requires
# the app object to already exist before the import runs.
from SnapVault.routes import auth_routes      # noqa: F401, E402
from SnapVault.routes import document_routes  # noqa: F401, E402
from SnapVault.routes import dashboard_routes  # noqa: F401, E402
from SnapVault.routes import reminder_routes   # noqa: F401, E402