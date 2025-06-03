import asyncio
import json
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from llm_client import create_llm_client
from audio_handler import AudioHandler

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.llm_client = create_llm_client()
        self.conversation_histories: Dict[WebSocket, List[Dict[str, str]]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.conversation_histories[websocket] = []
        print(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.conversation_histories:
            del self.conversation_histories[websocket]
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast(self, message: dict):
        """Send message to all connections"""
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error broadcasting message: {e}")
    
    async def handle_transcription(self, websocket: WebSocket, transcribed_text: str):
        """Handle transcribed audio and get LLM response"""
        try:
            # Send transcription to client
            await self.send_personal_message({
                "type": "transcription",
                "content": transcribed_text,
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)
            
            # Add to conversation history
            conversation_history = self.conversation_histories.get(websocket, [])
            conversation_history.append({"role": "user", "content": transcribed_text})
            
            # Send "thinking" status
            await self.send_personal_message({
                "type": "status",
                "content": "thinking",
                "message": "AI is thinking..."
            }, websocket)
            
            # Get LLM response (streaming)
            response_content = ""
            async for chunk in self.llm_client.get_streaming_response(
                transcribed_text, 
                conversation_history
            ):
                response_content += chunk
                await self.send_personal_message({
                    "type": "response_chunk",
                    "content": chunk,
                    "full_content": response_content,
                    "timestamp": asyncio.get_event_loop().time()
                }, websocket)
            
            # Add assistant response to conversation history
            conversation_history.append({"role": "assistant", "content": response_content})
            self.conversation_histories[websocket] = conversation_history
            
            # Send completion status
            await self.send_personal_message({
                "type": "response_complete",
                "content": response_content,
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)
            
        except Exception as e:
            print(f"Error handling transcription: {e}")
            await self.send_personal_message({
                "type": "error",
                "content": f"Error processing request: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)
    
    async def handle_message(self, websocket: WebSocket, data: dict):
        """Handle incoming WebSocket messages"""
        message_type = data.get("type")
        
        if message_type == "start_listening":
            await self.start_audio_listening(websocket)
        elif message_type == "stop_listening":
            await self.stop_audio_listening(websocket)
        elif message_type == "text_input":
            # Handle direct text input (for testing or manual input)
            text = data.get("content", "")
            if text.strip():
                await self.handle_transcription(websocket, text)
        elif message_type == "clear_history":
            self.conversation_histories[websocket] = []
            await self.send_personal_message({
                "type": "history_cleared",
                "message": "Conversation history cleared"
            }, websocket)
    
    async def start_audio_listening(self, websocket: WebSocket):
        """Start audio listening for specific client"""
        # This would be implemented per-client if needed
        # For now, we'll handle audio globally in the main server
        await self.send_personal_message({
            "type": "listening_started",
            "message": "Audio listening started"
        }, websocket)
    
    async def stop_audio_listening(self, websocket: WebSocket):
        """Stop audio listening for specific client"""
        await self.send_personal_message({
            "type": "listening_stopped",
            "message": "Audio listening stopped"
        }, websocket)

# Global connection manager instance
manager = ConnectionManager()