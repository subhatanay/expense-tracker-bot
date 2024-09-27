document.addEventListener('DOMContentLoaded', function() {
    const userId = localStorage.getItem('userId');
    const loginToken = localStorage.getItem('token'); 
    const fullName = localStorage.getItem('fullName'); 

    // Elements
    const sessionList = document.getElementById('sessionList');
    const addSessionBtn = document.getElementById('addSessionBtn');
    const addSessionModal = $('#addSessionModal'); 
    const addSessionForm = document.getElementById('addSessionForm');
    const sessionNameInput = document.getElementById('sessionName');

    const errorPopup = document.getElementById('errorPopup');
    const successPopup = document.getElementById('successPopup');

    const logoutBtn = document.getElementById('logoutBtn')
    document.getElementById('profileIcon').textContent = getShorterName(fullName);

    // Function to show error popup
    function showErrorPopup(message) {
        errorPopup.textContent = message;
        errorPopup.classList.add('show');
        setTimeout(() => {
            errorPopup.classList.remove('show');
        }, 3000); // Hide after 3 seconds
    }

    // Function to show success popup
    function showSuccessPopup(message) {
        successPopup.textContent = message;
        successPopup.classList.add('show');
        setTimeout(() => {
            successPopup.classList.remove('show');
        }, 3000); // Hide after 3 seconds
    }

    // Function to open chat view
    function openChatView(sessionId) {
        window.location.href = `/chat.html?sessionId=${sessionId}`;
    }

    // Function to open login screen
    function openLoginScreen() {
        localStorage.clear();
        window.location.href = `/index.html`;
    }

    // Function to fetch and display sessions
    function fetchSessions() {
        if (userId && loginToken) {
            fetch(`${backendUrl}/users/${userId}/sessions`, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${loginToken}`
                },
            })
            .then(response => {
                if (response.status === 403) {
                    throw new Error("Token expired. Please relogin.");
                } else if (response.status !== 200) { 
                    throw new Error("Unexpected error occurred.");
                }
                return response.json(); 
            })
            .then(data => {
                displaySessions(data);
            })
            .catch(error => {
                console.error('Error fetching sessions:', error);
                showErrorPopup(error.message);
                if (error.message === "Token expired. Please relogin.") {
                    openLoginScreen();
                }
            });
        } else {
            openLoginScreen();
        }
    }

    function getShorterName(fullName) {
        if (!fullName) {
            return "AB"
        }
        const names = fullName.toLocaleUpperCase().split(" ")
        if (names.length ==2) {
            return names[0].toLocaleUpperCase().charAt(0) + names[1].toLocaleUpperCase().charAt(0);
        }  if (names.length ==1) { 
            return names[0].toLocaleUpperCase().charAt(0) ;
        } else {
            return "AB"
        }
    }

    // Function to display sessions
    function displaySessions(sessions) {
        sessionList.innerHTML = ''; // Clear existing sessions

        if (sessions.length === 0) {
            sessionList.innerHTML = '<p class="text-center text-muted">No expense sessions found. Click the plus button to add one.</p>';
            return;
        }

        sessions.forEach(session => {
            const sessionDiv = document.createElement('div');
            sessionDiv.className = 'session-item';
            
            const sessionInfo = document.createElement('div');
            const sessionName = document.createElement('p');
            sessionName.textContent = session.session_name;
            const sessionDate = document.createElement('small');
            sessionDate.textContent = `Created on: ${new Date(session.created_at).toLocaleDateString()}`;
    
            sessionInfo.appendChild(sessionName);
    
            sessionDiv.appendChild(sessionInfo);
            sessionDiv.setAttribute('data-session-id', session.session_id);
            sessionDiv.addEventListener('click', () => {
                openChatView(session.session_id);
            });
            sessionList.appendChild(sessionDiv);
        });
    }

    // Event listener for Add Session button
    addSessionBtn.addEventListener('click', function() {
        // Clear previous input
        sessionNameInput.value = '';
        // Show the modal
        addSessionModal.modal('show');
    });

    // Event listener for Add Session form submission
    addSessionForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const sessionName = sessionNameInput.value.trim();

        if (!sessionName) {
            showErrorPopup('Session name cannot be empty.');
            return;
        }

        // Disable the submit button to prevent multiple submissions
        const submitButton = document.getElementById('submitSessionBtn');
        submitButton.disabled = true;
        submitButton.textContent = 'Adding...';

        // Prepare the payload
        const payload = {
            "session_name": sessionName
        };

        fetch(`${backendUrl}/users/${userId}/sessions`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${loginToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (response.status !== 201) { 
                return response.json().then(data => {
                    throw new Error(data.message || 'Failed to add session.');
                });
            }
            return response.json(); 
        })
        .then(data => {
            // Close the modal
            addSessionModal.modal('hide');
            // Show success popup
            showSuccessPopup('Session added successfully.');
            // Reload or update the sessions list
            fetchSessions();
        })
        .catch(error => {
            console.error('Error adding session:', error);
            showErrorPopup(error.message);
        })
        .finally(() => {
            // Re-enable the submit button
            submitButton.disabled = false;
            submitButton.textContent = 'Add Session';
        });
    });

    logoutBtn.addEventListener('click', function () {
        localStorage.clear()
        window.location.href = "index.html"
    })

    // Initial fetch of sessions
    fetchSessions();
});

