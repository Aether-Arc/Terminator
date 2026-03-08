from fastapi import WebSocket
from typing import List
import json
import logging

class SwarmStreamer:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        # Safely remove to prevent ValueError if it was already removed
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, agent_name: str, action: str, status: str = "thinking"):
        message = json.dumps({
            "agent": agent_name,
            "action": action,
            "status": status
        })
        
        dead_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                # If sending fails (e.g., client disconnected abruptly), mark for removal
                dead_connections.append(connection)
                
        # Cleanup dead connections after the loop to avoid modifying the list while iterating
        for dead_conn in dead_connections:
            self.disconnect(dead_conn)

# Global instance to be used by the Orchestrator
swarm_streamer = SwarmStreamer()