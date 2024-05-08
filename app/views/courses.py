from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Course
from app import db
from app.forms import EnrollmentForm, CourseForm

bp = Blueprint('courses', __name__, url_prefix='/courses')

@bp.route('/')
@login_required
def course_list():
    courses = Course.query.all()
    form = EnrollmentForm()
    enrollments = current_user.enrollments if current_user.is_authenticated else []
    enrolled_course_ids = [enrollment.course_id for enrollment in enrollments]
    return render_template('courses/course_list.html', courses=courses, form=form, enrolled_course_ids=enrolled_course_ids)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if not current_user.is_teacher():
        flash('강사만 강좌를 등록할 수 있습니다.', 'error')
        return redirect(url_for('main.index'))
    
    form = CourseForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        price = form.price.data
        course = Course(title=title, description=description, price=price, teacher=current_user)
        db.session.add(course)
        db.session.commit()
        flash('강좌가 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('courses.course_list'))
    
    return render_template('courses/create_course.html', form=form)