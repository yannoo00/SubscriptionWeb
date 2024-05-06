from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
import requests
from flask_wtf.csrf import CSRFProtect
from app import forms

csrf = CSRFProtect()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config['UPLOAD_FOLDER'] = 'uploads'

    csrf.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db) #초기화
    login_manager.init_app(app)

    # 로거 설정
    file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

    from app.views import mypage, auth, courses, payments, main, teachers, mypage, community, project
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(courses.bp, url_prefix='/courses')
    app.register_blueprint(payments.bp, url_prefix='/payments')
    app.register_blueprint(main.bp)
    app.register_blueprint(teachers.bp, url_prefix='/teachers')
    app.register_blueprint(mypage.bp, url_prefix='/mypage')
    app.register_blueprint(community.bp, url_prefix='/community')
    app.register_blueprint(project.bp)

    #with app.app_context():
    #     db.create_all()
    return app

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(int(user_id))
    return None


#PAYMENTS
TOSSPAYMENTS_CLIENT_KEY = 'test_ck_ma60RZblrqomPN1xAM6e3wzYWBn1'
TOSSPAYMENTS_SECRET_KEY = 'test_sk_PBal2vxj81gGY9mwM0g2V5RQgOAN'
TOSS_PAYMENTS_API_URL = 'https://api.tosspayments.com/v1/'
