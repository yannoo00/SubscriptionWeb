from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from app.models import Project, Course, ProjectSubmission, Notification
from app.forms import ProjectForm
from werkzeug.utils import secure_filename
from app import db
import os

bp = Blueprint('project', __name__, url_prefix='/project')

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project_select():
    if not current_user.is_teacher():
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('project.list'))

    courses = current_user.courses
    return render_template('project/create_select.html', courses=courses)

@bp.route('/list')
@login_required
def list():
    if current_user.is_teacher():
        courses = current_user.courses
        projects = Project.query.filter(Project.course_id.in_([course.id for course in courses])).all()
    else:
        enrollments = current_user.enrollments
        projects = Project.query.filter(Project.course_id.in_([enrollment.course_id for enrollment in enrollments])).all()

    return render_template('project/list.html', projects=projects)


@bp.route('/create/<int:course_id>', methods=['GET', 'POST'])
@login_required
def create_project(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher != current_user:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('project.list'))

    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(title=form.title.data, description=form.description.data,
                          start_date=form.start_date.data, end_date=form.end_date.data,
                          course_id=course_id)
        db.session.add(project)
        db.session.commit()

        for enrollment in course.enrollments:
            notification = Notification.query.filter_by(user_id=enrollment.student_id, message=f"{course.title} 강좌에 새로운 프로젝트가 등록되었습니다: {project.title}").first()
            if not notification:
                notification = Notification(user_id=enrollment.student_id, 
                                            message=f"{course.title} 강좌에 새로운 프로젝트가 등록되었습니다: {project.title}")
                db.session.add(notification)
                db.session.commit()
                socketio = current_app.extensions['socketio']
                socketio.emit('new_notification', {'message': notification.message}, room=str(enrollment.student_id))

        flash('프로젝트가 생성되었습니다.', 'success')
        return redirect(url_for('project.list'))

    return render_template('project/create.html', form=form, course=course)
@bp.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.course.teacher != current_user:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('mypage.index'))

    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        db.session.commit()
        flash('프로젝트가 수정되었습니다.', 'success')
        return redirect(url_for('mypage.index'))

    return render_template('project/edit.html', form=form, project=project)

@bp.route('/delete/<int:project_id>')
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.course.teacher != current_user:
        flash('권한이 없습니다.', 'error')
    else:
        db.session.delete(project)
        db.session.commit()
        flash('프로젝트가 삭제되었습니다.', 'success')
    return redirect(url_for('mypage.index'))

@bp.route('/detail/<int:project_id>')
@login_required
def detail(project_id):
    project = Project.query.get_or_404(project_id)
    submissions = ProjectSubmission.query.filter_by(project_id=project_id).all()
    return render_template('project/detail.html', project=project, submissions=submissions)

@bp.route('/submissions/<int:project_id>')
@login_required
def submissions(project_id):
    project = Project.query.get_or_404(project_id)
    if project.course.teacher != current_user:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('project.list'))
    submissions = ProjectSubmission.query.filter_by(project_id=project_id).all()
    return render_template('project/submissions.html', project=project, submissions=submissions)

@bp.route('/submit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def submit(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            submission = ProjectSubmission(project_id=project_id, student_id=current_user.id, file_path=file_path)
            db.session.add(submission)
            db.session.commit()
            flash('프로젝트가 제출되었습니다.', 'success')
            return redirect(url_for('project.detail', project_id=project_id))
        else:
            flash('파일을 선택해주세요.', 'error')
    return render_template('project/submit.html', project=project)

@bp.route('/download/<int:submission_id>')
@login_required
def download_submission(submission_id):
    submission = ProjectSubmission.query.get_or_404(submission_id)
    if submission.project.course.teacher != current_user:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('project.detail', project_id=submission.project.id))
    return send_file(submission.file_path, as_attachment=True)