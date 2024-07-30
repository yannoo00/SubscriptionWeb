from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, send_from_directory
from flask_login import login_required, current_user
from app.models import Project, Notification, ProjectPost, ProjectComment, ProjectParticipant, ProjectProgress
from app.forms import ProjectForm, PostForm, CommentForm, ProjectParticipationForm, ContributionForm, AcceptParticipantForm, ProjectProgressForm, ProjectPlanForm, ParticipateForm, CodeSaveForm, EmptyForm
from app import db
from app.views.github_integration import get_github_repo, get_branches_internal, get_files_internal, create_github_file, update_github_file, get_file_content, create_github_repo
from github import Github
from github.GithubException import GithubException
from werkzeug.utils import secure_filename
import os

bp = Blueprint('project', __name__, url_prefix='/project')

@bp.route('/list')
@login_required
def list_projects():
    form = ProjectParticipationForm()
    collaboration_projects = Project.query.filter_by(type='collaboration').all()
    public_study_projects = Project.query.filter_by(type='study', is_public=True).all()
    return render_template('project/list.html', collaboration_projects=collaboration_projects, study_projects=public_study_projects, form=form)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    type = request.args.get('type', 'study')  # 기본값을 'study'로 설정

    if type == 'collaboration' and not current_user.is_admin:
        flash('협업 프로젝트는 관리자만 생성할 수 있습니다.', 'danger')
        return redirect(url_for('project.list_projects'))

    form = ProjectForm()
    if form.validate_on_submit():
        # 먼저 Project 객체를 생성합니다
        project = Project(
            title=form.title.data, 
            description=form.description.data, 
            start_date=form.start_date.data, 
            end_date=form.end_date.data, 
            client=current_user,
            type=type,
            is_public=form.is_public.data if type == 'study' else True
        )
        db.session.add(project)
        db.session.commit()

        # GitHub 리포지토리 생성 및 연결
        success, repo_name, message = create_github_repo(project.title, project.description)
        if success:
            project.github_repo = repo_name
            db.session.commit()
            flash(f'새 {type} 프로젝트가 생성되고 GitHub 리포지토리가 연결되었습니다. {message}', 'success')
            return redirect(url_for('project.detail', project_id=project.id))
        else:
            flash(f'프로젝트는 생성되었지만 GitHub 리포지토리 연결에 실패했습니다. {message}', 'warning')
            return redirect(url_for('project.detail', project_id=project.id))
    
    return render_template('project/create.html', form=form, project_type=type)

@bp.route('/detail/<int:project_id>', methods=['GET', 'POST'])
@login_required
def detail(project_id):
    project = Project.query.get_or_404(project_id)
    post_form = PostForm()
    comment_form = CommentForm()
    contribution_form = ContributionForm()
    accept_form = AcceptParticipantForm()
    participate_form = ParticipateForm()
    progress_form = ProjectProgressForm()
    empty_form = EmptyForm()  # EmptyForm 인스턴스 생성

    if request.method == 'POST':
        if 'submit_progress' in request.form:
            if progress_form.validate_on_submit():
                filename = None
                if progress_form.image.data:
                    file = progress_form.image.data
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)

                conversation_filename = None
                if progress_form.ai_conversation_file.data:
                    conversation_file = progress_form.ai_conversation_file.data
                    conversation_filename = secure_filename(conversation_file.filename)
                    conversation_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], conversation_filename)
                    conversation_file.save(conversation_file_path)

                new_progress = ProjectProgress(
                    project=project,
                    user=current_user,
                    date=progress_form.date.data,
                    description=progress_form.description.data,
                    image=filename,
                    ai_conversation_link=progress_form.ai_conversation_link.data,
                    ai_conversation_file=conversation_filename
                )
                db.session.add(new_progress)
                db.session.commit()
                flash('진행 상황이 성공적으로 기록되었습니다.', 'success')

    progress_list = ProjectProgress.query.filter_by(project=project).order_by(ProjectProgress.date.desc()).all()

    return render_template('project/detail.html', project=project, post_form=post_form, comment_form=comment_form,
                           contribution_form=contribution_form, accept_form=accept_form, 
                           participate_form=participate_form,
                           progress_form=progress_form,
                           progress_list=progress_list,
                           form=empty_form)  # EmptyForm을 'form'으로 전달

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

@bp.route('/get_branches/<int:project_id>')
@login_required
def get_branches_api(project_id):
    project = Project.query.get_or_404(project_id)
    repo = get_github_repo(project)
    branches = get_branches_internal(repo)
    return jsonify(branches)

@bp.route('/create_branch/<int:project_id>', methods=['POST'])
@login_required
def create_branch(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.github_repo:
        return jsonify({'success': False, 'message': '이 프로젝트에는 연결된 GitHub 리포지토리가 없습니다.'})

    repo = get_github_repo(project)
    new_branch_name = request.form.get('new_branch_name')

    try:
        # 먼저 기본 브랜치를 가져오려고 시도합니다
        default_branch = repo.get_branch(repo.default_branch)
    except GithubException as e:
        if e.status == 404:
            # 기본 브랜치가 없는 경우, 빈 커밋을 만들어 기본 브랜치를 생성합니다
            try:
                repo.create_file("README.md", "Initial commit", "# " + project.title, branch="main")
                default_branch = repo.get_branch("main")
            except GithubException as e:
                return jsonify({'success': False, 'message': f'기본 브랜치 생성 실패: {str(e)}'})
        else:
            return jsonify({'success': False, 'message': f'기본 브랜치 가져오기 실패: {str(e)}'})

    try:
        repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=default_branch.commit.sha)
        return jsonify({'success': True, 'message': f'새 브랜치 "{new_branch_name}"가 생성되었습니다.'})
    except GithubException as e:
        return jsonify({'success': False, 'message': f'브랜치 생성 실패: {str(e)}'})
