from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Subscription, Project
from app import db
from app.forms import TeacherProfileForm

bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@bp.route('/')
@login_required
def index():
    participating_projects = current_user.projects
    created_projects = current_user.created_projects
    return render_template('mypage/index.html', participating_projects=participating_projects, created_projects=created_projects)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = TeacherProfileForm()
    if form.validate_on_submit():
        current_user.bio = form.bio.data
        db.session.commit()
        flash('프로필이 업데이트되었습니다.', 'success')
        return redirect(url_for('mypage.index'))
    form.bio.data = current_user.bio
    return render_template('mypage/profile.html', form=form)