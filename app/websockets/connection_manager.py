from typing import Dict, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Store session connections (user_id, session_id) -> Set[WebSocket]
        self.session_connections: Dict[tuple, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, session_id: int = None):
        """Accept a WebSocket connection."""
        await websocket.accept()

        # Add to user connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

        # Add to session connections if session_id provided
        if session_id:
            key = (user_id, session_id)
            if key not in self.session_connections:
                self.session_connections[key] = set()
            self.session_connections[key].add(websocket)

    async def disconnect(
        self, websocket: WebSocket, user_id: int, session_id: int = None
    ):
        """Remove a WebSocket connection."""
        # Remove from user connections
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove from session connections
        if session_id:
            key = (user_id, session_id)
            if key in self.session_connections:
                self.session_connections[key].discard(websocket)
                if not self.session_connections[key]:
                    del self.session_connections[key]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending message to WebSocket: {e}")

    async def send_message_to_user(self, message: str, user_id: int):
        """Send a message to all connections of a specific user."""
        if user_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    print(f"Error sending message to user {user_id}: {e}")
                    disconnected.add(websocket)

            # Remove disconnected websockets
            for ws in disconnected:
                self.active_connections[user_id].discard(ws)

    async def send_message_to_session(
        self, message: str, user_id: int, session_id: int
    ):
        """Send a message to all connections of a specific session."""
        key = (user_id, session_id)
        if key in self.session_connections:
            disconnected = set()
            for websocket in self.session_connections[key]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    print(f"Error sending message to session {session_id}: {e}")
                    disconnected.add(websocket)

            # Remove disconnected websockets
            for ws in disconnected:
                self.session_connections[key].discard(ws)

    async def broadcast_to_user_sessions(self, message: str, user_id: int):
        """Broadcast a message to all sessions of a user."""
        await self.send_message_to_user(message, user_id)

    def get_user_connection_count(self, user_id: int) -> int:
        """Get the number of active connections for a user."""
        return len(self.active_connections.get(user_id, set()))

    def get_session_connection_count(self, user_id: int, session_id: int) -> int:
        """Get the number of active connections for a session."""
        key = (user_id, session_id)
        return len(self.session_connections.get(key, set()))


manager = ConnectionManager()
