from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app.forms import RegistrationForm

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
            if 'logged_in' not in session:
                flash('로그인 되었습니다.', 'success')
                session['logged_in'] = True
            return redirect(url_for('main.index'))  #
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
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            current_app.logger.info(f'Registration failed for email {form.email.data}, user already exists')
            flash('이미 등록된 이메일입니다.', 'danger')
        elif form.is_admin.data and form.admin_password.data != current_app.config['ADMIN_PASSWORD']:
            current_app.logger.info('Registration failed, incorrect admin password')
            flash('관리자 인증 비밀번호가 올바르지 않습니다.', 'danger')
        else:
            new_user = User(
                name=form.name.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data, method='pbkdf2:sha256'),
                is_admin=form.is_admin.data
            )
            db.session.add(new_user)
            db.session.commit()
            current_app.logger.info(f'New user {form.email.data} registered successfully. Admin: {form.is_admin.data}')
            flash('회원가입이 완료되었습니다.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)