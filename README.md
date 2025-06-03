# 🎤 Real-Time AI Audio Assistant

A modern, web-based application that listens to your voice in real-time and provides intelligent responses using LLM APIs (OpenAI GPT or Google Gemini). Built with Python, FastAPI, and WebSockets for seamless real-time communication.

## ✨ Features

- **Real-time audio transcription** using Google Speech Recognition
- **Live LLM responses** with streaming support
- **Modern web interface** with responsive design
- **WebSocket communication** for real-time updates
- **Multiple LLM providers** (OpenAI GPT, Google Gemini)
- **Conversation history** maintained per session
- **Clean architecture** with separated concerns

## 🏗️ Architecture

The application is structured with clean separation of concerns:

```
├── main.py              # FastAPI server and main entry point
├── config.py            # Configuration management
├── audio_handler.py     # Audio capture and transcription
├── llm_client.py        # LLM API integration
├── websocket_manager.py # WebSocket connection management
├── web_ui.py           # Web interface HTML/CSS/JS
├── requirements.txt     # Python dependencies
└── .env                # Environment variables (API keys)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Microphone access
- API key from OpenAI or Google (for LLM responses)

### Installation

1. **Clone or download the project files**

2. **Run the installation script** (Linux/macOS):
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   **Or install manually**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. **Configure your API keys**:
   Edit the `.env` file and add your API keys:
   ```bash
   # For OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   LLM_PROVIDER=openai
   
   # Or for Gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   LLM_PROVIDER=gemini
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Open your browser** to `http://localhost:8000`

## 🎯 How to Use

1. **Grant microphone permissions** when prompted by your browser
2. **Click "Start Listening"** to begin audio capture
3. **Speak naturally** - your speech will be transcribed in real-time
4. **Watch the AI respond** with streaming text responses
5. **Use the text input** as an alternative to voice input
6. **Clear chat history** anytime with the Clear button

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (`openai` or `gemini`) | `openai` |
| `OPENAI_API_KEY` | OpenAI API key | Required if using OpenAI |
| `GEMINI_API_KEY` | Google Gemini API key | Required if using Gemini |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-3.5-turbo` |
| `HOST` | Server host | `localhost` |
| `PORT` | Server port | `8000` |

### Audio Settings

Audio settings can be modified in `config.py`:

```python
AUDIO_CHUNK_SIZE = 1024      # Audio buffer size
AUDIO_RATE = 16000           # Sample rate (16kHz)
AUDIO_CHANNELS = 1           # Mono audio
SILENCE_THRESHOLD = 500      # Silence detection
SILENCE_DURATION = 2.0       # Seconds before processing
```

## 🛠️ System Dependencies

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-dev
```

### macOS
```bash
brew install portaudio
```

### Windows
- PyAudio wheels usually include PortAudio
- If issues occur, install Microsoft Visual C++ Build Tools

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/ws` | WebSocket | Real-time communication |
| `/start-audio` | GET | Start audio listening |
| `/stop-audio` | GET | Stop audio listening |
| `/status` | GET | Application status |

## 🔌 WebSocket Messages

The application uses WebSocket for real-time communication:

### Client → Server
```json
{"type": "start_listening"}
{"type": "stop_listening"}
{"type": "text_input", "content": "Hello AI"}
{"type": "clear_history"}
```

### Server → Client
```json
{"type": "transcription", "content": "Hello there", "timestamp": 1234567890}
{"type": "response_chunk", "content": "Hi! How", "full_content": "Hi! How"}
{"type": "response_complete", "content": "Hi! How can I help?", "timestamp": 1234567890}
```

## 🎨 UI Features

- **Responsive design** that works on desktop and mobile
- **Real-time status indicators** for connection and listening state
- **Smooth animations** and modern glassmorphism design
- **Message history** with timestamps
- **Typing indicators** during AI processing
- **Error handling** with user-friendly messages

## 🔒 Security Considerations

- API keys are stored in environment variables
- WebSocket connections are validated
- No audio data is permanently stored
- HTTPS support for production deployment

## 🚀 Production Deployment

For production deployment:

1. **Use HTTPS** and secure WebSocket connections (WSS)
2. **Set environment variables** securely
3. **Configure reverse proxy** (nginx/Apache)
4. **Use process manager** (PM2, systemd)
5. **Set up monitoring** and logging

Example nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 🛟 Troubleshooting

### Common Issues

1. **Microphone not working**:
   - Check browser permissions
   - Ensure microphone is not used by other apps
   - Try different browsers

2. **Audio transcription failing**:
   - Check internet connection (uses Google Speech API)
   - Verify microphone input levels
   - Try speaking closer to microphone

3. **LLM responses not working**:
   - Verify API keys in `.env` file
   - Check API quotas and billing
   - Monitor console for error messages

4. **WebSocket connection issues**:
   - Check firewall settings
   - Verify port 8000 is available
   - Try different browsers

### Debugging

Enable detailed logging by modifying `main.py`:
```python
uvicorn.run("main:app", host=Config.HOST, port=Config.PORT, log_level="debug")
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📞 Support

If you encounter any issues or have questions, please check the troubleshooting section first, then open an issue on the project repository.