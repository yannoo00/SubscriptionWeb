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

  function updateParticipantList(participants) {
      if (participantList) {
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
      } else {
          console.error('participant-list element not found');
      }
  }

  function addMessageToChat(data) {
      const messageDiv = document.createElement('div');
      messageDiv.className = `chat-message ${data.user_id === CURRENT_USER_ID ? 'chat-message-sender' : 'chat-message-receiver'}`;
      
      const contentDiv = document.createElement('div');
      contentDiv.className = 'chat-message-content';
      
      const senderSpan = document.createElement('span');
      senderSpan.className = 'chat-message-sender-name';
      senderSpan.textContent = `${data.username}: `;
      
      const textP = document.createElement('p');
      textP.textContent = data.content;
      
      const timeSpan = document.createElement('span');
      timeSpan.className = 'chat-message-time';
      timeSpan.textContent = new Date(data.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
      
      contentDiv.appendChild(senderSpan);
      contentDiv.appendChild(textP);
      contentDiv.appendChild(timeSpan);
      messageDiv.appendChild(contentDiv);
      
      chatMessages.appendChild(messageDiv);
      scrollToBottom();
  }

  if (chatMessages && messageForm && messageInput && leaveRoomBtn) {
      socket.on('connect', function() {
          socket.emit('join', {room: CHAT_ROOM_ID});
      });

      socket.on('message', function(data) {
          addMessageToChat(data);
      });

      socket.on('status', function(data) {
          const statusDiv = document.createElement('div');
          statusDiv.className = 'chat-message chat-message-status';
          statusDiv.innerHTML = `<em>${data.msg}</em>`;
          chatMessages.appendChild(statusDiv);
          scrollToBottom();

          if (data.msg.startsWith('Error:')) {
              console.error(data.msg);
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

      scrollToBottom();
  }

  // 초기 참여자 목록 설정
  if (typeof INITIAL_PARTICIPANTS !== 'undefined') {
      updateParticipantList(INITIAL_PARTICIPANTS);
  }
});