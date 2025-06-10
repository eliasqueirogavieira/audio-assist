def get_html_content() -> str:
    """Return the HTML content for the web UI"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-Time AI Audio Assistant</title>
    <!-- Markdown parsing and HTML sanitization libraries -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            width: 100%;
            max-width: 1400px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #dc3545;
            animation: pulse 2s infinite;
        }
        
        .status-dot.connected {
            background: #28a745;
        }
        
        .status-dot.listening {
            background: #ffc107;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .controls-container {
            display: flex;
            flex-direction: row;
            align-items: stretch;
            gap: 16px;
            margin-bottom: 20px;
            flex-wrap: wrap; /* Allow wrapping on mobile */
        }
        
        .language-selector {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            flex: 1; /* Take up available space */
            min-width: 250px; /* Minimum width before wrapping */
        }
        
        .language-selector label {
            font-weight: 600;
            color: #333;
        }
        
        .language-dropdown {
            padding: 8px 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            background: white;
            color: #333;
            cursor: pointer;
            transition: border-color 0.3s ease;
        }
        
        .language-dropdown:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .language-dropdown:hover {
            border-color: #667eea;
        }
        
        .model-selector {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            flex: 1; /* Take up available space */
            min-width: 250px; /* Minimum width before wrapping */
        }
        
        .model-selector label {
            font-weight: 600;
            color: #333;
        }
        
        .model-dropdown {
            padding: 8px 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            background: white;
            color: #333;
            cursor: pointer;
            transition: border-color 0.3s ease;
            min-width: 200px;
        }
        
        .model-dropdown:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .model-dropdown:hover {
            border-color: #667eea;
        }
        
        .model-dropdown:disabled {
            background-color: #f8f9fa;
            cursor: not-allowed;
            opacity: 0.6;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .chat-container {
            background: white;
            border-radius: 15px;
            height: 70vh;
            overflow-y: auto;
            padding: 20px;
            border: 2px solid #e9ecef;
            margin-bottom: 20px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .message.assistant {
            background: #f8f9fa;
            color: #333;
            border-left: 4px solid #667eea;
        }
        
        .message.transcription {
            background: #e3f2fd;
            color: #1565c0;
            border-left: 4px solid #2196f3;
            font-style: italic;
        }
        
        .message .timestamp {
            font-size: 0.8rem;
            opacity: 0.7;
            margin-top: 5px;
        }
        
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 10px;
            padding: 12px 16px;
            background: #f8f9fa;
            border-radius: 15px;
            margin-bottom: 15px;
            max-width: 80%;
        }
        
        .typing-indicator.active {
            display: flex;
        }
        
        .typing-dots {
            display: flex;
            gap: 4px;
        }
        
        .typing-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        .input-area {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .text-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .text-input:focus {
            border-color: #667eea;
        }
        
        .send-btn {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 0.9rem;
        }
        
        /* Markdown formatting styles */
        .message p {
            margin-bottom: 0.8em;
        }
        
        .message h1, .message h2, .message h3, .message h4, .message h5, .message h6 {
            margin: 1em 0 0.5em 0;
            font-weight: bold;
        }
        
        .message h1 { font-size: 1.5em; }
        .message h2 { font-size: 1.3em; }
        .message h3 { font-size: 1.1em; }
        
        .message strong {
            font-weight: bold;
        }
        
        .message em {
            font-style: italic;
        }
        
        .message ul, .message ol {
            margin: 0.5em 0;
            padding-left: 1.5em;
        }
        
        .message li {
            margin-bottom: 0.3em;
        }
        
        .message pre {
            background-color: #f5f5f5;
            padding: 0.8em;
            border-radius: 6px;
            margin: 0.8em 0;
            overflow-x: auto;
            border-left: 3px solid #667eea;
        }
        
        .message code {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .message pre code {
            background-color: transparent;
            padding: 0;
            border-radius: 0;
            display: block;
            white-space: pre;
            word-wrap: normal;
        }
        
        .message :not(pre) > code {
            background-color: #f0f0f0;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 0.85em;
        }
        
        .message blockquote {
            border-left: 4px solid #ddd;
            margin: 0.8em 0;
            padding-left: 1em;
            color: #666;
            font-style: italic;
        }
        
        .message hr {
            border: none;
            border-top: 1px solid #ddd;
            margin: 1em 0;
        }
        
        .message table {
            border-collapse: collapse;
            margin: 0.8em 0;
            width: 100%;
        }
        
        .message th, .message td {
            border: 1px solid #ddd;
            padding: 0.4em 0.8em;
            text-align: left;
        }
        
        .message th {
            background-color: #f5f5f5;
            font-weight: bold;
        }

        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .controls-container {
                flex-direction: column; /* Stack dropdowns vertically on mobile */
                gap: 12px;
            }
            
            .language-selector,
            .model-selector {
                min-width: unset; /* Remove minimum width constraint */
                flex: none; /* Don't grow to fill space */
            }
            
            .controls {
                flex-direction: column;
                align-items: center;
            }
            
            .btn {
                width: 100%;
                max-width: 250px;
            }
            
            .chat-container {
                height: 60vh;
            }
            
            .message {
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 AI Audio Assistant</h1>
            <p>Speak naturally and get real-time AI responses</p>
        </div>
        
        <div class="status-bar">
            <div class="status-indicator">
                <div class="status-dot" id="connectionStatus"></div>
                <span id="connectionText">Disconnected</span>
            </div>
            <div class="status-indicator">
                <div class="status-dot" id="listeningStatus"></div>
                <span id="listeningText">Not Listening</span>
            </div>
        </div>
        
        <div class="controls-container">
            <div class="language-selector">
                <label for="languageSelect">🌐 Language:</label>
                <select id="languageSelect" class="language-dropdown">
                    <option value="en-US">English (Global)</option>
                    <option value="en-US-accent">English (Spanish Accent)</option>
                    <option value="pt-BR">Portuguese (Brazil)</option>
                </select>
            </div>
            
            <div class="model-selector">
                <label for="modelSelect">🤖 AI Model:</label>
                <select id="modelSelect" class="model-dropdown">
                    <!-- Options will be populated dynamically via WebSocket -->
                    <option value="">Loading models...</option>
                </select>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" id="startBtn" onclick="startListening()">
                🎤 Start Listening
            </button>
            <button class="btn btn-danger" id="stopBtn" onclick="stopListening()" disabled>
                ⏹️ Stop Listening
            </button>
            <button class="btn btn-secondary" onclick="clearChat()">
                🗑️ Clear Chat
            </button>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message assistant">
                <div>👋 Hello! I'm your AI assistant. Click "Start Listening" to begin our conversation, or type a message below.</div>
                <div class="timestamp" id="welcomeTime"></div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <div>🤖 AI is thinking</div>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" class="text-input" id="textInput" placeholder="Type a message or use voice input..." onkeypress="handleKeyPress(event)">
            <button class="send-btn" onclick="sendTextMessage()">Send</button>
        </div>
        
        <div class="footer">
            <p>🚀 Powered by Real-Time AI • WebSocket Connected</p>
        </div>
    </div>

    <script>
        let socket = null;
        let isListening = false;
        let currentResponse = '';
        
        // Configure marked.js for GitHub Flavored Markdown
        marked.setOptions({
            gfm: true,        // Use GitHub Flavored Markdown
            breaks: true,     // Convert single newlines into <br>
            mangle: false,    // To avoid obfuscating email addresses
            headerIds: false  // To avoid creating ids for headers
        });
        
        // Initialize WebSocket connection
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            socket = new WebSocket(wsUrl);
            
            socket.onopen = function(event) {
                console.log('WebSocket connected');
                updateConnectionStatus(true);
                addMessage('system', '✅ Connected to AI Assistant', new Date());
                
                // Send language preference when connected
                loadLanguagePreference();
                setLanguage();
            };
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };
            
            socket.onclose = function(event) {
                console.log('WebSocket disconnected');
                updateConnectionStatus(false);
                addMessage('system', '❌ Disconnected from AI Assistant', new Date());
                
                // Attempt to reconnect after 3 seconds
                setTimeout(initWebSocket, 3000);
            };
            
            socket.onerror = function(event) {
                console.error('WebSocket error:', event);
                addMessage('system', '⚠️ Connection error occurred', new Date());
            };
        }
        
        function handleWebSocketMessage(data) {
            switch(data.type) {
                case 'transcription':
                    addMessage('transcription', `🎙️ ${data.content}`, new Date(data.timestamp * 1000));
                    break;
                
                case 'status':
                    if (data.content === 'thinking') {
                        showTypingIndicator();
                    }
                    break;
                
                case 'response_chunk':
                    hideTypingIndicator();
                    updateStreamingResponse(data.content, data.full_content);
                    break;
                
                case 'response_complete':
                    hideTypingIndicator();
                    finalizeResponse(data.content, new Date(data.timestamp * 1000));
                    break;
                
                case 'listening_started':
                    updateListeningStatus(true);
                    break;
                
                case 'listening_stopped':
                    updateListeningStatus(false);
                    break;
                
                case 'history_cleared':
                    clearChatContainer();
                    addMessage('system', '🗑️ Chat history cleared', new Date());
                    break;
                
                case 'language_changed':
                    addMessage('system', `🌐 Language changed to: ${data.content}`, new Date());
                    break;
                
                case 'available_models':
                    populateModelDropdown(data.models, data.current_model);
                    break;
                
                case 'model_changed':
                    if (data.status === 'success') {
                        addMessage('system', `🤖 Model changed to: ${data.new_model_display_name}`, new Date(data.timestamp * 1000));
                        enableModelDropdown();
                    }
                    break;
                
                case 'error':
                    hideTypingIndicator();
                    addMessage('system', `❌ Error: ${data.content}`, new Date(data.timestamp * 1000));
                    enableModelDropdown();
                    break;
            }
        }
        
        function updateConnectionStatus(connected) {
            const statusDot = document.getElementById('connectionStatus');
            const statusText = document.getElementById('connectionText');
            
            if (connected) {
                statusDot.classList.add('connected');
                statusText.textContent = 'Connected';
            } else {
                statusDot.classList.remove('connected');
                statusText.textContent = 'Disconnected';
            }
        }
        
        function updateListeningStatus(listening) {
            const statusDot = document.getElementById('listeningStatus');
            const statusText = document.getElementById('listeningText');
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            
            isListening = listening;
            
            if (listening) {
                statusDot.classList.add('listening');
                statusText.textContent = 'Listening...';
                startBtn.disabled = true;
                stopBtn.disabled = false;
            } else {
                statusDot.classList.remove('listening');
                statusText.textContent = 'Not Listening';
                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
        }
        
        function startListening() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({type: 'start_listening'}));
                
                // Also call the HTTP endpoint to start audio capture
                fetch('/start-audio')
                    .then(response => response.json())
                    .then(data => console.log('Audio started:', data))
                    .catch(error => console.error('Error starting audio:', error));
            }
        }
        
        function stopListening() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({type: 'stop_listening'}));
                
                // Also call the HTTP endpoint to stop audio capture
                fetch('/stop-audio')
                    .then(response => response.json())
                    .then(data => console.log('Audio stopped:', data))
                    .catch(error => console.error('Error stopping audio:', error));
            }
        }
        
        function clearChat() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({type: 'clear_history'}));
            }
            clearChatContainer();
        }
        
        function clearChatContainer() {
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.innerHTML = '';
        }
        
        function sendTextMessage() {
            const textInput = document.getElementById('textInput');
            const message = textInput.value.trim();
            
            if (message && socket && socket.readyState === WebSocket.OPEN) {
                // Add user message to chat
                addMessage('user', message, new Date());
                
                // Send to server
                socket.send(JSON.stringify({
                    type: 'text_input',
                    content: message
                }));
                
                // Clear input
                textInput.value = '';
            }
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendTextMessage();
            }
        }
        
        function addMessage(type, content, timestamp) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            const timeStr = timestamp.toLocaleTimeString();
            messageDiv.innerHTML = `
                <div>${content}</div>
                <div class="timestamp">${timeStr}</div>
            `;
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        let currentResponseElement = null;
        
        function updateStreamingResponse(chunk, fullContent) {
            if (!currentResponseElement) {
                const chatContainer = document.getElementById('chatContainer');
                currentResponseElement = document.createElement('div');
                currentResponseElement.className = 'message assistant';
                chatContainer.appendChild(currentResponseElement);
            }
            
            // Parse markdown and sanitize HTML
            const rawHtml = marked.parse(fullContent);
            const sanitizedHtml = DOMPurify.sanitize(rawHtml);
            
            currentResponseElement.innerHTML = `
                <div>${sanitizedHtml}</div>
                <div class="timestamp">Responding...</div>
            `;
            
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function finalizeResponse(content, timestamp) {
            if (currentResponseElement) {
                const timeStr = timestamp.toLocaleTimeString();
                
                // Parse markdown and sanitize HTML for final response
                const rawHtml = marked.parse(content);
                const sanitizedHtml = DOMPurify.sanitize(rawHtml);
                
                currentResponseElement.innerHTML = `
                    <div>${sanitizedHtml}</div>
                    <div class="timestamp">${timeStr}</div>
                `;
                currentResponseElement = null;
            }
        }
        
        function showTypingIndicator() {
            document.getElementById('typingIndicator').classList.add('active');
        }
        
        function hideTypingIndicator() {
            document.getElementById('typingIndicator').classList.remove('active');
        }
        
        function setLanguage() {
            const languageSelect = document.getElementById('languageSelect');
            const selectedLanguage = languageSelect.value;
            
            if (socket && socket.readyState === WebSocket.OPEN) {
                // Map display value to API value (for Spanish accent)
                const apiLanguage = selectedLanguage === 'en-US-accent' ? 'en-US' : selectedLanguage;
                
                const message = {
                    type: 'set_language',
                    language: apiLanguage
                };
                
                socket.send(JSON.stringify(message));
                console.log('Language preference sent:', apiLanguage);
                
                // Save user preference
                localStorage.setItem('userLanguage', selectedLanguage);
            }
        }
        
        function loadLanguagePreference() {
            const savedLanguage = localStorage.getItem('userLanguage');
            if (savedLanguage) {
                const languageSelect = document.getElementById('languageSelect');
                languageSelect.value = savedLanguage;
                // Send language preference when connection is established
                if (socket && socket.readyState === WebSocket.OPEN) {
                    setLanguage();
                }
            }
        }
        
        function populateModelDropdown(models, currentModel) {
            const modelSelect = document.getElementById('modelSelect');
            modelSelect.innerHTML = ''; // Clear existing options
            
            // Add options for each available model
            Object.entries(models).forEach(([displayName, modelId]) => {
                const option = document.createElement('option');
                option.value = modelId;
                option.textContent = displayName;
                if (modelId === currentModel) {
                    option.selected = true;
                }
                modelSelect.appendChild(option);
            });
            
            // Enable the dropdown
            modelSelect.disabled = false;
            
            // Load saved model preference
            loadModelPreference();
        }
        
        function setModel() {
            const modelSelect = document.getElementById('modelSelect');
            const selectedModel = modelSelect.value;
            
            if (socket && socket.readyState === WebSocket.OPEN) {
                // Disable dropdown during switch to prevent rapid switching
                disableModelDropdown();
                
                const message = {
                    type: 'set_model',
                    model: selectedModel
                };
                
                socket.send(JSON.stringify(message));
                console.log('Model switch request sent:', selectedModel);
                
                // Save user preference
                localStorage.setItem('userModel', selectedModel);
            }
        }
        
        function disableModelDropdown() {
            const modelSelect = document.getElementById('modelSelect');
            modelSelect.disabled = true;
        }
        
        function enableModelDropdown() {
            const modelSelect = document.getElementById('modelSelect');
            modelSelect.disabled = false;
        }
        
        function loadModelPreference() {
            const savedModel = localStorage.getItem('userModel');
            if (savedModel) {
                const modelSelect = document.getElementById('modelSelect');
                // Check if the saved model is available in the current options
                const options = Array.from(modelSelect.options);
                const matchingOption = options.find(option => option.value === savedModel);
                if (matchingOption) {
                    modelSelect.value = savedModel;
                    // Automatically switch to saved model if different from current
                    if (socket && socket.readyState === WebSocket.OPEN) {
                        setModel();
                    }
                }
            }
        }
        
        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            // Set welcome message timestamp
            document.getElementById('welcomeTime').textContent = new Date().toLocaleTimeString();
            
            // Initialize WebSocket connection
            initWebSocket();
            
            // Set up language selector event listener
            document.getElementById('languageSelect').addEventListener('change', setLanguage);
            
            // Set up model selector event listener
            document.getElementById('modelSelect').addEventListener('change', setModel);
            
            // Load saved language preference
            loadLanguagePreference();
            
            // Focus on text input
            document.getElementById('textInput').focus();
        });
        
        // Handle page visibility change to manage connections
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                // Page is hidden, you might want to pause some operations
                console.log('Page hidden');
            } else {
                // Page is visible, ensure connection is active
                console.log('Page visible');
                if (!socket || socket.readyState !== WebSocket.OPEN) {
                    initWebSocket();
                }
            }
        });
    </script>
</body>
</html>
    """