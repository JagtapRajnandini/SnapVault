from datetime import datetime
from SnapVault import db


class User(db.Model):
    # db.Column -> Creates a database column.
    # db.relationship -> Creates a Python relationship between database tables.

    # Database table name.
    __tablename__ = 'user'

    # Primary key (auto-incremented).
    id = db.Column(db.Integer, primary_key=True)

    # Username must be unique and cannot be NULL.
    username = db.Column(db.String(50), unique=True, nullable=False)

    # Email must be unique and cannot be NULL.
    email = db.Column(db.String(150), unique=True, nullable=False)

    # Stores the HASHED password, never the actual password.
    password_hash = db.Column(db.String(128), nullable=False)

    # Time when the account was created.
    # Pass datetime.utcnow (not datetime.utcnow()) so SQLAlchemy
    # calls the function when a new row is inserted.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Automatically updated whenever this row changes.
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # One User can own many Documents.
    # Access:
    #   user.documents  -> list of Document objects
    #   document.owner  -> corresponding User
    #
    # lazy=True:
    #   Documents are loaded only when user.documents is accessed.
    #
    # cascade='all, delete-orphan':
    #   Delete User      -> delete all Documents.
    #   Remove Document from user.documents -> delete that Document.
    #   Delete Document  -> User is NOT deleted.
    documents = db.relationship(
        'Document',
        backref='owner',
        lazy=True,
        cascade='all, delete-orphan',
    )

    # One User can own many Reminders.
    # Same behaviour as the documents relationship.
    reminders = db.relationship(
        'Reminder',
        backref='owner',
        lazy=True,
        cascade='all, delete-orphan',
    )

    # String representation of a User object.
    # Used only for debugging and logging.
    def __repr__(self) -> str:
        return f'<User id={self.id} username={self.username!r}>'