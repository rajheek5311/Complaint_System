"""
routes/auth.py
----------------
Handles: Register page, Login page, Logout.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard_redirect'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user')

        # Basic validation
        if not name or not email or not password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('auth.register'))

        # Only allow 'user' or 'agent' signup from the public form.
        # (Admin accounts are created via seed_db.py, not this public form,
        #  so random visitors can't make themselves Admin.)
        if role not in ('user', 'agent'):
            role = 'user'

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('An account with this email already exists. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard_redirect'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('auth.dashboard_redirect'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
@login_required
def dashboard_redirect():
    """
    Sends each logged-in user to the correct dashboard
    based on their role.
    """
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'agent':
        return redirect(url_for('agent.dashboard'))
    else:
        return redirect(url_for('user.dashboard'))
