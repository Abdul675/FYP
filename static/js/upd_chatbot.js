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

// Text message sending
function sendMessage(text = null) {
    const input = document.getElementById("chatInput");
    const userText = text || input.value.trim();
    if (!userText) return;

    document.getElementById("chatOverlay").style.display = "none";

    if (!text) {
        addMessage(userText, "user");
        input.value = "";
    }

    const botMsg = document.createElement("div");
    botMsg.className = "chat-message bot";
    botMsg.textContent = "Typing...";
    chatArea.appendChild(botMsg);
    chatArea.scrollTop = chatArea.scrollHeight;

    fetch('/api/chatbot', {
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


const FORMAT = 16; 
const CHANNELS = 1;
const RATE = 16000;
const CHUNK = 1024;
const RECORD_SECONDS = 5;

let audioContext;
let mediaStream;
let audioWorkletNode;
let audioChunks = [];
let isRecording = false;


const ELEVENLABS_API_KEY = 'sk_1d981ce453eddbc00891681e56569ea86297e2be23a3bc82'; // Replace with your API key

async function startVoice() {
    const voiceModal = document.getElementById('voiceModal');
    voiceModal.classList.add('active');
    isRecording = true;
    audioChunks = [];

    try {
        
        audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: RATE
        });

    
        mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: CHANNELS,
                sampleRate: RATE,
                sampleSize: FORMAT,
                echoCancellation: true,
                noiseSuppression: true
            }
        });

        
        const source = audioContext.createMediaStreamSource(mediaStream);
        const processor = audioContext.createScriptProcessor(CHUNK, CHANNELS, CHANNELS);

        processor.onaudioprocess = (e) => {
            if (isRecording) {
                const inputData = e.inputBuffer.getChannelData(0);
                // Convert Float32Array to Int16Array
                const pcmData = new Int16Array(inputData.length);
                for (let i = 0; i < inputData.length; i++) {
                    pcmData[i] = Math.max(-32768, Math.min(32767, Math.round(inputData[i] * 32768)));
                }
                audioChunks.push(pcmData);
            }
        };

        source.connect(processor);
        processor.connect(audioContext.destination);

     
        /*setTimeout(() => {
            if (isRecording) {
                submitVoice();
            }
        }, RECORD_SECONDS * 1000);*/

    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Error accessing microphone. Please ensure you have granted microphone permissions.');
        cancelVoice();
    }
}

async function submitVoice() {
    if (!isRecording) {
        console.error('No active recording');
        return;
    }

    isRecording = false;
    document.getElementById('voiceModal').classList.remove('active');
    document.getElementById('analyzingAnimation').classList.add('active');

    try {
        
        const wavBlob = await createWavFile(audioChunks);
        console.log('Audio chunks:', audioChunks.length);
        console.log('WAV blob size:', wavBlob.size, 'bytes');
        console.log('WAV blob type:', wavBlob.type);

        if (wavBlob.size === 0) {
            throw new Error('No audio data recorded');
        }

       
        const formData = new FormData();
        formData.append('file', wavBlob, 'recording.wav');
        formData.append('model_id', 'scribe_v1');
        formData.append('language_code', 'en');
        formData.append('tag_audio_events', 'true'); // Boolean values should be strings
        formData.append('diarize', 'true');

      
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + (pair[1] instanceof Blob ? 'Blob(' + pair[1].size + ' bytes)' : pair[1]));
        }

        // Call ElevenLabs API
        const response = await fetch('https://api.elevenlabs.io/v1/speech-to-text', {
            method: 'POST',
            headers: {
                'xi-api-key': ELEVENLABS_API_KEY
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('ElevenLabs API Error Details:', errorData);
            throw new Error(`ElevenLabs API error: ${response.status} - ${JSON.stringify(errorData)}`);
        }

        const data = await response.json();
        document.getElementById('analyzingAnimation').classList.remove('active');

        if (data.text) {
            addMessage(data.text, 'user');
            
            const aiResponse = await fetch('/api/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: data.text })
            }).then(res => res.json());

            if (aiResponse.response) {
                addMessage(aiResponse.response, 'bot');
            }
        } else {
            addMessage('Error: No speech detected', 'bot');
        }
        addToHistory();

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('analyzingAnimation').classList.remove('active');
        addMessage(`Error: ${error.message}`, 'bot');
    } finally {
        // Cleanup
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
        }
        if (audioContext) {
            await audioContext.close();
        }
        audioChunks = [];
    }
}

function cancelVoice() {
    isRecording = false;
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
    if (audioContext) {
        audioContext.close();
    }
    document.getElementById('voiceModal').classList.remove('active');
    document.getElementById('analyzingAnimation').classList.remove('active');
    audioChunks = [];
}


async function createWavFile(audioChunks) {
    const numChannels = CHANNELS;
    const sampleRate = RATE;
    const bitsPerSample = FORMAT;
    const bytesPerSample = bitsPerSample / 8;
    const blockAlign = numChannels * bytesPerSample;
    
  
    const totalLength = audioChunks.reduce((acc, chunk) => acc + chunk.length, 0);
    const dataLength = totalLength * bytesPerSample;
    const buffer = new ArrayBuffer(44 + dataLength);
    const view = new DataView(buffer);

 
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataLength, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * blockAlign, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitsPerSample, true);
    writeString(view, 36, 'data');
    view.setUint32(40, dataLength, true);

    // Write audio data
    let offset = 44;
    for (const chunk of audioChunks) {
        for (let i = 0; i < chunk.length; i++) {
            view.setInt16(offset, chunk[i], true);
            offset += 2;
        }
    }

    return new Blob([buffer], { type: 'audio/wav' });
}

function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

function toggleHistory() {
    const historyPanel = document.querySelector('.history-panel');
    historyPanel.classList.toggle('active');
}


document.getElementById("chatInput").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && isRecording) {
        submitVoice();
    } else if (event.key === 'Escape' && isRecording) {
        cancelVoice();
    }
}); 