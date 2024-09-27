function sendchatrequest(request_prompt) {
    fetch('https://2ac5-103-175-169-161.ngrok-free.app/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: request_prompt
        })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json(); // Assuming the response is in JSON format
      })
      .then(data => {
        // Handle the response data
        addMessage(data.message, false)
      })
      .catch(error => {
        // Handle errors
        addMessage(error.message || "Error occured", false);
      });
}

const API_KEY = "AIzaSyC1kY8QZs1J83USpS6CmAUeGyTeHVcyLrU";
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

function addMessage(message, isUser) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function handleUserInput() {
    const message = userInput.value.trim();
    if (message) {
        addMessage(message, true);
        userInput.value = '';
        // Simulate bot response (replace with actual bot logic)
       
        sendchatrequest(message);
        
    } 
} 
sendButton.addEventListener('click', handleUserInput);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleUserInput();
    }
});

// Initial bot message
addMessage("Hello! How can I assist you today?", false);