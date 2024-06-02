from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory, current_app, send_file
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from app.models import User, Assignment
from app.forms import AssignTaskForm, RequestMentorshipForm, AcceptMentorshipForm, SubmitTaskForm
from app import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os

bp = Blueprint('mentorship', __name__)

@bp.route('/')
@login_required
def index():
    users = User.query.all()
    request_form = RequestMentorshipForm()
    accept_form = AcceptMentorshipForm()
    return render_template('mentorship/index.html', users=users, request_form=request_form, accept_form=accept_form)

@bp.route('/request_mentorship/<int:mentor_id>', methods=['POST'])
@login_required
def request_mentorship(mentor_id):
    form = RequestMentorshipForm()
    if form.validate_on_submit():
        mentor = User.query.get_or_404(mentor_id)
        if mentor == current_user:
            flash('자기 자신에게는 멘토링을 신청할 수 없습니다.', 'error')
        else:
            if current_user not in mentor.pending_mentees and current_user not in mentor.mentees:
                mentor.pending_mentees.append(current_user)
                db.session.commit()
                flash(f'{mentor.name}님에게 멘토링을 신청했습니다.', 'success')
            else:
                flash(f'{mentor.name}님에게는 이미 멘토링을 신청했거나 멘토링 관계입니다.', 'warning')
    else:
        flash('잘못된 요청입니다.', 'error')
    return redirect(url_for('mentorship.index'))

@bp.route('/accept_mentorship/<int:mentee_id>', methods=['POST'])
@login_required
def accept_mentorship(mentee_id):
    form = AcceptMentorshipForm()
    if form.validate_on_submit():
        mentee = User.query.get_or_404(mentee_id)
        if mentee in current_user.pending_mentees:
            if current_user.mentees.count() < 2:
                if mentee not in current_user.mentees:
                    current_user.mentees.append(mentee)
                    current_user.pending_mentees.remove(mentee)
                    db.session.commit()
                    flash(f'{mentee.name}님의 멘토링 신청을 수락했습니다.', 'success')
                else:
                    flash(f'{mentee.name}님과는 이미 멘토링 관계입니다.', 'warning')
            else:
                flash('멘티는 최대 2명까지만 가능합니다.', 'error')
        else:
            flash('잘못된 요청입니다.', 'error')
    else:
        flash('잘못된 요청입니다.', 'error')
    return redirect(url_for('mentorship.index'))

@bp.route('/assigned_tasks')
@login_required
def assigned_tasks():
    tasks = current_user.given_assignments
    return render_template('mentorship/assigned_tasks.html', tasks=tasks)

@bp.route('/received_tasks')
@login_required
def received_tasks():
    tasks = current_user.received_assignments
    form = SubmitTaskForm()
    return render_template('mentorship/received_tasks.html', tasks=tasks, form=form)

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

@bp.route('/my_mentoring')
@login_required
def my_mentoring():
    return render_template('mentorship/my_mentoring.html')

@bp.route('/download_file/<path:filename>')
@login_required
def download_file(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    print(f"File path: {file_path}")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('요청한 파일이 존재하지 않습니다.', 'error')
        return redirect(url_for('mentorship.assigned_tasks'))

@bp.route('/assign_task', methods=['GET', 'POST'])
@login_required
def assign_task():
    form = AssignTaskForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        deadline = form.deadline.data
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['_FOLDER'], filename)
            file.save(file_path)
        else:
            file_path = None
        
        if not current_user.mentees.all():
            flash('멘티가 없어서 과제를 할당할 수 없습니다.', 'error')
            return redirect(url_for('mentorship.assign_task'))
        
        for mentee in current_user.mentees:
            assignment = Assignment(mentor=current_user, mentee=mentee, title=title, description=description, deadline=deadline, file=file_path)
            db.session.add(assignment)
        
        db.session.commit()
        
        flash('과제가 성공적으로 할당되었습니다.', 'success')
        return redirect(url_for('mentorship.assigned_tasks'))
    
    return render_template('mentorship/assign_task.html', form=form)

@bp.route('/submit_task/<int:task_id>', methods=['POST'])
@login_required
def submit_task(task_id):
    task = Assignment.query.get_or_404(task_id)
    form = SubmitTaskForm()
    if form.validate_on_submit():  
        if task.mentee != current_user:
            flash('이 과제를 제출할 권한이 없습니다.', 'error')
        else:
            file = form.file.data
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                task.file = filename  # 실제 파일명과 확장자를 포함하도록 수정
                task.completed = True
                db.session.commit()
                flash('과제를 성공적으로 제출하였습니다.', 'success')
            else:
                flash('제출할 파일을 선택해주세요.', 'error')
    return redirect(url_for('mentorship.received_tasks'))