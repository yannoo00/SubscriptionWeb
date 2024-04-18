from app import create_app, db
from app.models import User, Course, Enrollment  # Teacher 모델 제거

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Course': Course, 'Enrollment': Enrollment}  # Teacher 모델 제거

if __name__ == '__main__':
    app.run(debug=True)