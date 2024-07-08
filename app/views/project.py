from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from app.models import Project, Notification, ProjectPost, ProjectComment, ProjectParticipant, ProjectProgress
from app.forms import ProjectForm, PostForm, CommentForm, ProjectParticipationForm, ContributionForm, AcceptParticipantForm, ProjectProgressForm, ProjectPlanForm, ParticipateForm, CodeSaveForm, CodeEditForm
from werkzeug.utils import secure_filename
from app import db
import os
from github import Github, GithubException

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

        # GitHub 리포지토리 생성
        github_token = current_app.config['GITHUB_ACCESS_TOKEN']
        g = Github(github_token)
        user = g.get_user()
        try:
            repo = user.create_repo(project.title, private=False, auto_init=True)
            project.github_repo = repo.full_name
            db.session.commit()
            flash(f'프로젝트와 GitHub 리포지토리 {repo.full_name}가 생성되었습니다.', 'success')
        except Exception as e:
            flash(f'GitHub 리포지토리 생성 중 오류가 발생했습니다: {str(e)}', 'error')

        return redirect(url_for('project.detail', project_id=project.id))
    return render_template('project/create.html', form=form)

@bp.route('/save_code/<int:project_id>', methods=['GET', 'POST'])
@login_required
def save_code(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.github_repo:
        flash('이 프로젝트에는 연결된 GitHub 리포지토리가 없습니다.', 'error')
        return redirect(url_for('project.detail', project_id=project.id))

    github_token = current_app.config['GITHUB_ACCESS_TOKEN']
    g = Github(github_token)
    repo = g.get_repo(project.github_repo)

    # 파일 목록 가져오기
    files = []
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            files.append(file_content)

    form = CodeSaveForm()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'new_file':
            if form.validate_on_submit():
                code_content = form.code.data
                file_name = form.file_name.data
                branch_name = form.branch_name.data
                commit_message = form.commit_message.data

                try:
                    # 브랜치 확인 및 생성
                    try:
                        repo.get_branch(branch_name)
                    except GithubException as e:
                        if e.status == 404:
                            default_branch = repo.get_branch(repo.default_branch)
                            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=default_branch.commit.sha)
                            flash(f'새로운 브랜치 "{branch_name}"가 생성되었습니다.', 'info')
                        else:
                            raise

                    # 새 파일 생성
                    repo.create_file(file_name, commit_message, code_content, branch=branch_name)
                    flash(f'새 파일 "{file_name}"이 생성되었습니다.', 'success')

                except GithubException as e:
                    flash(f'GitHub 작업 중 오류가 발생했습니다: {e.data.get("message", str(e))}', 'error')
                    current_app.logger.error(f'GitHub 오류: {str(e)}')
                except Exception as e:
                    flash(f'예상치 못한 오류가 발생했습니다: {str(e)}', 'error')
                    current_app.logger.error(f'예상치 못한 오류: {str(e)}')

            else:
                flash('폼 데이터가 유효하지 않습니다.', 'error')

        elif action == 'edit_file':
            file_path = request.form.get('file_path')
            content = request.form.get('edit_content')
            branch_name = request.form.get('edit_branch_name')
            commit_message = request.form.get('edit_commit_message')

            if file_path and content and branch_name and commit_message:
                try:
                    # 파일 업데이트
                    contents = repo.get_contents(file_path, ref=branch_name)
                    repo.update_file(contents.path, commit_message, content, contents.sha, branch=branch_name)
                    flash(f'파일 "{file_path}"이 업데이트되었습니다.', 'success')

                except GithubException as e:
                    flash(f'GitHub 작업 중 오류가 발생했습니다: {e.data.get("message", str(e))}', 'error')
                    current_app.logger.error(f'GitHub 오류: {str(e)}')
                except Exception as e:
                    flash(f'예상치 못한 오류가 발생했습니다: {str(e)}', 'error')
                    current_app.logger.error(f'예상치 못한 오류: {str(e)}')
            else:
                flash('필요한 모든 필드를 입력해주세요.', 'error')

        return redirect(url_for('project.detail', project_id=project.id))

    return render_template('project/save_code.html', form=form, project=project, files=files)



@bp.route('/get_file_content/<int:project_id>', methods=['GET', 'POST'])
@login_required
def get_file_content(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        file_path = request.form.get('file_path')
    else:
        file_path = request.args.get('file_path')
    
    github_token = current_app.config['GITHUB_ACCESS_TOKEN']
    g = Github(github_token)
    repo = g.get_repo(project.github_repo)

    try:
        content = repo.get_contents(file_path)
        return content.decoded_content.decode('utf-8')
    except Exception as e:
        return str(e), 400

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
    participate_form = ParticipateForm()
    return render_template('project/detail.html', project=project, post_form=post_form, comment_form=comment_form, contribution_form = contribution_form, accept_form = accept_form, form=participate_form)

@bp.route('/participate/<int:project_id>', methods=['POST'])
@login_required
def participate(project_id):
    form = ParticipateForm()
    if form.validate_on_submit():
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
    else:
        flash('CSRF 토큰이 유효하지 않습니다. 다시 시도해주세요.', 'error')
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