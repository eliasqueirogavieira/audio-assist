import openai
import asyncio
from typing import Optional, AsyncGenerator
from config import Config
import json

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
        elif self.provider == "gemini":
            if not Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            # For Gemini, you'd use google-generativeai library
            # This is a placeholder - you'd need to implement Gemini integration
            raise NotImplementedError("Gemini integration not implemented yet")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def get_response(self, text: str, conversation_history: list = None) -> str:
        """Get response from LLM"""
        try:
            if self.provider == "openai":
                return await self._get_openai_response(text, conversation_history)
            elif self.provider == "gemini":
                return await self._get_gemini_response(text, conversation_history)
        except Exception as e:
            print(f"LLM API error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def get_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Get streaming response from LLM"""
        try:
            if self.provider == "openai":
                async for chunk in self._get_openai_streaming_response(text, conversation_history):
                    yield chunk
            elif self.provider == "gemini":
                async for chunk in self._get_gemini_streaming_response(text, conversation_history):
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
    
    async def _get_openai_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Get streaming response from OpenAI API"""
        messages = self._build_messages(text, conversation_history)
        
        stream = await self.client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _build_messages(self, text: str, conversation_history: list = None) -> list:
        """Build message array for API call"""
        messages = [
            {
                "role": "system", 
                "content": "You are a helpful AI assistant. Respond conversationally to what the user says. Keep responses concise but helpful."
            }
        ]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Keep last 10 messages
        
        # Add current user message
        messages.append({"role": "user", "content": text})
        
        return messages
    
    async def _get_gemini_response(self, text: str, conversation_history: list = None) -> str:
        """Placeholder for Gemini API integration"""
        # You would implement Gemini API calls here
        # Example using google-generativeai:
        # import google.generativeai as genai
        # genai.configure(api_key=Config.GEMINI_API_KEY)
        # model = genai.GenerativeModel('gemini-pro')
        # response = model.generate_content(text)
        # return response.text
        raise NotImplementedError("Gemini integration not implemented")
    
    async def _get_gemini_streaming_response(self, text: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """Placeholder for Gemini streaming response"""
        raise NotImplementedError("Gemini streaming not implemented")

# Factory function to create LLM client
def create_llm_client() -> LLMClient:
    """Create and return configured LLM client"""
    return LLMClient()