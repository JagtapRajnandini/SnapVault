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

# Load all project settings from config.py.
app.config.from_object(Config)

# Initialize Flask extensions.
db = SQLAlchemy(app)          # Database
bcrypt = Bcrypt(app)          # Password hashing
login_manager = LoginManager(app)   # User login management

# Redirect users to the login page if they try to access
# a protected page without logging in.
login_manager.login_view = 'login_page'

# Message shown when login is required.
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


# SQLite does not check foreign keys by default.
# This enables foreign key support every time
# a new database connection is created.
@event.listens_for(Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, _sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


# Import models so SQLAlchemy knows about all database tables.
from SnapVault.models.user import User
from SnapVault.models.document import Document
from SnapVault.models.reminder import Reminder


# Flask-Login calls this function to load the logged-in user.
#
# Day 1:
# No login system exists yet, so always return None.
#
# Day 2:
# Return the User object using its ID.
@login_manager.user_loader
def load_user(user_id):
    return None


# Create all database tables if they don't already exist.
with app.app_context():
    db.create_all()


# Import routes after everything else is ready.
# Keeping this at the end avoids circular imports.
from SnapVault.routes import auth_routes

# Day 3:
# from SnapVault.routes import document_routes

# Day 4:
# from SnapVault.routes import dashboard_routes

# Day 5:
# from SnapVault.routes import reminder_routes