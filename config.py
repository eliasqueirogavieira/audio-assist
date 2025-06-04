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
    AUDIO_CHUNK_SIZE = 4096  # Larger chunks for system audio
    AUDIO_FORMAT = 16  # 16-bit
    AUDIO_CHANNELS = 1  # Mono
    AUDIO_RATE = 16000  # 16kHz sample rate

    # Real-time processing
    SILENCE_THRESHOLD = 200  # Lower threshold for system audio
    SILENCE_DURATION = 1.5  # Shorter silence duration for more responsive detection

    # Server Configuration
    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", 8000))

    # UI Configuration
    UI_TITLE = "Real-Time AI Audio Assistant"