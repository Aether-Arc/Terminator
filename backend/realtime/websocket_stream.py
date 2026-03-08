from fastapi import WebSocket
from typing import List
import json

class SwarmStreamer:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, agent_name: str, action: str, status: str = "thinking"):
        message = json.dumps({
            "agent": agent_name,
            "action": action,
            "status": status
        })
        for connection in self.active_connections:
            await connection.send_text(message)

# Global instance to be used by the Orchestrator
swarm_streamer = SwarmStreamer()