from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app.models import User, ChatRoom, ChatRoomParticipant, ChatMessage
from app import db, socketio
from app.forms import ChatRoomForm
from collections import deque
from datetime import datetime, timedelta
import json
from datetime import datetime


bp = Blueprint('chat', __name__, url_prefix='/chat')

# 메모리 내 메시지 저장소
chat_messages = {}
MESSAGE_RETENTION_PERIOD = timedelta(hours=24)

def add_message(room_id, message):
    if room_id not in chat_messages:
        chat_messages[room_id] = deque(maxlen=100)
    chat_messages[room_id].append({
        'content': message['content'],
        'username': message['username'],
        'timestamp': datetime.now()
    })
    
    # 데이터베이스에도 저장 (선택적)
    db_message = ChatMessage(
        chat_room_id=room_id,
        sender_id=message.get('sender_id'),  # sender_id가 없을 수 있으므로 get 사용
        content=message['content']
    )
    db.session.add(db_message)
    db.session.commit()

def get_recent_messages(room_id):
    if room_id in chat_messages:
        current_time = datetime.now()
        messages = [
            {
                'content': msg['content'],
                'username': msg['username'],
                'timestamp': json_serial(msg['timestamp'])
            }
            for msg in chat_messages[room_id]
            if current_time - msg['timestamp'] <= MESSAGE_RETENTION_PERIOD
        ]
        return messages
    return []



@bp.route('/')
@login_required
def chat_list():
    chat_rooms = current_user.chat_rooms
    return render_template('chat/chat_list.html', chat_rooms=chat_rooms)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_chat_room():
    form = ChatRoomForm()
    form.participants.choices = [(user.id, user.name) for user in User.query.filter(User.id != current_user.id).all()]
    
    if form.validate_on_submit():
        chat_room = ChatRoom(name=form.name.data, is_public=form.is_public.data, creator_id=current_user.id)
        db.session.add(chat_room)
        db.session.flush()  # ID를 얻기 위해 flush
        
        # 생성자를 참여자로 추가
        participant = ChatRoomParticipant(user_id=current_user.id, chat_room_id=chat_room.id)
        db.session.add(participant)
        
        # 비공개 채팅방일 경우 선택된 참여자 추가
        if not form.is_public.data:
            for user_id in form.participants.data:
                participant = ChatRoomParticipant(user_id=user_id, chat_room_id=chat_room.id)
                db.session.add(participant)
        
        db.session.commit()
        flash('채팅방이 생성되었습니다.', 'success')
        return redirect(url_for('chat.chat_list'))
    
    return render_template('chat/create_chat_room.html', form=form)

@bp.route('/<int:chat_room_id>')
@login_required
def chat_room(chat_room_id):
    chat_room = ChatRoom.query.get_or_404(chat_room_id)
    if not chat_room.is_public and current_user not in chat_room.participants:
        flash('이 채팅방에 접근할 권한이 없습니다.', 'error')
        return redirect(url_for('chat.chat_list'))
    messages = get_recent_messages(chat_room_id)
    return render_template('chat/chat_room.html', chat_room=chat_room, messages=messages)

@bp.route('/<int:chat_room_id>/send', methods=['POST'])
@login_required
def send_message(chat_room_id):
    content = request.form['content']
    message = {
        'content': content,
        'username': current_user.name,
        'sender_id': current_user.id,
        'timestamp': datetime.now()
    }
    add_message(chat_room_id, message)
    return jsonify(success=True)

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('status', {'msg': username + ' has entered the room.'}, room=room)
    recent_messages = get_recent_messages(room)
    emit('load_messages', {'messages': json.dumps(recent_messages, default=json_serial)}, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'{current_user.name} has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    content = data.get('msg') or data.get('content') or data.get('message')
    if content is None:
        print("Error: Message content not found in data", data)
        return

    room = data['room']
    username = data.get('username', 'Anonymous')
    
    message = {
        'content': content,
        'username': username,
        'sender_id': current_user.id if current_user.is_authenticated else None
    }
    
    add_message(room, message)
    
    emit('message', {
        'content': content,
        'username': username
    }, room=room)


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")