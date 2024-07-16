from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from flask_wtf.csrf import generate_csrf
from app.models import User, ChatRoom, ChatRoomParticipant, ChatMessage
from app import db, socketio
from app.forms import ChatRoomForm
from datetime import datetime

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/')
@login_required
def chat_list():
    public_rooms = ChatRoom.query.filter_by(is_public=True).all()
    private_rooms = ChatRoom.query.filter(
        ChatRoom.is_public == False,
        ChatRoom.participants.any(id=current_user.id)
    ).all()
    chat_rooms = public_rooms + private_rooms
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
    
    messages = ChatMessage.query.filter_by(chat_room_id=chat_room_id).order_by(ChatMessage.timestamp).all()
    csrf_token = generate_csrf()    
    return render_template('chat/chat_room.html', chat_room=chat_room, messages=messages)

@socketio.on('join')
def on_join(data):
    username = current_user.name
    room = data['room']
    join_room(room)
    emit('status', {'msg': username + ' has entered the room.'}, room=room)
    
    # 참여자가 입장할 때 업데이트된 참여자 목록 전송
    chat_room = ChatRoom.query.get(room)
    updated_participants = [{"id": p.id, "name": p.name} for p in chat_room.participants]
    emit('update_participants', {'participants': updated_participants}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = current_user.name
    room = data['room']
    leave_room(room)
    emit('status', {'msg': username + ' has left the room.'}, room=room)
    
    # 참여자가 퇴장할 때 업데이트된 참여자 목록 전송
    chat_room = ChatRoom.query.get(room)
    updated_participants = [{"id": p.id, "name": p.name} for p in chat_room.participants if p.id != current_user.id]
    emit('update_participants', {'participants': updated_participants}, room=room)


@socketio.on('message')
def handle_message(data):
    content = data.get('msg')
    room = data['room']
    
    chat_room = ChatRoom.query.get(room)
    if not chat_room:
        return
    
    new_message = ChatMessage(
        chat_room_id=room,
        sender_id=current_user.id,
        content=content
    )
    db.session.add(new_message)
    db.session.commit()
    
    message = {
        'content': content,
        'username': current_user.name,
        'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    emit('message', message, room=room)

@bp.route('/<int:chat_room_id>/leave', methods=['POST'])
@login_required
# @csrf.exempt  # CSRF 보호를 비활성화하려면 이 줄의 주석을 제거하세요
def leave_chat_room(chat_room_id):
    chat_room = ChatRoom.query.get_or_404(chat_room_id)
    participant = ChatRoomParticipant.query.filter_by(
        user_id=current_user.id,
        chat_room_id=chat_room_id
    ).first()

    if participant:
        db.session.delete(participant)
        db.session.commit()
        flash('채팅방을 나갔습니다.', 'success')
        
        # 업데이트된 참여자 목록 전송
        updated_participants = [{"id": p.id, "name": p.name} for p in chat_room.participants]
        socketio.emit('update_participants', {'participants': updated_participants}, room=chat_room_id)
    else:
        flash('해당 채팅방의 참여자가 아닙니다.', 'error')

    return redirect(url_for('chat.chat_list'))