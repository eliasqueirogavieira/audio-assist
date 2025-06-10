import openai
import asyncio
import aiohttp
import json
from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator
import google.generativeai as genai
from config import Config


class BaseLLMClient(ABC):
    """Abstract base class for all LLM clients"""
    
    def __init__(self, model: str, api_key: str = None):
        self.model = model
        self.api_key = api_key
        if api_key is not None and not api_key:
            raise ValueError(f"API key for {self.__class__.__name__} is not set")
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Provider-specific client initialization"""
        pass
    
    @abstractmethod
    async def get_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Generate streaming response from the LLM"""
        pass
    
    def _build_messages(self, text: str, conversation_history: list = None) -> list:
        """Build message array for API call"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Respond conversationally to what the user says. Keep responses concise but helpful."
            }
        ]
        
        if conversation_history:
            messages.extend(conversation_history[-10:])
        
        messages.append({"role": "user", "content": text})
        return messages


class OpenAIClient(BaseLLMClient):
    """OpenAI LLM client implementation"""
    
    def _initialize_client(self):
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
    
    async def get_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Get streaming response from OpenAI API"""
        messages = self._build_messages(text, conversation_history)
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1500,
                temperature=0.7,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"OpenAI Error: {str(e)}"


class GroqClient(BaseLLMClient):
    """Groq LLM client implementation"""
    
    def _initialize_client(self):
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    
    async def get_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Get streaming response from Groq API"""
        messages = self._build_messages(text, conversation_history)
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.6,
                top_p=0.9,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Groq Error: {str(e)}"


class GeminiClient(BaseLLMClient):
    """Google Gemini LLM client implementation"""
    
    def _initialize_client(self):
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
    
    async def get_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Get streaming response from Gemini API"""
        try:
            # Build conversation context for Gemini
            prompt = self._build_gemini_prompt(text, conversation_history)
            
            # Generate streaming response
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.generate_content(
                    prompt,
                    stream=True,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=2000,
                        temperature=0.6
                    )
                )
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"Gemini Error: {str(e)}"
    
    def _build_gemini_prompt(self, text: str, conversation_history: list = None) -> str:
        """Build prompt for Gemini API"""
        prompt = "You are a helpful AI assistant. Respond conversationally to what the user says. Keep responses concise but helpful.\n\n"
        
        if conversation_history:
            for msg in conversation_history[-6:]:
                if msg["role"] == "user":
                    prompt += f"Human: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"
        
        prompt += f"Human: {text}\nAssistant:"
        return prompt


class OllamaClient(BaseLLMClient):
    """Ollama local LLM client implementation"""
    
    def __init__(self, model: str, base_url: str = None):
        self.base_url = base_url or Config.OLLAMA_BASE_URL
        super().__init__(model, api_key=None)  # Ollama doesn't need API key
    
    def _initialize_client(self):
        # No client initialization needed for Ollama
        pass
    
    async def get_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Get streaming response from local Ollama instance"""
        try:
            messages = self._build_messages(text, conversation_history)
            prompt = self._messages_to_prompt(messages)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 1000
                        }
                    }
                ) as response:
                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line.decode('utf-8'))
                                if 'response' in chunk:
                                    yield chunk['response']
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"Ollama Error: {str(e)}"
    
    def _messages_to_prompt(self, messages: list) -> str:
        """Convert messages to a single prompt for Ollama"""
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"Human: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n\n"
        
        prompt += "Assistant: "
        return prompt


class CohereClient(BaseLLMClient):
    """Cohere LLM client implementation"""
    
    def _initialize_client(self):
        # No specific client initialization needed
        pass
    
    async def get_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Get streaming response from Cohere API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Build conversation context for Cohere
            chat_history = []
            if conversation_history:
                for msg in conversation_history[-6:]:
                    if msg["role"] == "user":
                        chat_history.append({"role": "USER", "message": msg["content"]})
                    elif msg["role"] == "assistant":
                        chat_history.append({"role": "CHATBOT", "message": msg["content"]})
            
            payload = {
                "message": text,
                "model": self.model,
                "chat_history": chat_history,
                "temperature": 0.7,
                "max_tokens": 1500,
                "stream": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.cohere.ai/v1/chat",
                    headers=headers,
                    json=payload
                ) as response:
                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line.decode('utf-8'))
                                if chunk.get("event_type") == "text-generation":
                                    yield chunk.get("text", "")
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"Cohere Error: {str(e)}"


class HuggingFaceClient(BaseLLMClient):
    """HuggingFace LLM client implementation"""
    
    def _initialize_client(self):
        # No specific client initialization needed
        pass
    
    async def get_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Get streaming response from HuggingFace API (simulated streaming)"""
        try:
            # Build conversational prompt
            prompt = self._build_hf_prompt(text, conversation_history)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api-inference.huggingface.co/models/{self.model}",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list) and len(result) > 0:
                            response_text = result[0].get("generated_text", "No response generated")
                        else:
                            response_text = str(result)
                        
                        # Simulate streaming by yielding words
                        words = response_text.split()
                        for word in words:
                            yield word + " "
                            await asyncio.sleep(0.05)  # Small delay for streaming effect
                    else:
                        error_text = await response.text()
                        yield f"HuggingFace Error: {response.status} - {error_text}"
        except Exception as e:
            yield f"HuggingFace Error: {str(e)}"
    
    def _build_hf_prompt(self, text: str, conversation_history: list = None) -> str:
        """Build prompt for HuggingFace models"""
        prompt = "You are a helpful AI assistant. Respond conversationally.\n\n"
        
        if conversation_history:
            for msg in conversation_history[-4:]:
                if msg["role"] == "user":
                    prompt += f"Human: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"
        
        prompt += f"Human: {text}\nAssistant:"
        return prompt


