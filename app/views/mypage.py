from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Course, Enrollment, Subscription, Project
from app import db
from app.forms import RatingForm, TeacherProfileForm


bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@bp.route('/')
@login_required
def index():
    if current_user.is_teacher():
        courses = current_user.courses
        enrollments = Enrollment.query.filter(Enrollment.course_id.in_([course.id for course in courses])).all()
        projects = Project.query.filter(Project.course_id.in_([course.id for course in courses])).all()
    else:
        enrollments = current_user.enrollments
        projects = Project.query.join(Course).filter(Course.id.in_([enrollment.course_id for enrollment in enrollments])).all()

    form = RatingForm();    
    return render_template('mypage/index.html', enrollments=enrollments, projects=projects, form = form)

@bp.route('/approve_enrollment/<int:enrollment_id>')
@login_required
def approve_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    if enrollment.course.teacher != current_user:
        flash('권한이 없습니다.', 'error')
    else:
        enrollment.approved = True
        db.session.commit()
        flash('수강 신청이 승인되었습니다.', 'success')
    return redirect(url_for('mypage.index'))


@bp.route('/rate_course/<int:enrollment_id>', methods=['POST'])
@login_required
def rate_course(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    if enrollment.student != current_user:
        flash('권한이 없습니다.', 'error')
    else:
        rating = int(request.form['rating'])
        if 1 <= rating <= 5:
            enrollment.rating = rating
            db.session.commit()
            flash('평점이 등록되었습니다.', 'success')
        else:
            flash('평점은 1점부터 5점까지 가능합니다.', 'error')
    return redirect(url_for('mypage.index'))


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_teacher():
        flash('강사만 접근할 수 있습니다.', 'error')
        return redirect(url_for('mypage.index'))

    form = TeacherProfileForm()
    if form.validate_on_submit():
        current_user.bio = form.bio.data
        db.session.commit()
        flash('프로필이 업데이트되었습니다.', 'success')
        return redirect(url_for('mypage.index'))

    form.bio.data = current_user.bio
    return render_template('mypage/profile.html', form=form)