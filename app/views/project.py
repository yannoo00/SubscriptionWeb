from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from app.models import Project, Notification, ProjectPost, ProjectComment, ProjectParticipant, ProjectProgress
from app.forms import ProjectForm, PostForm, CommentForm, ProjectParticipationForm, ContributionForm, AcceptParticipantForm, ProjectProgressForm, ProjectPlanForm
from werkzeug.utils import secure_filename
from app import db
import os

bp = Blueprint('project', __name__, url_prefix='/project')

@bp.route('/list')
@login_required
def list_projects():
    form = ProjectParticipationForm()
    projects = Project.query.all()
    return render_template('project/list.html', projects=projects, form=form)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(title=form.title.data, description=form.description.data, start_date=form.start_date.data, end_date=form.end_date.data, client=current_user)
        db.session.add(project)
        db.session.commit()
        flash('프로젝트가 생성되었습니다.', 'success')
        return redirect(url_for('project.detail', project_id=project.id))
    return render_template('project/create.html', form=form)

@bp.route('/create_post/<int:project_id>', methods=['POST'])
@login_required
def create_post(project_id):
    project = Project.query.get_or_404(project_id)
    form = PostForm()
    if form.validate_on_submit():
        post = ProjectPost(project=project, user=current_user, title=form.title.data, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        flash('게시글이 작성되었습니다.', 'success')
        return redirect(url_for('project.detail', project_id=project.id))
    else:
        flash('게시글 작성에 실패했습니다. 폼을 다시 확인해주세요.', 'error')
        return redirect(url_for('project.detail', project_id=project.id))

@bp.route('/create_comment/<int:post_id>', methods=['POST'])
@login_required
def create_comment(post_id):
    post = ProjectPost.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = ProjectComment(post=post, user=current_user, content=form.content.data)
        db.session.add(comment)
        db.session.commit()
        flash('댓글이 작성되었습니다.', 'success')
    return redirect(url_for('project.detail', project_id=post.project_id))

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
    post_form = PostForm()
    comment_form = CommentForm()
    contribution_form = ContributionForm()
    accept_form = AcceptParticipantForm()
    return render_template('project/detail.html', project=project, post_form=post_form, comment_form=comment_form, contribution_form = contribution_form, accept_form = accept_form)

@bp.route('/participate/<int:project_id>', methods=['POST'])
@login_required
def participate(project_id):
    project = Project.query.get_or_404(project_id)
    participant = ProjectParticipant.query.filter_by(user=current_user, project=project).first()
    if participant:
        if participant.accepted:
            flash('이미 프로젝트에 참여 중입니다.', 'warning')
        else:
            flash('이미 참가 신청을 하였습니다.', 'warning')
    else:
        new_participant = ProjectParticipant(user=current_user, project=project)
        db.session.add(new_participant)
        db.session.commit()
        flash('프로젝트 참가 신청이 완료되었습니다.', 'success')
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

@bp.route('/contribute/<int:project_id>', methods=['POST'])
@login_required
def contribute(project_id):
    project = Project.query.get_or_404(project_id)
    form = ContributionForm()
    if form.validate_on_submit():
        participant = ProjectParticipant.query.filter_by(user=current_user, project=project).first()
        if participant:
            if participant.hours_contributed is None:
                participant.hours_contributed = form.hours.data
            else:
                participant.hours_contributed += form.hours.data
            db.session.commit()
            flash('참여 시간이 기록되었습니다.', 'success')
        else:
            flash('프로젝트에 참여한 회원만 참여 시간을 기록할 수 있습니다.', 'warning')
    return redirect(url_for('project.detail', project_id=project_id))

@bp.route('/accept_participant/<int:project_id>', methods=['POST'])
@login_required
def accept_participant(project_id):
    project = Project.query.get_or_404(project_id)
    form = AcceptParticipantForm()

    if form.validate_on_submit():
        user_id = form.user_id.data

        if project.client != current_user:
            flash('프로젝트 생성자만 참가 신청을 수락할 수 있습니다.', 'error')
        else:
            participant = ProjectParticipant.query.filter_by(user_id=user_id, project_id=project_id).first()
            if participant:
                participant.accepted = True
                db.session.commit()
                flash(f'{participant.user.name}님의 참가 신청을 수락하였습니다.', 'success')
            else:
                flash('해당 사용자의 참가 신청이 존재하지 않습니다.', 'warning')
    else:
        flash('잘못된 요청입니다.', 'error')

    return redirect(url_for('project.detail', project_id=project_id))

@bp.route('/progress/<int:project_id>', methods=['GET', 'POST'])
@login_required
def progress(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user not in project.participants and current_user != project.client:
        flash('프로젝트 참여자와 의뢰자만 진행상황을 볼 수 있습니다.', 'warning')
        return redirect(url_for('project.detail', project_id=project_id))
    
    form = ProjectProgressForm()
    if form.validate_on_submit():
        progress = ProjectProgress(project=project, user=current_user, date=form.date.data, description=form.description.data)
        db.session.add(progress)
        db.session.commit()
        flash('진행상황이 성공적으로 기록되었습니다.', 'success')
        return redirect(url_for('project.progress', project_id=project_id))
    
    progress_list = ProjectProgress.query.filter_by(project=project).order_by(ProjectProgress.date.desc()).all()
    return render_template('project/progress.html', project=project, form=form, progress_list=progress_list)


@bp.route('/plan/<int:project_id>', methods=['GET', 'POST'])
@login_required
def plan(project_id):
    project = Project.query.get_or_404(project_id)
    
    form = ProjectPlanForm()
    
    if form.validate_on_submit():
        project.overview = form.overview.data
        project.flowchart = form.flowchart.data
        db.session.commit()
        
        flash('프로젝트 기획이 성공적으로 저장되었습니다.', 'success')
        return redirect(url_for('project.detail', project_id=project_id))
    
    form.overview.data = project.overview
    form.flowchart.data = project.flowchart
    
    return render_template('project/plan.html', project=project, form=form)