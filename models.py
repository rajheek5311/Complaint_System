"""
models.py
----------
This file defines the DATABASE TABLES for our project using SQLAlchemy.
Think of each "class" below as one Excel sheet (table) in our database.
Each variable inside the class is a COLUMN in that sheet.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    """
    Table: user
    Stores every person who can log in: Admin, Agent, or normal User.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # role can be: 'admin', 'agent', 'user'
    role = db.Column(db.String(20), nullable=False, default='user')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: tickets this user created (as a customer)
    tickets_created = db.relationship(
        'Ticket', foreign_keys='Ticket.user_id', backref='creator', lazy=True
    )
    # Relationship: tickets assigned to this user (if they are an agent)
    tickets_assigned = db.relationship(
        'Ticket', foreign_keys='Ticket.assigned_agent_id', backref='agent', lazy=True
    )


class Ticket(db.Model):
    """
    Table: ticket
    Stores every complaint/ticket raised by a user.
    """
    id = db.Column(db.Integer, primary_key=True)

    # Unique human-readable ticket code, e.g. TCK-0001A2B3
    ticket_code = db.Column(db.String(20), unique=True, nullable=False)

    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Filled automatically by our AI logic
    category = db.Column(db.String(50), nullable=False, default='General')
    priority = db.Column(db.String(20), nullable=False, default='Low')

    # status can be: 'Open', 'In Progress', 'Resolved'
    status = db.Column(db.String(20), nullable=False, default='Open')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments = db.relationship('Comment', backref='ticket', lazy=True,
                                cascade='all, delete-orphan')


class Comment(db.Model):
    """
    Table: comment
    Stores every comment/reply written on a ticket
    (by the user who raised it, the agent, or the admin).
    """
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', foreign_keys=[user_id])
