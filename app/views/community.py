from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Post, Comment
from app.views.teachers import get_teacher_rankings

bp = Blueprint('community', __name__)

@bp.route('/posts')
def post_list():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    rankings = get_teacher_rankings()
    return render_template('community/post_list.html', posts=posts, rankings=rankings)

@bp.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    rankings = get_teacher_rankings()
    return render_template('community/post_detail.html', post=post, rankings=rankings)

@bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('글이 성공적으로 작성되었습니다.', 'success')
        return redirect(url_for('community.post_detail', post_id=post.id))
    rankings = get_teacher_rankings()
    return render_template('community/post_form.html', rankings=rankings)

@bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('수정 권한이 없습니다.', 'error')
        return redirect(url_for('community.post_detail', post_id=post.id))
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('글이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('community.post_detail', post_id=post.id))
    rankings = get_teacher_rankings()
    return render_template('community/post_form.html', post=post, rankings=rankings)

@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@login_required
def new_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form['content']
    comment = Comment(content=content, author=current_user, post=post)
    db.session.add(comment)
    db.session.commit()
    flash('댓글이 성공적으로 작성되었습니다.', 'success')
    return redirect(url_for('community.post_detail', post_id=post.id))