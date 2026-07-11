# SnapVault/routes/auth_routes.py
#
# Routes for user authentication:
# Home, Register, Login, Logout, and Profile.

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from SnapVault import app, bcrypt, db
from SnapVault.forms.auth_forms import LoginForm, RegisterForm
from SnapVault.models.user import User


# ---------------------------------------------------------------------------
# Home Page
# ---------------------------------------------------------------------------
# Public home page.
# If the user is already logged in, send them to the dashboard.

@app.route('/')
@app.route('/home')
def home_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))

    return render_template('home.html')


# ---------------------------------------------------------------------------
# Register Page
# ---------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register_page():

    # Logged-in users should not access the registration page.
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))

    form = RegisterForm()

    if form.validate_on_submit():

        # Create a new user.
        # Assigning to user.password automatically hashes the password.
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.password = form.password.data

        db.session.add(user)
        db.session.commit()

        # Automatically log in the user after successful registration.
        login_user(user)

        flash(f'Account created! Welcome, {user.username}.', 'success')
        return redirect(url_for('dashboard_page'))

    return render_template('auth/register.html', form=form)


# ---------------------------------------------------------------------------
# Login Page
# ---------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login_page():

    # Logged-in users are redirected to the dashboard.
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))

    form = LoginForm()

    if form.validate_on_submit():

        # Find the user by username.
        user = User.query.filter_by(username=form.username.data).first()

        # Login succeeds only if both username and password are correct.
        # A single error message is shown for security.
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):

            login_user(user)
            flash('Logged in successfully.', 'success')

            # If the user was redirected here from a protected page,
            # return them to that page after login.
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard_page'))

        else:
            flash('Username and password do not match. Please try again.', 'danger')

    return render_template('auth/login.html', form=form)


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------
# Logs out the current user and returns them to the login page.

@app.route('/logout')
def logout_page():

    logout_user()

    flash('You have been logged out.', 'info')

    return redirect(url_for('login_page'))


# ---------------------------------------------------------------------------
# Profile Page
# ---------------------------------------------------------------------------
# Only logged-in users can access this page.

@app.route('/profile')
@login_required
def profile_page():
    return render_template('auth/profile.html')