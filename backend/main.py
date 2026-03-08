from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.orchestrator import EventOrchestrator
from realtime.websocket_stream import swarm_streamer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon demo purposes
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = EventOrchestrator()

@app.websocket("/ws/swarm")
async def websocket_endpoint(websocket: WebSocket):
    await swarm_streamer.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        swarm_streamer.disconnect(websocket)

@app.post("/plan_event")
async def create_event(event_data: dict):
    # Pass the streamer to the orchestrator so it can emit live events
    result = await orchestrator.plan_event(event_data, swarm_streamer) 
    return result