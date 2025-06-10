import openai
import asyncio
import aiohttp
import json
from typing import Optional, AsyncGenerator
from config import Config


class LLMClient:
    def __init__(self):
        self.provider = Config.LLM_PROVIDER.lower()
        self._setup_client()

    def _setup_client(self):
        """Setup the appropriate LLM client"""
        if self.provider == "openai":
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

        elif self.provider == "groq":
            if not hasattr(Config, 'GROQ_API_KEY') or not Config.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            self.client = openai.AsyncOpenAI(
                api_key=Config.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )

        elif self.provider == "ollama":
            # Ollama runs locally, no API key needed
            self.base_url = getattr(Config, 'OLLAMA_BASE_URL', 'http://localhost:11434')
            self.model = getattr(Config, 'OLLAMA_MODEL', 'llama3.2:1b')

        elif self.provider == "huggingface":
            if not hasattr(Config, 'HUGGINGFACE_API_KEY') or not Config.HUGGINGFACE_API_KEY:
                raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")
            self.hf_model = getattr(Config, 'HUGGINGFACE_MODEL', 'microsoft/DialoGPT-medium')

        elif self.provider == "cohere":
            if not hasattr(Config, 'COHERE_API_KEY') or not Config.COHERE_API_KEY:
                raise ValueError("COHERE_API_KEY not found in environment variables")

        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def get_response(self, text: str, conversation_history: list = None) -> str:
        """Get response from LLM"""
        try:
            if self.provider == "openai":
                return await self._get_openai_response(text, conversation_history)
            elif self.provider == "groq":
                return await self._get_groq_response(text, conversation_history)
            elif self.provider == "ollama":
                return await self._get_ollama_response(text, conversation_history)
            elif self.provider == "huggingface":
                return await self._get_huggingface_response(text, conversation_history)
            elif self.provider == "cohere":
                return await self._get_cohere_response(text, conversation_history)
        except Exception as e:
            print(f"LLM API error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def get_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Get streaming response from LLM"""
        try:
            if self.provider in ["openai", "groq"]:
                async for chunk in self._get_openai_streaming_response(text, conversation_history):
                    yield chunk
            elif self.provider == "ollama":
                async for chunk in self._get_ollama_streaming_response(text, conversation_history):
                    yield chunk
            elif self.provider == "huggingface":
                # HuggingFace doesn't support streaming for most models
                response = await self._get_huggingface_response(text, conversation_history)
                # Simulate streaming by yielding words
                words = response.split()
                for word in words:
                    yield word + " "
                    await asyncio.sleep(0.05)  # Small delay for streaming effect
            elif self.provider == "cohere":
                async for chunk in self._get_cohere_streaming_response(text, conversation_history):
                    yield chunk
        except Exception as e:
            print(f"LLM streaming error: {e}")
            yield f"Sorry, I encountered an error: {str(e)}"

    async def _get_openai_response(self, text: str, conversation_history: list = None) -> str:
        """Get response from OpenAI API"""
        messages = self._build_messages(text, conversation_history)

        response = await self.client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )

        return response.choices[0].message.content

    async def _get_openai_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[
        str, None]:
        """Get streaming response from OpenAI API (also works for Groq)"""
        messages = self._build_messages(text, conversation_history)

        # Use different model for Groq
        model = Config.GROQ_MODEL if self.provider == "groq" else Config.OPENAI_MODEL

        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=2000,
            temperature=0.6,
            top_p=0.9,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def _get_groq_response(self, text: str, conversation_history: list = None) -> str:
        """Get response from Groq API (uses OpenAI-compatible format)"""
        return await self._get_openai_response(text, conversation_history)

    async def _get_ollama_response(self, text: str, conversation_history: list = None) -> str:
        """Get response from local Ollama instance"""
        messages = self._build_messages(text, conversation_history)

        # Convert messages to Ollama format
        prompt = self._messages_to_prompt(messages)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 500
                        }
                    }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "No response received")
                else:
                    raise Exception(f"Ollama API error: {response.status}")

    async def _get_ollama_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[
        str, None]:
        """Get streaming response from local Ollama instance"""
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
                            "num_predict": 500
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

    async def _get_huggingface_response(self, text: str, conversation_history: list = None) -> str:
        """Get response from HuggingFace Inference API"""
        # Build a conversational prompt
        prompt = self._build_hf_prompt(text, conversation_history)

        headers = {
            "Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}",
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
                    f"https://api-inference.huggingface.co/models/{self.hf_model}",
                    headers=headers,
                    json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "No response generated")
                    else:
                        return str(result)
                else:
                    error_text = await response.text()
                    raise Exception(f"HuggingFace API error: {response.status} - {error_text}")

    async def _get_cohere_response(self, text: str, conversation_history: list = None) -> str:
        """Get response from Cohere API"""
        headers = {
            "Authorization": f"Bearer {Config.COHERE_API_KEY}",
            "Content-Type": "application/json"
        }

        # Build conversation context
        chat_history = []
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages
                if msg["role"] == "user":
                    chat_history.append({"role": "USER", "message": msg["content"]})
                elif msg["role"] == "assistant":
                    chat_history.append({"role": "CHATBOT", "message": msg["content"]})

        payload = {
            "message": text,
            "model": getattr(Config, 'COHERE_MODEL', 'command-light'),
            "chat_history": chat_history,
            "temperature": 0.7,
            "max_tokens": 500
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "https://api.cohere.ai/v1/chat",
                    headers=headers,
                    json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("text", "No response received")
                else:
                    error_text = await response.text()
                    raise Exception(f"Cohere API error: {response.status} - {error_text}")

    async def _get_cohere_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[
        str, None]:
        """Get streaming response from Cohere API"""
        headers = {
            "Authorization": f"Bearer {Config.COHERE_API_KEY}",
            "Content-Type": "application/json"
        }

        chat_history = []
        if conversation_history:
            for msg in conversation_history[-6:]:
                if msg["role"] == "user":
                    chat_history.append({"role": "USER", "message": msg["content"]})
                elif msg["role"] == "assistant":
                    chat_history.append({"role": "CHATBOT", "message": msg["content"]})

        payload = {
            "message": text,
            "model": getattr(Config, 'COHERE_MODEL', 'command-light'),
            "chat_history": chat_history,
            "temperature": 0.7,
            "max_tokens": 500,
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

    def _messages_to_prompt(self, messages: list) -> str:
        """Convert messages to a single prompt for models that don't support chat format"""
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

    def _build_hf_prompt(self, text: str, conversation_history: list = None) -> str:
        """Build prompt for HuggingFace models"""
        prompt = "You are a helpful AI assistant. Respond conversationally.\n\n"

        if conversation_history:
            for msg in conversation_history[-4:]:  # Last 4 messages
                if msg["role"] == "user":
                    prompt += f"Human: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"

        prompt += f"Human: {text}\nAssistant:"
        return prompt


def create_llm_client() -> LLMClient:
    """Create and return configured LLM client"""
    return LLMClient()