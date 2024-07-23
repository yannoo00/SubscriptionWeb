from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, SubmitField, IntegerField, FloatField, HiddenField, FieldList, FormField, BooleanField, SelectMultipleField, SelectField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, URL, Email, EqualTo

class RatingForm(FlaskForm):
    rating = IntegerField('평점', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('평점 매기기')

class ProjectForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired()])
    description = TextAreaField('설명', validators=[DataRequired()])
    start_date = DateField('시작일', validators=[DataRequired()])
    end_date = DateField('종료일', validators=[DataRequired()])
    submit = SubmitField('저장')
    type = SelectField('프로젝트 유형', choices=[('collaboration', '협업 프로젝트'), ('study', '스터디 프로젝트')])
    is_public = BooleanField('공개 설정 (스터디 프로젝트만 해당)')

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
    image = FileField('이미지 업로드', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '이미지 파일만 허용됩니다.')])
    ai_conversation_link = StringField('GPT 대화 공유 링크', validators=[URL()])
    ai_conversation_file = FileField('Claude 대화 내역 업로드', validators=[FileAllowed(['mhtml'], 'MHTML 파일만 허용됩니다.')])


class RequirementForm(FlaskForm):
    requirement = StringField('Requirement', validators=[DataRequired()])

class ProjectPlanForm(FlaskForm):
    overview = TextAreaField('Project Overview', validators=[DataRequired()])
    flowchart = TextAreaField('Flowchart', validators=[DataRequired()])
    submit = SubmitField('Save')


class ChatRoomForm(FlaskForm):
    name = StringField('채팅방 이름', validators=[DataRequired()])
    is_public = BooleanField('공개 채팅방')
    participants = SelectMultipleField('참여자 선택', coerce=int)

    def __init__(self, *args, **kwargs):
        super(ChatRoomForm, self).__init__(*args, **kwargs)
        # 참여자 선택 옵션은 뷰 함수에서 설정합니다.
        
class CodeSaveForm(FlaskForm):
    code = TextAreaField('코드', validators=[DataRequired()])
    file_name = StringField('파일 이름', validators=[DataRequired()])
    branch_name = StringField('브랜치 이름', validators=[DataRequired()])
    commit_message = StringField('커밋 메시지', validators=[DataRequired()])
    submit = SubmitField('저장 및 업로드')

class CodeEditForm(FlaskForm):
    file_path = StringField('파일 경로', validators=[DataRequired()])
    content = TextAreaField('파일 내용', validators=[DataRequired()])
    branch_name = StringField('브랜치 이름', validators=[DataRequired(), Length(max=100)])
    commit_message = StringField('Commit 메시지', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('수정')


class RegistrationForm(FlaskForm):
    name = StringField('이름', validators=[DataRequired()])
    email = StringField('이메일', validators=[DataRequired(), Email()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    confirm_password = PasswordField('비밀번호 확인', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('관리자로 가입')
    admin_password = PasswordField('관리자 인증 비밀번호')
    submit = SubmitField('가입하기')