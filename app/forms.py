from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, SubmitField, IntegerField, FloatField, HiddenField, FieldList, FormField
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

#이 코드는 project_list에서 버튼 삭제하고 얘도 같이 삭제할 것.
class ProjectParticipationForm(FlaskForm):
    submit =  SubmitField('참여하기')

class ParticipateForm(FlaskForm):
    submit = SubmitField('참가 신청')

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

class AcceptParticipantForm(FlaskForm):
    user_id = HiddenField('User ID', validators=[DataRequired()])
    submit = SubmitField('수락')

class ProjectProgressForm(FlaskForm):
    date = DateField('날짜', validators=[DataRequired()])
    description = TextAreaField('진행내용', validators=[DataRequired()])
    submit = SubmitField('기록')    

class RequirementForm(FlaskForm):
    requirement = StringField('Requirement', validators=[DataRequired()])

class ProjectPlanForm(FlaskForm):
    overview = TextAreaField('Project Overview', validators=[DataRequired()])
    flowchart = TextAreaField('Flowchart', validators=[DataRequired()])
    submit = SubmitField('Save')

class ChatRoomForm(FlaskForm):
    name = StringField('채팅방 이름', validators=[DataRequired()])
 

 