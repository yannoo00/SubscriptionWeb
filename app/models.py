from app import db
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' 또는 'teacher'
    enrollments = db.relationship('Enrollment', back_populates='student', lazy=True)
    courses = db.relationship('Course', back_populates='teacher', lazy=True)  # 강사가 가르치는 강좌들
    subscription = db.relationship('Subscription', back_populates='subscriber', uselist=False)
    bio = db.Column(db.Text)
    notifications = db.relationship('Notification', back_populates='user', lazy=True)
    def is_teacher(self):
        return self.role == 'teacher'
    def get_student_count(self):
        return Enrollment.query.join(Course).filter(Course.teacher_id == self.id).count()

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', back_populates='courses')
    enrollments = db.relationship('Enrollment', back_populates='course', lazy=True)
    projects = db.relationship('Project', back_populates='course', lazy=True)

    @hybrid_property
    def average_rating(self):
        if self.enrollments:
            total_rating = sum(enrollment.rating for enrollment in self.enrollments if enrollment.rating)
            count = sum(1 for enrollment in self.enrollments if enrollment.rating)
            return round(total_rating / count, 1) if count > 0 else None
        return None
    @hybrid_property
    def rating_count(self):
        return sum(1 for enrollment in self.enrollments if enrollment.rating)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    student = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')
    rating = db.Column(db.Integer)

class Mentorship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    mentor = db.relationship('User', foreign_keys=[mentor_id], back_populates='mentees')
    mentee = db.relationship('User', foreign_keys=[mentee_id], back_populates='mentors')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', back_populates='projects')
    submissions = db.relationship('ProjectSubmission', back_populates='project', lazy=True)

class ProjectSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    project = db.relationship('Project', back_populates='submissions')
    student = db.relationship('User', backref=db.backref('project_submissions', lazy=True))

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

User.mentees = db.relationship('Mentorship', foreign_keys=[Mentorship.mentor_id], back_populates='mentor', lazy=True)
User.mentors = db.relationship('Mentorship', foreign_keys=[Mentorship.mentee_id], back_populates='mentee', lazy=True)