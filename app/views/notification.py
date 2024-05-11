from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Notification



bp = Blueprint('notification', __name__, url_prefix='/notification')

@bp.route('/')
@login_required
def index():
    notifications = Notification.query.filter_by(user=current_user).order_by(Notification.created_at.desc()).all()
    return render_template('notification/index.html', notifications=notifications)

@bp.route('/read/<int:notification_id>')
@login_required
def read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user == current_user:
        notification.read = True
        db.session.commit()
    return redirect(url_for('notification.index'))

