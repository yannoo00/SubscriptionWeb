from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Course, Enrollment
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