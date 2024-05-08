# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FloatField, SubmitField, HiddenField
from wtforms.validators import DataRequired

class ProjectForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired()])
    description = TextAreaField('설명', validators=[DataRequired()])
    start_date = DateField('시작일', validators=[DataRequired()])
    end_date = DateField('종료일', validators=[DataRequired()])
    submit = SubmitField('저장')

class EnrollmentForm(FlaskForm):
    course_id = HiddenField()
    submit = SubmitField('수강 신청')

class CourseForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired()])
    description = TextAreaField('설명', validators=[DataRequired()])
    price = FloatField('가격', validators=[DataRequired()])
    submit = SubmitField('등록')

class PostForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired()])
    content = TextAreaField('내용', validators=[DataRequired()])
    submit = SubmitField('작성')

class CommentForm(FlaskForm):
    content = TextAreaField('댓글', validators=[DataRequired()])
    submit = SubmitField('작성')