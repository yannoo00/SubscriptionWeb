document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const chatMessages = document.getElementById('chat-messages');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const leaveRoomBtn = document.getElementById('leave-room-btn');
    const participantList = document.getElementById('participant-list');
  
    function scrollToBottom() {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  
    if (chatMessages && messageForm && messageInput && leaveRoomBtn) {
      socket.on('connect', function() {
        socket.emit('join', {room: CHAT_ROOM_ID});
      });
  
      socket.on('message', function(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${data.user_id === CURRENT_USER_ID ? 'sent' : 'received'}`;
        messageDiv.innerHTML = `
            <strong>${data.username}</strong>
            <p>${data.content}</p>
            <small>${data.timestamp}</small>
        `;
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    });
  
      socket.on('status', function(data) {
        const statusDiv = document.createElement('div');
        statusDiv.className = 'message status';
        statusDiv.innerHTML = `<em>${data.msg}</em>`;
        chatMessages.appendChild(statusDiv);
        scrollToBottom();

        if (data.msg.startsWith('Error:')) {
            console.error(data.msg);
            // 필요한 경우 사용자에게 오류 메시지를 표시하거나 다른 처리를 수행할 수 있습니다.
          }        
      });
  
      socket.on('update_participants', function(data) {
        updateParticipantList(data.participants);
      });
  
      messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (messageInput.value) {
          socket.emit('message', {room: CHAT_ROOM_ID, msg: messageInput.value});
          messageInput.value = '';
        }
      });
  
      leaveRoomBtn.addEventListener('click', function(e) {
        e.preventDefault();
        socket.emit('leave', {room: CHAT_ROOM_ID});
      
        fetch(LEAVE_CHAT_ROOM_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
          },
          credentials: 'same-origin'
        }).then(response => {
          if (response.ok) {
            window.location.href = CHAT_LIST_URL;  
        } else {
            console.error('채팅방을 나가는데 실패했습니다.');
          }
        });
      });
  
      function updateParticipantList(participants) {
        participantList.innerHTML = '';
        participants.forEach(function(participant) {
          const li = document.createElement('li');
          li.textContent = participant.name;
          if (participant.id === CHAT_ROOM_CREATOR_ID) {
            const span = document.createElement('span');
            span.className = 'badge badge-primary';
            span.textContent = '방장';
            li.appendChild(span);
          }
          participantList.appendChild(li);
        });
      }
  
      scrollToBottom();
    }
  });