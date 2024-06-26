from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user, emit, join_room, leave_room
from app import app, db, socketio
from models import User, ChatRoom, ChatRoomParticipant, ChatMessage

@app.route('/chat')
@login_required
def chat():
    chat_rooms = current_user.chat_rooms
    return render_template('chat.html', chat_rooms=chat_rooms)

@app.route('/chat/create', methods=['GET', 'POST'])
@login_required
def create_chat_room():
    if request.method == 'POST':
        name = request.form['name']
        chat_room = ChatRoom(name=name)
        db.session.add(chat_room)
        db.session.commit()

        participant = ChatRoomParticipant(user_id=current_user.id, chat_room_id=chat_room.id)
        db.session.add(participant)
        db.session.commit()

        return redirect(url_for('chat'))
    return render_template('create_chat_room.html')

@app.route('/chat/<int:chat_room_id>')
@login_required
def chat_room(chat_room_id):
    chat_room = ChatRoom.query.get_or_404(chat_room_id)
    messages = chat_room.messages
    return render_template('chat_room.html', chat_room=chat_room, messages=messages)

@app.route('/chat/<int:chat_room_id>/send', methods=['POST'])
@login_required
def send_message(chat_room_id):
    chat_room = ChatRoom.query.get_or_404(chat_room_id)
    content = request.form['content']
    message = ChatMessage(chat_room_id=chat_room.id, sender_id=current_user.id, content=content)
    db.session.add(message)
    db.session.commit()
    return redirect(url_for('chat_room', chat_room_id=chat_room.id))

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