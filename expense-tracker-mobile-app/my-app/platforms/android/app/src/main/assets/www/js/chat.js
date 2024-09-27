

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
        if (userMessage.toLocaleLowerCase() === "help" || !(userMessage.startsWith("add") || userMessage.startsWith("get"))) {
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
                handleHelpCommand()
            }
        });
    });
    loadPreviousChats();

    function handleHelpCommand() {
        commands = `
            Hey there! I’m your personal Expense Tracker Bot, ready to help you stay on top of your finances. Let’s get started!<br><br>\
Here are the commands you can use:<br><br>\
<ul>\
<li>add e &lt;Amount&gt; &lt;Category&gt; [Date] – Record an expense effortlessly!</li>\
<li>add i &lt;Amount&gt; &lt;Category&gt; [Date] – Log your income in seconds!</li>\
<li>get report day/month/year &lt;expenses/income/all&gt; – Generate detailed reports whenever you need.</li>\
<li>get total day/month/year &lt;expenses/income/all&gt; – Quickly see your total expenses or income.</li>\
<li>help – Need assistance? Just ask for help!</li>\
</ul>
        `
        const currentDate = new Date().toISOString();
        appendMessage(commands, 'server-message', currentDate);
    }
});

logoutBtn.addEventListener('click', function () {
    localStorage.clear()
    window.location.href = "index.html"
})

