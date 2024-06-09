from app import db
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta

mentorship = db.Table('mentorship',
    db.Column('mentor_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('mentee_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)
mentorship_mentor = db.Table('mentorship_mentor',
    db.Column('mentor_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('mentee_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

mentorship_mentee = db.Table('mentorship_mentee',
    db.Column('mentee_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('mentor_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    notifications = db.relationship('Notification', back_populates='user', lazy=True)
    projects = db.relationship('Project', secondary='project_participant', back_populates='participants', overlaps="project_participants")
    subscription = db.relationship('Subscription', back_populates='subscriber', uselist=False)
    created_projects = db.relationship('Project', back_populates='client', lazy=True, foreign_keys='Project.client_id')
    mentees = db.relationship('User', 
                              secondary=mentorship_mentor,
                              primaryjoin=(mentorship_mentor.c.mentor_id == id),
                              secondaryjoin=(mentorship_mentor.c.mentee_id == id),
                              backref=db.backref('mentors', lazy='dynamic'),
                              lazy='dynamic')
                              
    pending_mentees = db.relationship('User', 
                                    secondary=mentorship_mentee,
                                    primaryjoin=(mentorship_mentee.c.mentor_id == id),
                                    secondaryjoin=(mentorship_mentee.c.mentee_id == id),
                                    backref=db.backref('pending_mentors', lazy='dynamic'),
                                    lazy='dynamic')
    project_participants = db.relationship('ProjectParticipant', back_populates='user', lazy=True, overlaps="projects")

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client = db.relationship('User', back_populates='created_projects')
    completed = db.Column(db.Boolean, default=False)
    participants = db.relationship('User', secondary='project_participant', back_populates='projects', overlaps="project_participants")
    project_participants = db.relationship('ProjectParticipant', back_populates='project', lazy=True, overlaps="participants,projects")

class ProjectParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    hours_contributed = db.Column(db.Float, default=0.0)    
    user = db.relationship('User', back_populates='project_participants', overlaps="participants,projects")
    project = db.relationship('Project', back_populates='project_participants', overlaps="participants,projects")

class ProjectPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
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
    file = db.Column(db.String(255), nullable = True)


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