# Factory function to create LLM clients
def create_llm_client(model_id: str) -> BaseLLMClient:
    """
    Factory function to create an LLM client instance.
    model_id should be in format 'provider/model_name'
    """
    if model_id not in Config.AVAILABLE_MODELS.values():
        raise ValueError(f"Model '{model_id}' is not allowed. Available models: {list(Config.AVAILABLE_MODELS.values())}")
    
    try:
        provider, model_name = model_id.split('/', 1)
    except ValueError:
        raise ValueError(f"Invalid model_id format. Expected 'provider/model_name', got '{model_id}'")
    
    if provider == "openai":
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        return OpenAIClient(model=model_name, api_key=Config.OPENAI_API_KEY)
    
    elif provider == "groq":
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
        return GroqClient(model=model_name, api_key=Config.GROQ_API_KEY)
    
    elif provider == "gemini":
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")
        return GeminiClient(model=model_name, api_key=Config.GEMINI_API_KEY)
    
    elif provider == "ollama":
        return OllamaClient(model=model_name, base_url=Config.OLLAMA_BASE_URL)
    
    elif provider == "cohere":
        if not Config.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY is not set in environment variables")
        return CohereClient(model=model_name, api_key=Config.COHERE_API_KEY)
    
    elif provider == "huggingface":
        if not Config.HUGGINGFACE_API_KEY:
            raise ValueError("HUGGINGFACE_API_KEY is not set in environment variables")
        return HuggingFaceClient(model=model_name, api_key=Config.HUGGINGFACE_API_KEY)
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


# Legacy compatibility function
def create_llm_client_legacy() -> BaseLLMClient:
    """Create LLM client using legacy Config.LLM_PROVIDER setting"""
    provider = Config.LLM_PROVIDER.lower()
    
    if provider == "openai":
        return create_llm_client(f"openai/{Config.OPENAI_MODEL}")
    elif provider == "groq":
        return create_llm_client(f"groq/{Config.GROQ_MODEL}")
    elif provider == "gemini":
        return create_llm_client(f"gemini/{Config.GEMINI_MODEL}")
    elif provider == "ollama":
        return create_llm_client(f"ollama/{Config.OLLAMA_MODEL}")
    elif provider == "cohere":
        return create_llm_client(f"cohere/{Config.COHERE_MODEL}")
    elif provider == "huggingface":
        return create_llm_client(f"huggingface/{Config.HUGGINGFACE_MODEL}")
    else:
        # Default to Groq if provider is unknown
        return create_llm_client(Config.DEFAULT_MODEL_ID)