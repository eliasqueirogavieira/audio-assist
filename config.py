import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Choose your LLM provider: 'openai' or 'gemini'
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    
    # OpenAI Configuration
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Audio Configuration
    AUDIO_CHUNK_SIZE = 1024
    AUDIO_FORMAT = 16  # 16-bit
    AUDIO_CHANNELS = 1  # Mono
    AUDIO_RATE = 16000  # 16kHz sample rate
    
    # Real-time processing
    SILENCE_THRESHOLD = 500  # Silence detection threshold
    SILENCE_DURATION = 2.0   # Seconds of silence before processing
    
    # Server Configuration
    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", 8000))
    
    # UI Configuration
    UI_TITLE = "Real-Time AI Audio Assistant"