from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Assignment
from app import db
from datetime import datetime

bp = Blueprint('mentorship', __name__)

@bp.route('/')
@login_required
def index():
    users = User.query.all()
    return render_template('mentorship/index.html', users=users)

@bp.route('/request_mentorship/<int:mentor_id>', methods=['POST'])
@login_required
def request_mentorship(mentor_id):
    mentor = User.query.get_or_404(mentor_id)
    if mentor == current_user:
        flash('자기 자신에게는 멘토링을 신청할 수 없습니다.', 'error')
    else:
        current_user.mentor = mentor
        db.session.commit()
        flash(f'{mentor.name}님에게 멘토링을 신청했습니다.', 'success')
    return redirect(url_for('mentorship.index'))

@bp.route('/assign_task', methods=['GET', 'POST'])
@login_required
def assign_task():
    if request.method == 'POST':
        mentee_id = request.form['mentee_id']
        title = request.form['title']
        description = request.form['description']
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d')

        assignment = Assignment(mentor=current_user, mentee_id=mentee_id, title=title, description=description, deadline=deadline)
        db.session.add(assignment)
        db.session.commit()

        flash('과제가 성공적으로 할당되었습니다.', 'success')
        return redirect(url_for('mentorship.assigned_tasks'))

    mentees = current_user.mentees
    return render_template('mentorship/assign_task.html', mentees=mentees)

@bp.route('/assigned_tasks')
@login_required
def assigned_tasks():
    tasks = current_user.given_assignments
    return render_template('mentorship/assigned_tasks.html', tasks=tasks)

@bp.route('/received_tasks')
@login_required
def received_tasks():
    tasks = current_user.received_assignments
    return render_template('mentorship/received_tasks.html', tasks=tasks)

@bp.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Assignment.query.get_or_404(task_id)
    if task.mentee != current_user:
        flash('이 과제를 완료할 권한이 없습니다.', 'error')
    else:
        task.completed = True
        db.session.commit()
        flash('과제를 완료하였습니다.', 'success')
    return redirect(url_for('mentorship.received_tasks'))