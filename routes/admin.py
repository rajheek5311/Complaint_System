"""
routes/admin.py
------------------
Handles everything the 'admin' can do:
- See analytics dashboard (all tickets, chart data)
- Assign a ticket to a Support Agent
- Change ticket status
- View all users
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user

from models import db, Ticket, User, Comment
from utils.email_utils import send_email

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required():
    if current_user.role != 'admin':
        abort(403)


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    admin_required()

    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    agents = User.query.filter_by(role='agent').all()

    total = len(tickets)
    open_count = len([t for t in tickets if t.status == 'Open'])
    progress_count = len([t for t in tickets if t.status == 'In Progress'])
    resolved_count = len([t for t in tickets if t.status == 'Resolved'])

    high = len([t for t in tickets if t.priority == 'High'])
    medium = len([t for t in tickets if t.priority == 'Medium'])
    low = len([t for t in tickets if t.priority == 'Low'])

    technical = len([t for t in tickets if t.category == 'Technical'])
    billing = len([t for t in tickets if t.category == 'Billing'])
    general = len([t for t in tickets if t.category == 'General'])

    return render_template(
        'admin_dashboard.html',
        tickets=tickets,
        agents=agents,
        total=total, open_count=open_count,
        progress_count=progress_count, resolved_count=resolved_count,
        high=high, medium=medium, low=low,
        technical=technical, billing=billing, general=general
    )


@admin_bp.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_detail(ticket_id):
    admin_required()
    ticket = Ticket.query.get_or_404(ticket_id)
    agents = User.query.filter_by(role='agent').all()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'assign':
            agent_id = request.form.get('agent_id')
            if agent_id:
                agent = User.query.get(int(agent_id))
                ticket.assigned_agent_id = agent.id
                if ticket.status == 'Open':
                    ticket.status = 'In Progress'
                db.session.commit()

                send_email(
                    to_address=agent.email,
                    subject=f'New Ticket Assigned: {ticket.ticket_code}',
                    body=f'You have been assigned ticket "{ticket.subject}".'
                )
                send_email(
                    to_address=ticket.creator.email,
                    subject=f'Ticket {ticket.ticket_code} Update',
                    body=f'Your ticket has been assigned to agent {agent.name}.'
                )
                flash(f'Ticket assigned to {agent.name}.', 'success')

        elif action == 'status':
            new_status = request.form.get('status')
            if new_status in ('Open', 'In Progress', 'Resolved'):
                ticket.status = new_status
                db.session.commit()
                flash(f'Status updated to {new_status}.', 'success')

        elif action == 'comment':
            text = request.form.get('comment', '').strip()
            if text:
                comment = Comment(ticket_id=ticket.id, user_id=current_user.id, text=text)
                db.session.add(comment)
                db.session.commit()
                flash('Comment added.', 'success')

        return redirect(url_for('admin.ticket_detail', ticket_id=ticket.id))

    return render_template('ticket_detail.html', ticket=ticket, agents=agents, is_admin_view=True)


@admin_bp.route('/users')
@login_required
def manage_users():
    admin_required()
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('manage_users.html', users=users)
