import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # LLM API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Choose your LLM provider: 'openai', 'groq', 'ollama', 'huggingface', 'cohere'
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Default to Groq (free)

    # OpenAI Configuration
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # Groq Configuration (FREE with high rate limits)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # Fast and free

    # Ollama Configuration (LOCAL - completely free)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")  # Lightweight model

    # HuggingFace Configuration (FREE with rate limits)
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium")

    # Cohere Configuration (FREE tier available)
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    COHERE_MODEL = os.getenv("COHERE_MODEL", "command-light")

    # Audio Configuration
    AUDIO_CHUNK_SIZE = 4096
    AUDIO_FORMAT = 16
    AUDIO_CHANNELS = 1
    AUDIO_RATE = 16000

    # Real-time processing
    SILENCE_THRESHOLD = 200
    SILENCE_DURATION = 1.5

    # Server Configuration
    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", 8000))

    # UI Configuration
    UI_TITLE = "Real-Time AI Audio Assistant"
    
    # Language Configuration
    DEFAULT_LANGUAGE = "en-US"
    
    # Dictionary of supported languages with their Google Speech API codes
    SUPPORTED_LANGUAGES = {
        "en-US": "English (Global)",
        "pt-BR": "Portuguese (Brazil)"
    }