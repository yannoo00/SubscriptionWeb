from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
import requests
from flask_wtf.csrf import CSRFProtect, CSRFError
from app import forms

csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads')
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

    from app.views import mypage, auth, payments, main, community, project, notification, mentorship, chat
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(payments.bp, url_prefix='/payments')
    app.register_blueprint(main.bp)
    app.register_blueprint(mypage.bp, url_prefix='/mypage')
    app.register_blueprint(community.bp, url_prefix='/community')
    app.register_blueprint(project.bp)
    app.register_blueprint(notification.bp, url_prefix='/notification')
    app.register_blueprint(mentorship.bp, url_prefix='/mentorship')
    app.register_blueprint(chat.bp, url_prefix='/chat')

    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            join_room(current_user.id)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        if current_user.is_authenticated:
            leave_room(current_user.id)

    return app

def send_notification(user_id, message):
    socketio.emit('notification', {'message':message}, room = user_id)

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(int(user_id))
    return None

TOSSPAYMENTS_CLIENT_KEY = 'test_ck_ma60RZblrqomPN1xAM6e3wzYWBn1'
TOSSPAYMENTS_SECRET_KEY = 'test_sk_PBal2vxj81gGY9mwM0g2V5RQgOAN'
TOSS_PAYMENTS_API_URL = 'https://api.tosspayments.com/v1/'