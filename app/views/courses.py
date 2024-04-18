from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import Course
from flask import current_app
from app import db
#from app.models import Teacher

bp = Blueprint('courses', __name__, url_prefix='/courses')

@bp.route('/')
@login_required
def course_list():
    current_app.logger.info('Entering course_list function')
    courses = Course.query.all()
    current_app.logger.info('Rendering course_list template')
    return render_template('courses/course_list.html', courses=courses)


@bp.route('/create', methods=['GET','POST'])
@login_required
def create_course():
    if not current_user.is_teacher():
        flash('강사만 강좌를 등록할 수 있습니다.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']

        course = Course(title=title, description=description, price=price, teacher=current_user)
        db.session.add(course)
        db.session.commit()

        flash('강좌가 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('courses.course_list'))

    return render_template('courses/create_course.html')
