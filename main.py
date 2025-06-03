import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import threading
import signal
import sys

from config import Config
from audio_handler import AudioHandler
from websocket_manager import manager
from web_ui import get_html_content

# Initialize FastAPI app
app = FastAPI(title=Config.UI_TITLE)

# Global audio handler
audio_handler = None


@app.on_event("startup")
async def startup_event():
    """Initialize audio handler on startup"""
    global audio_handler
    print("Starting Real-Time AI Audio Assistant...")
    print(f"Using LLM Provider: {Config.LLM_PROVIDER}")

    # Initialize audio handler with callback
    def on_transcription(text: str):
        """Callback for when audio is transcribed"""
        # Send transcription to all connected clients
        asyncio.create_task(broadcast_transcription(text))

    try:
        audio_handler = AudioHandler(on_transcription)
        print("Audio handler initialized successfully")
    except Exception as e:
        print(f"Failed to initialize audio handler: {e}")
        print("Audio features will be disabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global audio_handler
    if audio_handler:
        audio_handler.stop_listening()
    print("Application shutdown complete")


async def broadcast_transcription(text: str):
    """Broadcast transcription to all connected WebSocket clients"""
    for connection in manager.active_connections:
        try:
            await manager.handle_transcription(connection, text)
        except Exception as e:
            print(f"Error broadcasting transcription: {e}")


@app.get("/", response_class=HTMLResponse)
async def get_ui():
    """Serve the main UI"""
    return HTMLResponse(content=get_html_content())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle the message
            await manager.handle_message(websocket, message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.get("/start-audio")
async def start_audio():
    """Start audio listening"""
    global audio_handler
    if audio_handler:
        audio_handler.start_listening()
        return {"status": "started", "message": "Audio listening started"}
    return {"status": "error", "message": "Audio handler not available"}


@app.get("/stop-audio")
async def stop_audio():
    """Stop audio listening"""
    global audio_handler
    if audio_handler:
        audio_handler.stop_listening()
        return {"status": "stopped", "message": "Audio listening stopped"}
    return {"status": "error", "message": "Audio handler not available"}


@app.get("/status")
async def get_status():
    """Get application status"""
    return {
        "status": "running",
        "llm_provider": Config.LLM_PROVIDER,
        "active_connections": len(manager.active_connections),
        "audio_available": audio_handler is not None,
        "audio_listening": audio_handler.is_listening if audio_handler else False
    }


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\nShutting down gracefully...")
    global audio_handler
    if audio_handler:
        audio_handler.stop_listening()
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"Starting server on {Config.HOST}:{Config.PORT}")
    print("Make sure to set your API keys in the .env file!")
    print("Press Ctrl+C to stop the server")

    # Start the server
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=False,  # Disable reload in production
        log_level="info"
    )


if __name__ == "__main__":
    main()