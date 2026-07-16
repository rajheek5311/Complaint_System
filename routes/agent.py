"""
routes/agent.py
------------------
Handles everything a 'Support Agent' can do:
- See dashboard of tickets ASSIGNED to them
- Update status of their tickets
- Add comments / replies
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user

from models import db, Ticket, Comment
from utils.email_utils import send_email

agent_bp = Blueprint('agent', __name__, url_prefix='/agent')


def agent_required():
    if current_user.role != 'agent':
        abort(403)


@agent_bp.route('/dashboard')
@login_required
def dashboard():
    agent_required()

    my_tickets = Ticket.query.filter_by(assigned_agent_id=current_user.id) \
        .order_by(Ticket.created_at.desc()).all()

    total = len(my_tickets)
    open_count = len([t for t in my_tickets if t.status == 'Open'])
    progress_count = len([t for t in my_tickets if t.status == 'In Progress'])
    resolved_count = len([t for t in my_tickets if t.status == 'Resolved'])

    return render_template(
        'agent_dashboard.html',
        tickets=my_tickets,
        total=total, open_count=open_count,
        progress_count=progress_count, resolved_count=resolved_count
    )


@agent_bp.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_detail(ticket_id):
    agent_required()
    ticket = Ticket.query.get_or_404(ticket_id)

    # An agent may only manage tickets assigned to them.
    if ticket.assigned_agent_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'status':
            new_status = request.form.get('status')
            if new_status in ('Open', 'In Progress', 'Resolved'):
                ticket.status = new_status
                db.session.commit()

                send_email(
                    to_address=ticket.creator.email,
                    subject=f'Ticket {ticket.ticket_code} Status Update',
                    body=f'Your ticket status changed to: {new_status}'
                )
                flash(f'Status updated to {new_status}.', 'success')

        elif action == 'comment':
            text = request.form.get('comment', '').strip()
            if text:
                comment = Comment(ticket_id=ticket.id, user_id=current_user.id, text=text)
                db.session.add(comment)
                db.session.commit()
                flash('Reply added.', 'success')

        return redirect(url_for('agent.ticket_detail', ticket_id=ticket.id))

    return render_template('ticket_detail.html', ticket=ticket, is_agent_view=True)
