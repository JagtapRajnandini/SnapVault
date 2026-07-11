# SnapVault/forms/auth_forms.py
#
# WTForms used for user registration and login.
# FlaskForm automatically adds CSRF protection to every form.

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)
from SnapVault.models.user import User


# ---------------------------------------------------------------------------
# Registration Form
# ---------------------------------------------------------------------------

class RegisterForm(FlaskForm):
    """Form used to create a new user account.

    Checks that:
    - All required fields are filled.
    - Username and email have valid lengths.
    - Email has a valid format.
    - Password is long enough.
    - Passwords match.
    - Username is not already taken.
    - Email is not already registered.
    """

    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(min=2, max=50, message="Username must be between 2 and 50 characters."),
        ],
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Please enter a valid email address."),
            Length(max=150, message="Email must be 150 characters or fewer."),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=6, message="Password must be at least 6 characters."),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    submit = SubmitField("Create Account")

    # WTForms automatically calls validate_<field_name>()
    # after the normal validators.

    def validate_username(self, username: StringField) -> None:
        """Check if the username already exists."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is already taken. Please choose a different one."
            )

    def validate_email(self, email: EmailField) -> None:
        """Check if the email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                "An account with that email already exists. Please log in instead."
            )


# ---------------------------------------------------------------------------
# Login Form
# ---------------------------------------------------------------------------

class LoginForm(FlaskForm):
    """Form used to log in an existing user.

    The username is not checked here.
    That check is done in the route so the application
    always shows the same login error message.
    """

    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(max=50),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
        ],
    )

    submit = SubmitField("Log In")