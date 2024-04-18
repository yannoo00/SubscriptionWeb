from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Course, Enrollment
from app import db
from flask import current_app

bp = Blueprint('payments', __name__, url_prefix='/payments')

@bp.route('/checkout/<int:course_id>', methods=['GET', 'POST'])
@login_required
def checkout(course_id):
    current_app.logger.info(f'Entering checkout function for course_id={course_id}, request.method={request.method}')
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        enrollment = Enrollment(student_id=current_user.id, course_id=course.id)
        db.session.add(enrollment)
        db.session.commit()
        current_app.logger.info(f'Enrollment created for user {current_user.email} and course {course.title}')
        flash('결제가 완료되었습니다.', 'success')
        return redirect(url_for('courses.course_list'))
    current_app.logger.info('Rendering payment template')
    return render_template('payments/payment.html', course=course)