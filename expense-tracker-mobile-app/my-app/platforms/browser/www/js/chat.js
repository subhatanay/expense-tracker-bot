

function openLoginScreen() {
    localStorage.clear()
    window.location.href = `/index.html`;
}

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('sessionId'); 
    const userId = localStorage.getItem('userId');
    const loginToken = localStorage.getItem('token');
    const fullName = localStorage.getItem('fullName'); 

    const logoutBtn = document.getElementById('logoutBtn') 
    const names = fullName.split(" ")
    document.getElementById('profileIcon').textContent = getShorterName(fullName);
    

    if (!sessionId || !userId || !loginToken) {
        openLoginScreen();
        return;
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

    function loadPreviousChats() {
        fetch(`${backendUrl}/users/${userId}/sessions/${sessionId}/chat_events`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                 'Authorization': `Bearer ${loginToken}`
            }
        })
        .then(response => {
            if (response.status != 200) { 
                throw new Error('Unexpected error occured.');
            }
            if (response.status == 403) {
                throw new Error("Token expired. Please relogin.");
            }
            return response.json(); 
        })
        .then(data => {
            if (data.length == 0) {
                handleHelpCommand()
                return;
            }
            data.forEach(event => {
                appendMessage(event.prompt_req, 'user-message', event.created_date);   // User message
                appendMessage(event.prompt_res, 'server-message', event.created_date); // Server response
            });
        })
        .catch(error => {
            showErrorPopup(error)
            console.error('Error fetching previous chats:', error);
            if (error.message == "Token expired. Please relogin.") {
                openLoginScreen()
                
            }
        });
    }

    const chatContainer = document.getElementById('messageContainer');
    const chatInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendButton');

    // Function to append messages to the chat container
    function appendMessage(content, className,date) {
        const messageDate = document.createElement('span');
        messageDate.className = 'message-date';
        messageDate.textContent = new Date(date).toLocaleString(); 
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        messageDiv.innerHTML = content;
        messageDiv.appendChild(messageDate);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;  // Auto-scroll to the bottom
    }

    // Handle send button click
    sendBtn.addEventListener('click', function() {
        var userMessage = chatInput.value.trim();
        
        if (userMessage === "") return;  // Ignore if message is empty
        userMessage = userMessage.toLocaleLowerCase()
        
        const currentDate = new Date().toISOString();


        // Append the user's message to the chat
        appendMessage(userMessage, 'user-message', currentDate);
        if (userMessage.toLocaleLowerCase() === "help") {
            handleHelpCommand();
            chatInput.value = ""; 
            return;
        }
        chatInput.value = "";  // Clear the input box
        
        // Make POST request to send the message
        fetch(`${backendUrl}/v2/users/${userId}/sessions/${sessionId}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                 'Authorization': `Bearer ${loginToken}`
            },
            body: JSON.stringify({
                message: userMessage
            })
        })
        .then(response => {
            if (response.status == 400) {
                throw new Error("Invalid command");
            }
            if (response.status != 201) { 
                throw new Error('Unexpected error occured.');
            }
            if (response.status == 403) {
                throw new Error("Token expired. Please relogin.");
            }
            return response.json(); 
        })
        .then(data => {
            const serverMessage = data.prompt_res;  // Get server response
            appendMessage(serverMessage, 'server-message', currentDate);  // Append server message to chat
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorPopup(error)
            if (error.message == "Invalid command") {
                handleErrorWithHelpCommand()
            }
        });
    });
    loadPreviousChats();

    function handleErrorWithHelpCommand() {
        commands = `
        <h5>Oops! It looks like the command you provided is not recognized.</h5>
        <p>Not sure what to do? No worries, here's how you can use the Expense Tracker Bot:</p>

        <h6>Commands</h6>

        <ul>
            <li><strong>spent 1000 on groceries</strong> – Log an expense of 1000 for groceries.</li>
            <li><strong>log an expense of 1500 on dining on 01-07-2024</strong> – Record a dining expense of 1500.</li>
            <li><strong>received income of 3000 from salary</strong> – Log salary income of 3000.</li>
            <li><strong>report for this month</strong> – Generate a transaction report for this month</li>
            <li><strong>total month expenses</strong> – See total expenses for the month.</li>
            <li><strong>help</strong> – Display this help message.</li>
        </ul>`
        const currentDate = new Date().toISOString();
        appendMessage(commands, 'server-message', currentDate);
    }

    function handleHelpCommand() {
        coammds = `
        <h5>Expense Tracker Bot - Help</h5>
        <p>Welcome! Here are the commands you can use to track your expenses and income:</p>

        <h6>Commands</h6>

        <ul>
            <li><strong>spent 1000 on groceries</strong> – Log an expense of 1000 for groceries.</li>
            <li><strong>log an expense of 1500 on dining on 01-07-2024</strong> – Record a dining expense of 1500.</li>
            <li><strong>received income of 3000 from salary</strong> – Log salary income of 3000.</li>
            <li><strong>report for this month</strong> – Generate a transaction report for this month</li>
            <li><strong>total month expenses</strong> – See total expenses for the month.</li>
            <li><strong>help</strong> – Display this help message.</li>
        </ul>

        <p>Use these commands to stay on top of your finances!</p>
        `
    }
});

logoutBtn.addEventListener('click', function () {
    localStorage.clear()
    window.location.href = "index.html"
})

