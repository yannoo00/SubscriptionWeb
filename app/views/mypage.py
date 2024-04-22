from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Course, Enrollment, Subscription
from app import db

bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@bp.route('/')
@login_required
def index():
    if current_user.is_teacher():
        courses = current_user.courses
        enrollments = Enrollment.query.filter(Enrollment.course_id.in_([course.id for course in courses])).all()
    else:
        enrollments = current_user.enrollments

    subscriptios = current_user.subscriptions
    return render_template('mypage/index.html', enrollments=enrollments)


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
