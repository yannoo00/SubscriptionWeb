from app import db
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    notifications = db.relationship('Notification', back_populates='user', lazy=True)
    projects = db.relationship('ProjectParticipant', back_populates='user', lazy=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mentor = db.relationship('User', remote_side=[id], backref=db.backref('mentees', lazy=True))
    assignments = db.relationship('Assignment', backref='user', lazy=True)
    subscription = db.relationship('Subscription', back_populates='subscriber', uselist=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client = db.relationship('User', backref=db.backref('created_projects', lazy=True))
    participants = db.relationship('ProjectParticipant', back_populates='project', lazy=True)
    completed = db.Column(db.Boolean, default=False)

class ProjectParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user = db.relationship('User', back_populates='projects')
    project = db.relationship('Project', back_populates='participants')

class ProjectPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project = db.relationship('Project', backref=db.backref('posts', lazy=True))
    user = db.relationship('User', backref=db.backref('project_posts', lazy=True))

class ProjectComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('project_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post = db.relationship('ProjectPost', backref=db.backref('comments', lazy=True))
    user = db.relationship('User', backref=db.backref('project_comments', lazy=True))

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    mentor = db.relationship('User', foreign_keys=[mentor_id], backref=db.backref('given_assignments', lazy=True))
    mentee = db.relationship('User', foreign_keys=[mentee_id], backref=db.backref('received_assignments', lazy=True))

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiration_date = db.Column(db.DateTime)
    subscriber = db.relationship('User', back_populates='subscription')

    def __init__(self, user_id):
        self.user_id = user_id
        self.payment_date = datetime.utcnow()
        self.expiration_date = self.payment_date + timedelta(days=30)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    user = db.relationship('User', back_populates='notifications')