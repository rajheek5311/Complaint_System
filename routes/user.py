"""
routes/user.py
----------------
Handles everything a normal 'user' (customer) can do:
- See their dashboard
- Raise a new complaint
- Track their tickets
- View one ticket + add comments
"""

import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user

from models import db, Ticket, Comment
from utils.ai_logic import classify_complaint
from utils.email_utils import send_email

user_bp = Blueprint('user', __name__, url_prefix='/user')


def role_required(role):
    """Small helper: block access if current_user's role doesn't match."""
    if current_user.role != role:
        abort(403)


def generate_ticket_code():
    """Creates a short, unique, human-friendly ticket ID like TCK-9F3A2B."""
    return 'TCK-' + uuid.uuid4().hex[:8].upper()


@user_bp.route('/dashboard')
@login_required
def dashboard():
    role_required('user')

    my_tickets = Ticket.query.filter_by(user_id=current_user.id) \
        .order_by(Ticket.created_at.desc()).all()

    total = len(my_tickets)
    open_count = len([t for t in my_tickets if t.status == 'Open'])
    progress_count = len([t for t in my_tickets if t.status == 'In Progress'])
    resolved_count = len([t for t in my_tickets if t.status == 'Resolved'])

    return render_template(
        'user_dashboard.html',
        tickets=my_tickets,
        total=total,
        open_count=open_count,
        progress_count=progress_count,
        resolved_count=resolved_count
    )


@user_bp.route('/complaint/new', methods=['GET', 'POST'])
@login_required
def new_complaint():
    role_required('user')

    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()

        if not subject or not description:
            flash('Please fill in both subject and description.', 'danger')
            return redirect(url_for('user.new_complaint'))

        # ---- AI LOGIC RUNS HERE ----
        result = classify_complaint(subject, description)

        ticket = Ticket(
            ticket_code=generate_ticket_code(),
            subject=subject,
            description=description,
            category=result['category'],
            priority=result['priority'],
            status='Open',
            user_id=current_user.id
        )
        db.session.add(ticket)
        db.session.commit()

        # Dummy email notification
        send_email(
            to_address=current_user.email,
            subject=f'Ticket {ticket.ticket_code} Created',
            body=(f'Your complaint "{subject}" was received. '
                  f'Priority: {ticket.priority}, Category: {ticket.category}.')
        )

        flash(f'Complaint submitted! Your ticket ID is {ticket.ticket_code} '
              f'(Priority: {ticket.priority}, Category: {ticket.category}).', 'success')
        return redirect(url_for('user.track_tickets'))

    return render_template('complaint_form.html')


@user_bp.route('/tickets')
@login_required
def track_tickets():
    role_required('user')
    my_tickets = Ticket.query.filter_by(user_id=current_user.id) \
        .order_by(Ticket.created_at.desc()).all()
    return render_template('ticket_tracking.html', tickets=my_tickets)


@user_bp.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # Security check: a normal user may only view THEIR OWN ticket.
    # (Admin/Agent have their own separate ticket_detail routes.)
    if current_user.role == 'user' and ticket.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        text = request.form.get('comment', '').strip()
        if text:
            comment = Comment(ticket_id=ticket.id, user_id=current_user.id, text=text)
            db.session.add(comment)
            db.session.commit()
            flash('Comment added.', 'success')
        return redirect(url_for('user.ticket_detail', ticket_id=ticket.id))

    return render_template('ticket_detail.html', ticket=ticket)
