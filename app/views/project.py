from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from app.models import Project, Notification
from app.forms import ProjectForm
from werkzeug.utils import secure_filename
from app import db
import os

bp = Blueprint('project', __name__, url_prefix='/project')

@bp.route('/list')
@login_required
def list_projects():
    projects = current_user.projects
    return render_template('project/list.html', projects=projects)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(title=form.title.data, description=form.description.data, client=current_user)
        db.session.add(project)
        db.session.commit()
        flash('프로젝트가 생성되었습니다.', 'success')
        
        # 프로젝트 생성 알림 보내기
        notification = Notification(user=current_user, message=f'새 프로젝트가 생성되었습니다: {project.title}')
        db.session.add(notification)
        db.session.commit()
        
        return redirect(url_for('project.detail', project_id=project.id))
    return render_template('project/create.html', form=form)

@bp.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.client != current_user:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('project.detail', project_id=project.id))
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        db.session.commit()
        flash('프로젝트가 수정되었습니다.', 'success')
        return redirect(url_for('project.detail', project_id=project.id))
    return render_template('project/edit.html', form=form, project=project)

@bp.route('/delete/<int:project_id>')
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.client != current_user:
        flash('권한이 없습니다.', 'error')
    else:
        db.session.delete(project)
        db.session.commit()
        flash('프로젝트가 삭제되었습니다.', 'success')
    return redirect(url_for('project.list_projects'))

@bp.route('/detail/<int:project_id>')
@login_required
def detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project/detail.html', project=project)

@bp.route('/participate/<int:project_id>')
@login_required
def participate(project_id):
    project = Project.query.get_or_404(project_id)
    project.participants.append(current_user)
    db.session.commit()
    flash('프로젝트에 참여하였습니다.', 'success')
    
    # 프로젝트 참여 알림 보내기
    notification = Notification(user=project.client, message=f'{current_user.name}님이 프로젝트 {project.title}에 참여하였습니다.')
    db.session.add(notification)
    db.session.commit()
    
    return redirect(url_for('project.detail', project_id=project_id))

@bp.route('/complete/<int:project_id>')
@login_required
def complete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.client != current_user:
        flash('권한이 없습니다.', 'error')
    else:
        project.completed = True
        db.session.commit()
        flash('프로젝트를 완료하였습니다.', 'success')
        
        # 프로젝트 완료 알림 보내기
        for participant in project.participants:
            notification = Notification(user=participant, message=f'프로젝트 {project.title}이(가) 완료되었습니다.')
            db.session.add(notification)
        db.session.commit()
        
    return redirect(url_for('project.detail', project_id=project_id))