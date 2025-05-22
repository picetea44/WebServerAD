// Chat Widget JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get current user from meta tag
    const currentUserMeta = document.querySelector('meta[name="current-user"]');
    if (!currentUserMeta) return; // Not logged in

    const currentUser = currentUserMeta.getAttribute('content');
    let chatSocket = null;
    let currentRoomId = null;
    let lastUserId = null;


    const chatToggle = document.getElementById('chat-toggle');
    const chatDropdown = document.getElementById('chat-dropdown');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send');
    const chatPartner = document.getElementById('chat-partner');

    // 채팅 아이콘 강조 효과 추가 함수
    function highlightChatIcon() {
        const chatIcon = document.querySelector('.chat-icon');
        if (chatIcon) {
            chatIcon.classList.add('chat-icon-active');
            setTimeout(() => {
                chatIcon.classList.remove('chat-icon-active');
            }, 2000);
        }
    }

    // 채팅 드롭다운 열기 함수
    function openChatDropdown() {
        if (chatDropdown) {
            chatDropdown.classList.add('show');
            highlightChatIcon();
        }
    }


    // Handle chat-with-btn clicks
    document.querySelectorAll('.chat-with-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();

        const userId = this.getAttribute('data-user-id');
            const partnerName = this.getAttribute('data-partner');
            lastUserId = userId; // 마지막 사용자 ID 저장

            // 채팅창 열기
            openChatDropdown();

            // 페이지 스크롤을 상단으로 이동시켜 채팅창이 보이도록 함
            window.scrollTo({top: 0, behavior: 'smooth'});

            // Fetch chat room
            fetch(`/chat/with/${userId}/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                connectToChatRoom(data.room_id, partnerName);
            })
            .catch(error => {
                console.error('Error fetching room:', error);
                showErrorMessage();
            });

            // Prevent dropdown from closing when clicking inside
            chatDropdown.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });
    });


    if (!chatToggle) return; // Chat toggle button not found

    // Prevent dropdown from closing when clicking inside (add this listener only once)
    chatDropdown.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Initialize chat dropdown
    chatToggle.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();

    // 클래스 직접 조작으로 토글 기능 구현
    if (chatDropdown.classList.contains('show')) {
        chatDropdown.classList.remove('show');
        // 웹소켓 연결 닫기
        if (chatSocket) {
            chatSocket.close();
            chatSocket = null;
        }
    } else {
        chatDropdown.classList.add('show');
        // 최신 채팅방 가져오기
        fetchLatestRoom();
    }
});

// 문서 전체에 클릭 이벤트 추가하여 외부 클릭 시 드롭다운 닫기
document.addEventListener('click', function(e) {
    if (chatDropdown && chatToggle) {
        // 드롭다운이나 토글 버튼 이외의 영역 클릭 시 드롭다운 닫기
        const isChatWithBtn = e.target.closest('.chat-with-btn');
        if (!chatDropdown.contains(e.target) && !chatToggle.contains(e.target) && !isChatWithBtn) {
            chatDropdown.classList.remove('show');

            // 웹소켓 연결 닫기
            if (chatSocket) {
                chatSocket.close();
                chatSocket = null;
            }

        }
    }
});


    // Fetch latest chat room
    function fetchLatestRoom() {
        fetch('/chat/latest/')
            .then(response => {
                if (response.status === 204) {
                    // No recent chat
                    showEmptyChatMessage();
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    // Connect to chat room
                    connectToChatRoom(data.room_id, data.partner);
                }
            })
            .catch(error => {
                console.error('Error fetching latest room:', error);
                showErrorMessage();
            });
    }

    // 채팅 내역이 없을 때 표시하는 메시지 수정
    function showEmptyChatMessage() {
        chatPartner.textContent = '채팅';
        chatMessages.innerHTML = `
            <div class="no-chat-message">
                채팅을 원하는 유저를 먼저 선택하세요.<br>
                프로필 페이지에서 채팅하기 버튼을 누르면<br>
                대화를 시작할 수 있습니다.
            </div>
        `;


        // Hide input container
        document.getElementById('chat-input-container').style.display = 'none';
    }

    // Show error message
    function showErrorMessage() {
        chatPartner.textContent = 'Error';
        chatMessages.innerHTML = `
            <div class="no-chat-message">
                채팅을 불러오는 중 오류가 발생했습니다.<br>
                다시 시도해주세요.
            </div>
        `;
    }

    // Connect to chat room
    function connectToChatRoom(roomId, partnerName) {
        // Update UI
        chatPartner.textContent = partnerName;
        chatMessages.innerHTML = '<div class="loading-message">Loading messages...</div>';
        document.getElementById('chat-input-container').style.display = 'flex';

        // Store current room ID
        currentRoomId = roomId;

        // Close existing socket if any
        if (chatSocket) {
            chatSocket.close();
        }

        // Connect to WebSocket
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/chat/${roomId}/`;

        chatSocket = new WebSocket(wsUrl);

        chatSocket.onopen = function(e) {
            console.log('WebSocket connection established');
        };

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);

            if (data.type === 'chat_history') {
                // Display chat history
                displayChatHistory(data.messages);
            } else if (data.type === 'chat_message') {
                // Add new message
                addChatMessage(data);
            }
        };

        chatSocket.onclose = function(e) {
            console.log('WebSocket connection closed');
        };

        chatSocket.onerror = function(e) {
            console.error('WebSocket error:', e);
            showErrorMessage();
        };
    }

    // Display chat history
    function displayChatHistory(messages) {
        chatMessages.innerHTML = '';

        if (messages.length === 0) {
            chatMessages.innerHTML = '<div class="loading-message">아직 대화 내용이 없습니다. 첫 메시지를 보내보세요!\n</div>';
            return;
        }

        messages.forEach(message => {
            addChatMessage(message);
        });

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Add chat message
    function addChatMessage(message) {
        const isSent = message.sender === currentUser;
        const messageClass = isSent ? 'sent' : 'received';

        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${messageClass}`;

        // Format time
        const messageTime = new Date(message.sent_at);
        const formattedTime = messageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageElement.innerHTML = `
            ${!isSent ? `<div class="sender">${message.sender}</div>` : ''}
            <div class="text">${message.text}</div>
            <div class="time">${formattedTime}</div>
        `;

        chatMessages.appendChild(messageElement);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Send message
    function sendMessage() {
        const message = chatInput.value.trim();

        if (message && chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({
                'message': message
            }));

            chatInput.value = '';
        }
    }

    // Send message on button click
    chatSendBtn.addEventListener('click', sendMessage);

    // Send message on Enter key
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // This function is no longer needed as Bootstrap handles closing the dropdown
    // The WebSocket connection is closed in the hidden.bs.dropdown event handler

    // Export openChatRoom function for use in room.html
    window.openChatRoom = function(roomId) {
        // Fetch room details
        openChatDropdown();
        fetch(`/chat/with/${roomId}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            connectToChatRoom(data.room_id, data.partner);
        })
        .catch(error => {
            console.error('Error fetching room details:', error);
        });
    };
});