@bp.route('/save_code/<int:project_id>', methods=['GET', 'POST'])
@login_required
def save_code(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.github_repo:
        return jsonify({'success': False, 'message': '이 프로젝트에는 연결된 GitHub 리포지토리가 없습니다.'})

    repo = get_github_repo(project)
    branches = get_branches_internal(repo)
    
    form = CodeSaveForm()
    form.branch_name.choices = [(branch, branch) for branch in branches]

    if request.method == 'POST':
        action = request.form.get('action') 

        if action == '새 파일 저장':
            if form.validate_on_submit():
                success, message = create_github_file(repo, form.file_name.data, form.code.data, form.branch_name.data, form.commit_message.data)
                return jsonify({'success': success, 'message': message})
            else:
                return jsonify({'success': False, 'message': '폼 유효성 검사 실패', 'errors': form.errors})

        elif action == '파일 수정':
            file_path = request.form.get('file_path')
            content = request.form.get('edit_content')
            branch_name = request.form.get('edit_branch_name')
            commit_message = request.form.get('edit_commit_message')

            if file_path and content and branch_name and commit_message:
                success, message = update_github_file(repo, file_path, content, branch_name, commit_message)
                return jsonify({'success': success, 'message': message})
            else:
                return jsonify({'success': False, 'message': '필요한 모든 필드를 입력해주세요.'})

    return render_template('project/save_code.html', form=form, project=project, branches=branches)


@bp.route('/get_file_content/<int:project_id>', methods=['GET', 'POST'])
@login_required
def get_file_content_api(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        file_path = request.form.get('file_path')
        branch_name = request.form.get('branch_name')
    else:
        file_path = request.args.get('file_path')
        branch_name = request.args.get('branch_name')
    
    repo = get_github_repo(project)
    success, content = get_file_content(repo, file_path, branch_name)
    
    if success:
        return content
    else:
        return content, 400

@bp.route('/get_files/<int:project_id>')
@login_required
def get_files_api(project_id):
    branch = request.args.get('branch')
    if not branch:
        return jsonify({"error": "Branch parameter is missing"}), 400
    
    project = Project.query.get_or_404(project_id)
    repo = get_github_repo(project)

    try:
        files = get_files_internal(repo, branch)
        if not files:
            current_app.logger.info(f'프로젝트 {project_id}의 브랜치 {branch}에 파일이 없습니다.')
        return jsonify(files)
    except GithubException as e:
        current_app.logger.error(f'GitHub API 오류: {e.status} {e.data}')
        return jsonify({"error": str(e.data)}), e.status
    except Exception as e:
        current_app.logger.error(f'파일 목록을 가져오는 중 예상치 못한 오류 발생: {str(e)}')
        return jsonify({"error": "Internal server error"}), 500
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

@bp.route('/feedback/<int:project_id>')
@login_required
def feedback(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user not in project.participants and current_user != project.client:
        flash('You are not authorized to view this page.', 'warning')
        return redirect(url_for('project.detail', project_id=project_id))

    post_form = PostForm()
    comment_form = CommentForm()

    return render_template('project/feedback.html', project=project, post_form=post_form, comment_form=comment_form)

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

@bp.route('/progress/<int:project_id>', methods=['GET', 'POST'])
@login_required
def progress(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user not in project.participants and current_user != project.client:
        flash('프로젝트 참여자와 의뢰자만 진행상황을 볼 수 있습니다.', 'warning')
        return redirect(url_for('project.detail', project_id=project_id))
    
    form = ProjectProgressForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        conversation_filename = None
        if form.ai_conversation_file.data:
            conversation_file = form.ai_conversation_file.data
            conversation_filename = secure_filename(conversation_file.filename)
            conversation_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], conversation_filename)
            conversation_file.save(conversation_file_path)
        
        progress = ProjectProgress(
            project=project, 
            user=current_user, 
            date=form.date.data, 
            description=form.description.data,
            image=filename,
            ai_conversation_link=form.ai_conversation_link.data,
            ai_conversation_file=conversation_filename
        )
        db.session.add(progress)
        db.session.commit()
        flash('진행상황이 성공적으로 기록되었습니다.', 'success')
        return redirect(url_for('project.progress', project_id=project_id))
    
    progress_list = ProjectProgress.query.filter_by(project=project).order_by(ProjectProgress.date.desc()).all()
    return render_template('project/progress.html', project=project, form=form, progress_list=progress_list)

#이미지 업로드용 API엔드포인트.
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image.save(file_path)
        
        return jsonify({'url': url_for('uploaded_file', filename=filename)})

    return jsonify({'error': 'Invalid file type'}), 400


@bp.route('/toggle_automation_tool/<int:project_id>', methods=['POST'])
@login_required
def toggle_automation_tool(project_id):
    form = EmptyForm()  # 빈 폼 생성
    if form.validate_on_submit():  # CSRF 토큰 검증
        project = Project.query.get_or_404(project_id)
        if current_user != project.client:
            flash('권한이 없습니다.', 'error')
        else:
            project.automation_tool_in_development = not project.automation_tool_in_development
            db.session.commit()
            flash('자동화 툴 상태가 업데이트되었습니다.', 'success')
    else:
        flash('CSRF 토큰이 유효하지 않습니다.', 'error')
    return redirect(url_for('project.detail', project_id=project_id))

