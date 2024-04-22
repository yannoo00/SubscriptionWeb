from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Course, Enrollment  # Teacher 모델 대신 User 모델 import
from app import db

bp = Blueprint('teachers', __name__, url_prefix='/teachers')

@bp.route('/<int:teacher_id>')
def profile(teacher_id):
    teacher = User.query.get_or_404(teacher_id)  # User 모델로 변경
    return render_template('teachers/profile.html', teacher=teacher)

@bp.route('/<int:teacher_id>/enroll', methods=['POST'])
@login_required
def enroll(teacher_id):
    course_id = request.form['course_id']
    enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    flash('수강 신청이 완료되었습니다. 선생님의 승인을 기다려 주세요.', 'success')
    return redirect(url_for('teachers.profile', teacher_id=teacher_id))

@bp.route('/enrollments')
@login_required
def enrollments():
    teacher = User.query.filter_by(email=current_user.email).first_or_404()  # User 모델로 변경
    enrollments = Enrollment.query.join(Course).filter(Course.teacher_id == teacher.id).all()
    return render_template('teachers/enrollments.html', enrollments=enrollments)

@bp.route('/enrollments/<int:enrollment_id>/approve', methods=['POST'])
@login_required
def approve_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    enrollment.approved = True
    db.session.commit()
    flash('수강 신청을 승인했습니다.', 'success')
    return redirect(url_for('teachers.enrollments'))

@bp.route('/enrollments/<int:enrollment_id>/reject', methods=['POST'])
@login_required
def reject_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    db.session.delete(enrollment)
    db.session.commit()
    flash('수강 신청을 거절했습니다.', 'success')
    return redirect(url_for('teachers.enrollments'))

def get_teacher_rankings():
    teachers = User.query.filter_by(role='teacher').all()
    teacher_scores = []
    for teacher in teachers:
        enrollments = Enrollment.query.join(Course).filter(Course.teacher == teacher).all()
        num_students = len(enrollments)
        avg_rating = sum(enrollment.rating or 0 for enrollment in enrollments) / num_students if num_students > 0 else 0
        score = num_students * avg_rating
        teacher_scores.append((teacher, score))
    rankings = sorted(teacher_scores, key=lambda x: x[1], reverse=True)
    return rankings

@bp.route('/rankings')
def rankings():
    rankings = get_teacher_rankings()
    return render_template('teachers/rankings.html', rankings=rankings)