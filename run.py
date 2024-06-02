from app import create_app, db, socketio
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == '__main__':
    socketio.run(app, host = '0.0.0.0', port=5000)