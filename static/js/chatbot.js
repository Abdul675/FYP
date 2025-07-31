const chatArea = document.getElementById("chatArea");
const historyList = document.getElementById("historyList");
let currentChat = [];
let chatHistory = [];

function addMessage(content, sender) {
  const msg = document.createElement("div");
  msg.className = `chat-message ${sender}`;
  msg.textContent = content;
  chatArea.appendChild(msg);
  chatArea.scrollTop = chatArea.scrollHeight;
  
  currentChat.push({ content, sender });
}

function addToHistory() {
  if (currentChat.length > 0) {
    const chatEntry = {
      id: Date.now(),
      messages: [...currentChat],
      preview: currentChat[0].content.substring(0, 30) + "...",
      timestamp: new Date().toLocaleTimeString()
    };
    
    chatHistory.unshift(chatEntry);
    
    updateHistoryDisplay();
    
    currentChat = [];
  }
}

function updateHistoryDisplay() {
  historyList.innerHTML = '';
  
  chatHistory.forEach(chat => {
    const historyItem = document.createElement("div");
    historyItem.className = "history-item";
    
    const preview = document.createElement("div");
    preview.className = "history-preview";
    preview.textContent = chat.preview;
    
    const time = document.createElement("div");
    time.className = "history-time";
    time.textContent = chat.timestamp;
    
    historyItem.appendChild(preview);
    historyItem.appendChild(time);
    
    historyItem.onclick = () => loadChat(chat.messages);
    historyList.appendChild(historyItem);
  });
}

function loadChat(messages) {
  chatArea.innerHTML = '<div id="chatOverlay">How can I help you today?</div>';
  document.getElementById("chatOverlay").style.display = "none";
  messages.forEach(msg => addMessage(msg.content, msg.sender));
}

function sendMessage() {
  const input = document.getElementById("chatInput");
  const userText = input.value.trim();
  if (!userText) return;

  document.getElementById("chatOverlay").style.display = "none";

  addMessage(userText, "user");
  input.value = "";

  const botMsg = document.createElement("div");
  botMsg.className = "chat-message bot";
  botMsg.textContent = "Typing...";
  chatArea.appendChild(botMsg);
  chatArea.scrollTop = chatArea.scrollHeight;

  fetch('http://localhost:5000/api/chatbot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userText })
  })
  .then(response => response.json())
  .then(data => {
    botMsg.textContent = data.response || data.error || "No response from server.";
    chatArea.scrollTop = chatArea.scrollHeight;
    addToHistory();
  })
  .catch(error => {
    botMsg.textContent = "⚠️ Error connecting to server.";
    console.error("Error:", error);
  });
  
}

function generateBotReply(text) {
  if (text.toLowerCase().includes("hello")) return "Hi there! How can I assist you?";
  if (text.toLowerCase().includes("services")) return "We offer web, app, and AI development services.";
  return "I'm here to help you with anything you need!";
}

function startVoice() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    document.getElementById('chatInput').value = transcript;
    sendMessage();
  };
  recognition.start();
}

function toggleHistory() {
  const historyPanel = document.querySelector('.history-panel');
  const chatWrapper = document.querySelector('.chat-wrapper');
  const toggleButton = document.querySelector('.history-toggle img');
  
  historyPanel.classList.toggle('hidden');
  chatWrapper.classList.toggle('expanded');

  if (historyPanel.classList.contains('hidden')) {
    toggleButton.src = "https://img.icons8.com/fluency/48/chevron-right.png";
  } else {
    toggleButton.src = "https://img.icons8.com/fluency/48/chevron-left.png";
  }
} 