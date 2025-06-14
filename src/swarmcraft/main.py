from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from swarmcraft.api.routes import router
from swarmcraft.api.websocket import websocket_manager, handle_websocket_message

load_dotenv()

app = FastAPI(
    title="SwarmCraft API",
    description="Interactive swarm intelligence for experiential learning",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # Svelte dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.websocket("/ws/{session_id}/{participant_id}")
async def websocket_endpoint(
    websocket: WebSocket, session_id: str, participant_id: str
):
    await websocket_manager.connect(websocket, session_id, participant_id)
    await handle_websocket_message(websocket, session_id, participant_id)
