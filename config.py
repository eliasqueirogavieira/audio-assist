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
    
    # Gemini Configuration (Google AI)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-05-20")

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
    
    # Available models for dynamic selection
    # Key: User-friendly display name, Value: Internal model identifier  
    AVAILABLE_MODELS = {
        "Groq Llama3 8B (Free)": f"groq/{GROQ_MODEL}",
        "OpenAI GPT-3.5 Turbo": f"openai/{OPENAI_MODEL}",
        "Gemini 2.5 Flash Preview": f"gemini/{GEMINI_MODEL}",
        "Ollama Local": f"ollama/{OLLAMA_MODEL}",
        "Cohere Command Light": f"cohere/{COHERE_MODEL}"
    }
    
    # Default model for new connections
    DEFAULT_MODEL_ID = f"groq/{GROQ_MODEL}"
    
    # Model-specific performance tuning for real-time processing
    MODEL_CONFIG = {
        "groq": {
            "realtime_processing_lag_ms": 200,  # Groq is very fast
            "silence_threshold_ms": 1200,       # Shorter for quick response
            "max_tokens": 2000,
            "temperature": 0.6
        },
        "openai": {
            "realtime_processing_lag_ms": 500,  # OpenAI moderate speed
            "silence_threshold_ms": 1500,
            "max_tokens": 1500,
            "temperature": 0.7
        },
        "gemini": {
            "realtime_processing_lag_ms": 300,  # Gemini 2.0 Flash is fast
            "silence_threshold_ms": 1300,
            "max_tokens": 2000,
            "temperature": 0.6
        },
        "ollama": {
            "realtime_processing_lag_ms": 800,  # Local processing varies
            "silence_threshold_ms": 2000,
            "max_tokens": 1000,
            "temperature": 0.7
        },
        "cohere": {
            "realtime_processing_lag_ms": 600,
            "silence_threshold_ms": 1800,
            "max_tokens": 1500,
            "temperature": 0.7
        },
        "default": {  # Fallback for any unspecified models
            "realtime_processing_lag_ms": 500,
            "silence_threshold_ms": 1500,
            "max_tokens": 1500,
            "temperature": 0.7
        }
    }
    
    @staticmethod
    def get_model_config(model_id: str) -> dict:
        """Get performance config for a given model_id"""
        provider = model_id.split('/')[0] if '/' in model_id else 'default'
        return Config.MODEL_CONFIG.get(provider, Config.MODEL_CONFIG["default"])