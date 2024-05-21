from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import ProjectPost, ProjectComment
from app.forms import PostForm, CommentForm

bp = Blueprint('community', __name__, url_prefix='/community')

@bp.route('/')
def post_list():
    posts = ProjectPost.query.order_by(ProjectPost.created_at.desc()).all()
    return render_template('community/post_list.html', posts=posts)

@bp.route('/<int:post_id>')
def post_detail(post_id):
    post = ProjectPost.query.get_or_404(post_id)
    form = CommentForm()
    return render_template('community/post_detail.html', post=post, form=form)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = ProjectPost(content=form.content.data, user=current_user)
        db.session.add(post)
        db.session.commit()
        flash('글이 성공적으로 작성되었습니다.', 'success')
        return redirect(url_for('community.post_detail', post_id=post.id))
    return render_template('community/post_form.html', form=form)

@bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = ProjectPost.query.get_or_404(post_id)
    if post.user != current_user:
        flash('수정 권한이 없습니다.', 'error')
        return redirect(url_for('community.post_detail', post_id=post.id))
    form = PostForm(obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.commit()
        flash('글이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('community.post_detail', post_id=post.id))
    return render_template('community/post_form.html', form=form)

@bp.route('/<int:post_id>/comments', methods=['POST'])
@login_required
def new_comment(post_id):
    post = ProjectPost.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = ProjectComment(content=form.content.data, user=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('댓글이 성공적으로 작성되었습니다.', 'success')
        return redirect(url_for('community.post_detail', post_id=post.id))
    return redirect(url_for('community.post_detail', post_id=post.id))