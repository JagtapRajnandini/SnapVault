from datetime import datetime
from SnapVault import db


class Reminder(db.Model):
    # Database table name.
    __tablename__ = 'reminder'

    # -------------------- Primary Key --------------------

    # Unique ID for each reminder.
    id = db.Column(db.Integer, primary_key=True)

    # -------------------- Owner --------------------

    # Foreign key to the User table.
    # Every Reminder belongs to one User.
    # If the User is deleted, all their Reminders are also deleted.
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
    )

    # -------------------- Linked Document --------------------

    # Foreign key to the Document table.
    # A Reminder can optionally be linked to a Document.
    # If the Document is deleted, this field becomes NULL.
    document_id = db.Column(
        db.Integer,
        db.ForeignKey('document.id', ondelete='SET NULL'),
        nullable=True,
    )

    # -------------------- Reminder Details --------------------

    # Short title of the reminder.
    title = db.Column(db.String(200), nullable=False)

    # Date when the reminder is due.
    # Stores only the date (no time).
    due_date = db.Column(db.Date, nullable=False)

    # -------------------- Status --------------------

    # Current reminder status.
    #
    # pending   -> Reminder is not completed.
    # completed -> Reminder has been completed.
    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending',
    )

    # -------------------- Timestamp --------------------

    # Time when the reminder was created.
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # -------------------- Debugging --------------------

    # String representation of a Reminder object.
    # Used only for debugging and logging.
    def __repr__(self) -> str:
        return (
            f'<Reminder id={self.id} '
            f'title={self.title!r} '
            f'due={self.due_date} '
            f'status={self.status!r}>'
        )