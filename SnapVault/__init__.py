# SnapVault/__init__.py
#
# Creates the Flask application and sets up everything
# needed before the application starts.
#
# Day 2:
# - Removed the temporary user_loader from this file.
# - The real user_loader is now inside models/user.py.

import sqlite3 as _sqlite3

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
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

# Login configuration.
login_manager.login_view = 'login_page'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


# Enable foreign key support in SQLite.
@event.listens_for(Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, _sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


# Import all database models.
# Importing user.py also registers the user_loader.
from SnapVault.models.user import User
from SnapVault.models.document import Document
from SnapVault.models.reminder import Reminder


# Create database tables if they do not already exist.
with app.app_context():
    db.create_all()


# Import routes after everything else is ready.
# This avoids circular imports.
from SnapVault.routes import auth_routes

# Day 3:
# from SnapVault.routes import document_routes

# Day 4:
# from SnapVault.routes import dashboard_routes

# Day 5:
# from SnapVault.routes import reminder_routes