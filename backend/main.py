from fastapi import FastAPI
from orchestrator.orchestrator import EventOrchestrator
from models.event_model import EventInput

app = FastAPI()

orchestrator = EventOrchestrator()


@app.post("/plan_event")
async def plan_event(event: EventInput):
    return await orchestrator.plan_event(event)


@app.post("/simulate_crisis")
async def crisis(data: dict):
    return await orchestrator.handle_crisis(data)


@app.get("/status")
def status():
    return {"system": "EventOS running"}