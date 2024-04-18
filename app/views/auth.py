from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    current_app.logger.info(f'Entering login function, request.method={request.method}')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            current_app.logger.info(f'User {user.email} logged in successfully')
            flash('로그인 되었습니다.', 'success')
            return redirect(url_for('courses.course_list'))
        else:
            current_app.logger.info(f'Login failed for email {email}')
            flash('잘못된 이메일 또는 비밀번호입니다.', 'danger')

    current_app.logger.info('Rendering login template')
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃 되었습니다.', 'success')
    return redirect(url_for('main.index'))



@bp.route('/register', methods=['GET', 'POST'])
def register():
    current_app.logger.info(f'Entering register function, request.method={request.method}')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        user = User.query.filter_by(email=email).first()
        if user:
            current_app.logger.info(f'Registration failed for email {email}, user already exists')
            flash('이미 등록된 이메일입니다.', 'danger')
        elif password != confirm_password:
            current_app.logger.info('Registration failed, passwords do not match')
            flash('비밀번호가 일치하지 않습니다.', 'danger')
        else:
            new_user = User(name=name, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'), role=role)
            db.session.add(new_user)
            db.session.commit()
            current_app.logger.info(f'New user {email} registered successfully')
            flash('회원가입이 완료되었습니다.', 'success')
            return redirect(url_for('auth.login'))

    current_app.logger.info('Rendering register template')
    return render_template('auth/register.html')