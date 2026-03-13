
import os
from dotenv import load_dotenv
import datetime
import json
from pydantic import BaseModel, Field
from pathlib import Path
from coolname import generate_slug

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from google.adk import events, tools, Runner, sessions
from google.adk.sessions import Session, InMemorySessionService
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

load_dotenv(Path(__file__).parent / "agent_1" / ".env")

from agent_1 import agent

app = FastAPI()

APP_NAME = "Chat Agent"
CLIENT_URL = os.getenv("CLIENT_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", CLIENT_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

random_name = generate_slug(2)

session_service = InMemorySessionService()
runner = Runner(
    agent=agent.root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

user_id = "user1"
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=user_id,
    session_id=random_name
)   

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

class Message(BaseModel):
    role: str
    content: str
    timestamp: float = Field(default_factory=lambda: datetime.datetime.now().timestamp())

@app.get("/")
async def root() -> FileResponse:
    """Serve the index.html page."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")

@app.websocket("/samuel_secret_socket")
async def websocket_endpoint(websocket: WebSocket) -> None:
    print(f"Websocket connection requested.")
    print(f"Websocket headers: {websocket.headers}")
    
    await manager.connect(websocket)

    print(f"Initial state: {session.state}")

    try:
        while True:
            data = await websocket.receive_text()
            message_dict = json.loads(data)
            user_message = Message(**message_dict)
            print(f"User: {user_message.content}")
            user_message = Content(parts=[Part(text=user_message.content)])
            for event in runner.run(
                new_message=user_message,
                user_id=user_id,
                session_id=random_name,
            ):
                if event.is_final_response() == True:
                    print("Agent:", event.content.parts[0].text)
                    response_message = Message(role='assistant', content=event.content.parts[0].text)

                    await manager.send_personal_message(response_message.json(), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)   
        await manager.broadcast(f"Client disconnected.")