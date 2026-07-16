"""
app.py
-------
This is the MAIN file you run to start the website.
It:
1. Creates the Flask app
2. Connects the SQLite database
3. Sets up login system
4. Registers all the route "blueprints" (auth, user, admin, agent)
5. Creates the database tables automatically if they don't exist
6. Creates a default ADMIN account automatically (so you always have one)

To run this file, see the "HOW TO RUN" instructions given in chat.
"""

import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

from models import db, User
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.agent import agent_bp

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Secret key is used by Flask to keep login sessions secure.
# In a real production project, this should be a long random string
# stored as an environment variable, not written in code.
app.config['SECRET_KEY'] = 'change-this-secret-key-in-production'

# Tell Flask-SQLAlchemy where our SQLite database file lives.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---- Login manager setup ----
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---- Register blueprints (this "plugs in" all our route files) ----
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(agent_bp)


@app.route('/')
def home():
    # Sends visitors straight to the login page.
    return redirect(url_for('auth.login'))


@app.errorhandler(403)
def forbidden(e):
    return "<h2>403 - You don't have permission to view this page.</h2>", 403


@app.errorhandler(404)
def not_found(e):
    return "<h2>404 - Page not found.</h2>", 404


def create_default_admin():
    """
    Runs once at startup. If there is no admin account yet,
    it creates one automatically so you can always log in as admin.

    Default Admin Login:
        Email:    admin@example.com
        Password: admin123
    """
    existing_admin = User.query.filter_by(role='admin').first()
    if not existing_admin:
        admin = User(
            name='System Admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('>>> Default admin created: admin@example.com / admin123')


with app.app_context():
    db.create_all()
    create_default_admin()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
