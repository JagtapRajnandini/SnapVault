from datetime import datetime

from flask_login import UserMixin

from SnapVault import bcrypt, db, login_manager


class User(UserMixin, db.Model):
    # UserMixin adds Flask-Login features like:
    # is_authenticated, is_active, is_anonymous and get_id().

    # Database table name.
    __tablename__ = "user"

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
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

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
        "Document",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan",
    )

    # One User can own many Reminders.
    # Same behaviour as the documents relationship.
    reminders = db.relationship(
        "Reminder",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan",
    )

    # Returns the stored password hash.
    # Routes should never use this directly.
    @property
    def password(self):
        return self.password_hash

    # Automatically hashes the password before saving it.
    # Example:
    #   user.password = "mypassword"
    # The database stores only the hash.
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(
            plain_text_password
        ).decode("utf-8")

    # String representation of a User object.
    # Used only for debugging and logging.
    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"


@login_manager.user_loader
def load_user(user_id):
    # Flask-Login calls this after a user logs in.
    # It loads the user from the database using the stored user ID.
    return User.query.get(int(user_id))