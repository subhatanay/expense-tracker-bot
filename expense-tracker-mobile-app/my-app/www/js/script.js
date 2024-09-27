document.addEventListener('DOMContentLoaded', function() {
    // Initialize Materialize components
    M.AutoInit();

    // Check if user ID is in local storage
    if (localStorage.getItem('userId')) {
        showSessionsPage();
    } else {
        showLoginPage();
    }

    // Event listener for login button
    document.getElementById('login-btn').addEventListener('click', function() {
        const userId = document.getElementById('user-id').value;
        if (userId) {
            localStorage.setItem('userId', userId);
            showSessionsPage();
        } else {
            alert('Please enter a User ID');
        }
    });

    // Sample session data
    const sessions = [
        { id: 1, name: 'Session 1' },
        { id: 2, name: 'Session 2' }
    ];

    function showSessionsPage() {
        document.getElementById('login-page').style.display = 'none';
        document.getElementById('sessions-page').style.display = 'block';
        
        const sessionsList = document.getElementById('sessions-list');
        sessionsList.innerHTML = '';
        sessions.forEach(session => {
            const li = document.createElement('li');
            li.className = 'collection-item';
            li.textContent = session.name;
            li.dataset.id = session.id;
            li.addEventListener('click', function() {
                showChatPage(session.id, session.name);
            });
            sessionsList.appendChild(li);
        });
    }

    function showChatPage(sessionId, sessionName) {
        document.getElementById('sessions-page').style.display = 'none';
        document.getElementById('chat-page').style.display = 'block';
        document.getElementById('chat-session-name').textContent = sessionName;

        document.getElementById('send-btn').addEventListener('click', function() {
            const message = document.getElementById('chat-message').value;
            if (message) {
                addChatMessage('sent', message);
                document.getElementById('chat-message').value = '';

                // Simulate a server response
                setTimeout(() => {
                    addChatMessage('received', 'Server response to: ' + message);
                }, 1000);
            }
        });
    }

    function addChatMessage(type, message) {
        const chatBox = document.getElementById('chat-box');
        const div = document.createElement('div');
        div.className = `message ${type}`;
        div.textContent = message;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function showLoginPage() {
        document.getElementById('login-page').style.display = 'block';
        document.getElementById('sessions-page').style.display = 'none';
        document.getElementById('chat-page').style.display = 'none';
    }
});