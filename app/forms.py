from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, NumberRange

class RatingForm(FlaskForm):
    rating = IntegerField('평점', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('평점 매기기')

class ProjectForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired()])
    description = TextAreaField('설명', validators=[DataRequired()])
    start_date = DateField('시작일', validators=[DataRequired()])
    end_date = DateField('종료일', validators=[DataRequired()])
    submit = SubmitField('저장')

class PostForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired()])
    content = TextAreaField('내용', validators=[DataRequired()])
    submit = SubmitField('작성')

class CommentForm(FlaskForm):
    content = TextAreaField('댓글', validators=[DataRequired()])
    submit = SubmitField('작성')

class TeacherProfileForm(FlaskForm):
    bio = TextAreaField('약력')
    submit = SubmitField('저장')

class ProjectParticipationForm(FlaskForm):
    submit =  SubmitField('참여하기')

class AssignTaskForm(FlaskForm):
    title = StringField('과제 제목', validators=[DataRequired()])
    description = TextAreaField('과제 설명', validators=[DataRequired()])
    deadline = DateField('마감일', validators=[DataRequired()])
    submit = SubmitField('과제 할당')
    file = FileField('과제 파일', validators=[FileAllowed(['pdf', 'doc', 'docx'])])

class RequestMentorshipForm(FlaskForm):
    submit = SubmitField('멘토링 신청')

class AcceptMentorshipForm(FlaskForm):
    submit = SubmitField('멘토링 수락')

class SubmitTaskForm(FlaskForm):
    file = FileField('과제 파일', validators=[DataRequired(), FileAllowed(['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar'])])
    submit = SubmitField('제출')

class ContributionForm(FlaskForm):
    hours = FloatField('참여 시간', validators=[DataRequired()])
    submit = SubmitField('기록')
