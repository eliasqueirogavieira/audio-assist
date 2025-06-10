import asyncio
import json
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from llm_client import create_llm_client, create_llm_client_legacy
from audio_handler import AudioHandler
from config import Config

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.conversation_histories: Dict[WebSocket, List[Dict[str, str]]] = {}
        self.connection_audio_handlers: Dict[WebSocket, AudioHandler] = {}
        # Per-connection LLM clients and configurations
        self.connection_llm_clients: Dict[WebSocket, Any] = {}
        self.connection_model_configs: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.conversation_histories[websocket] = []
        
        # Initialize default LLM client for this connection
        try:
            default_llm_client = create_llm_client(Config.DEFAULT_MODEL_ID)
            self.connection_llm_clients[websocket] = default_llm_client
            self.connection_model_configs[websocket] = Config.get_model_config(Config.DEFAULT_MODEL_ID)
            print(f"Client connected with default model: {Config.DEFAULT_MODEL_ID}. Total connections: {len(self.active_connections)}")
            
            # Send available models to client
            await self.send_personal_message({
                "type": "available_models",
                "models": Config.AVAILABLE_MODELS,
                "current_model": Config.DEFAULT_MODEL_ID
            }, websocket)
            
        except Exception as e:
            print(f"Error initializing LLM client for connection: {e}")
            # Fall back to legacy client
            self.connection_llm_clients[websocket] = create_llm_client_legacy()
            self.connection_model_configs[websocket] = Config.get_model_config(Config.DEFAULT_MODEL_ID)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.conversation_histories:
            del self.conversation_histories[websocket]
        if websocket in self.connection_audio_handlers:
            del self.connection_audio_handlers[websocket]
        # Clean up per-connection LLM client data
        if websocket in self.connection_llm_clients:
            del self.connection_llm_clients[websocket]
        if websocket in self.connection_model_configs:
            del self.connection_model_configs[websocket]
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
            
            # Get LLM response (streaming) using per-connection client
            response_content = ""
            llm_client = self.connection_llm_clients.get(websocket)
            if not llm_client:
                # Fallback if no client is set for this connection
                llm_client = create_llm_client_legacy()
                self.connection_llm_clients[websocket] = llm_client
            
            async for chunk in llm_client.get_streaming_response(
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
        elif message_type == "set_language":
            await self.handle_language_change(websocket, data)
        elif message_type == "set_model":
            await self.handle_model_change(websocket, data)
    
    async def handle_language_change(self, websocket: WebSocket, data: dict):
        """Handle language change request"""
        try:
            from main import audio_handler as global_audio_handler
            language = data.get("language")
            
            if global_audio_handler:
                success = global_audio_handler.set_language(language)
                if success:
                    await self.send_personal_message({
                        "type": "language_changed",
                        "content": f"{language}",
                        "message": f"Language changed to {language}"
                    }, websocket)
                else:
                    await self.send_personal_message({
                        "type": "error",
                        "content": f"Unsupported language: {language}",
                        "timestamp": asyncio.get_event_loop().time()
                    }, websocket)
            else:
                await self.send_personal_message({
                    "type": "error",
                    "content": "Audio handler not available",
                    "timestamp": asyncio.get_event_loop().time()
                }, websocket)
        except Exception as e:
            print(f"Error handling language change: {e}")
            await self.send_personal_message({
                "type": "error",
                "content": f"Error changing language: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
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
    
    async def handle_model_change(self, websocket: WebSocket, data: dict):
        """Handle model switching request with security validation"""
        try:
            new_model_id = data.get("model")
            
            # 1. SERVER-SIDE VALIDATION (CRITICAL FOR SECURITY)
            if not new_model_id or new_model_id not in Config.AVAILABLE_MODELS.values():
                await self.send_personal_message({
                    "type": "error",
                    "content": f"Invalid or disallowed model: {new_model_id}",
                    "timestamp": asyncio.get_event_loop().time()
                }, websocket)
                return
            
            # 2. Rate limiting check (prevent rapid switching)
            # Note: This is a basic implementation. For production, consider using Redis
            current_time = asyncio.get_event_loop().time()
            last_switch_time = getattr(websocket, '_last_model_switch', 0)
            if current_time - last_switch_time < 2.0:  # 2 second cooldown
                await self.send_personal_message({
                    "type": "error", 
                    "content": "Model switching too frequently. Please wait a moment.",
                    "timestamp": current_time
                }, websocket)
                return
            
            websocket._last_model_switch = current_time
            
            # 3. Use the factory to create the new client
            new_llm_client = create_llm_client(new_model_id)
            old_model_id = getattr(self.connection_llm_clients.get(websocket), 'model', 'unknown')
            
            # 4. Update connection state
            self.connection_llm_clients[websocket] = new_llm_client
            new_config = Config.get_model_config(new_model_id)
            self.connection_model_configs[websocket] = new_config
            
            # 4.5. Update global audio handler with new model config for real-time processing
            try:
                from main import audio_handler as global_audio_handler
                if global_audio_handler:
                    global_audio_handler.update_realtime_config(new_config)
            except Exception as e:
                print(f"Warning: Could not update audio handler config: {e}")
            
            # 5. Send confirmation to the client
            await self.send_personal_message({
                "type": "model_changed",
                "status": "success",
                "old_model": old_model_id,
                "new_model": new_model_id,
                "config": Config.get_model_config(new_model_id),
                "message": f"Model switched from {old_model_id} to {new_model_id}",
                "timestamp": current_time
            }, websocket)
            
            print(f"Client switched model from {old_model_id} to {new_model_id}")
            
        except ValueError as e:
            # This will catch missing API keys or other validation errors from the factory
            await self.send_personal_message({
                "type": "error",
                "content": f"Model switch failed: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)
        except Exception as e:
            print(f"Error handling model change: {e}")
            await self.send_personal_message({
                "type": "error",
                "content": f"Error switching model: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)

# Global connection manager instance
manager = ConnectionManager()