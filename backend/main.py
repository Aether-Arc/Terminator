from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.orchestrator import EventOrchestrator
from realtime.websocket_stream import swarm_streamer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = EventOrchestrator()

@app.websocket("/ws/swarm")
async def websocket_endpoint(websocket: WebSocket):
    await swarm_streamer.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        swarm_streamer.disconnect(websocket)

@app.post("/plan_event")
async def plan_event(event_data: dict): # Accept raw dict from frontend
    # Pass the streamer so nodes light up in real-time
    result = await orchestrator.plan_event(event_data, swarm_streamer)
    return result

@app.post("/simulate_crisis")
async def crisis(data: dict):
    result = await orchestrator.handle_crisis(data, swarm_streamer)
    return result

@app.get("/status")
def status():
    return {"system": "EventOS DeepMind Swarm running"}