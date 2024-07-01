from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app.models import User, ChatRoom, ChatRoomParticipant, ChatMessage
from app import db, socketio
from app.forms import ChatRoomForm
from wtforms import StringField
from wtforms.validators import DataRequired

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/')
@login_required
def chat_list():
    chat_rooms = current_user.chat_rooms
    return render_template('chat/chat_list.html', chat_rooms=chat_rooms)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_chat_room():
    form = ChatRoomForm()
    if form.validate_on_submit():
        chat_room = ChatRoom(name=form.name.data)
        db.session.add(chat_room)
        db.session.commit()
        
        participant = ChatRoomParticipant(user_id=current_user.id, chat_room_id=chat_room.id)
        db.session.add(participant)
        db.session.commit()
        
        flash('채팅방이 생성되었습니다.', 'success')
        return redirect(url_for('chat.chat_list'))
    return render_template('chat/create_chat_room.html', form=form)

@bp.route('/<int:chat_room_id>')
@login_required
def chat_room(chat_room_id):
    chat_room = ChatRoom.query.get_or_404(chat_room_id)
    messages = chat_room.messages
    return render_template('chat/chat_room.html', chat_room=chat_room, messages=messages)

@bp.route('/<int:chat_room_id>/send', methods=['POST'])
@login_required
def send_message(chat_room_id):
    chat_room = ChatRoom.query.get_or_404(chat_room_id)
    content = request.form['content']
    message = ChatMessage(chat_room_id=chat_room.id, sender_id=current_user.id, content=content)
    db.session.add(message)
    db.session.commit()
    return redirect(url_for('chat.chat_room', chat_room_id=chat_room.id))

# SocketIO 이벤트 핸들러는 그대로 유지
@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('status', {'msg': username + ' has entered the room.'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': username + ' has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    emit('message', data, room=data['room'])