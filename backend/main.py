from dotenv import load_dotenv
load_dotenv()

import os
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.types import Command

from orchestrator.orchestrator import EventOrchestrator
from realtime.websocket_stream import swarm_streamer

# --- PRE-FLIGHT DIAGNOSTICS ---
from memory.redis_memory import store_state, get_state
from memory.vector_store import store_memory, search_memory
from langchain_openai import ChatOpenAI
from config import LOCAL_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY


# ===============================
# Models
# ===============================

class ForkRequest(BaseModel):
    thread_id: str
    new_prompt: str


# ===============================
# Diagnostics
# ===============================

def run_diagnostics():
    print("\n" + "⚙️ " * 20)
    print("RUNNING PRE-FLIGHT SYSTEM CHECKS...")

    # Redis Test
    try:
        store_state("diagnostic_test", "system_online")
        result = get_state("diagnostic_test")

        if result:
            print("✅ REDIS MEMORY: ONLINE")
        else:
            print("⚠️ REDIS MEMORY: OFFLINE")

    except Exception as e:
        print(f"❌ REDIS ERROR: {e}")

    # Vector store
    try:
        store_memory("Diagnostic event memory.")
        search_result = search_memory("Diagnostic")

        if search_result and "documents" in search_result:
            print("✅ VECTOR STORE: ONLINE")
        else:
            print("❌ VECTOR STORE FAILED")

    except Exception as e:
        print(f"❌ VECTOR STORE ERROR: {e}")

    # LLM wakeup
    try:
        llm = ChatOpenAI(
            model=LOCAL_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            max_tokens=10,
            temperature=0
        )

        print(f"[*] Waking model {LOCAL_MODEL}...")

        response = llm.invoke("Respond with exactly one word: Ready")

        if response and response.content:
            print(f"✅ MODEL READY: {response.content.strip()}")

    except Exception as e:
        print(f"❌ MODEL ERROR: {e}")

    print("⚙️ " * 20 + "\n")


run_diagnostics()

# ===============================
# FastAPI Setup
# ===============================

app = FastAPI(title="EventOS DeepMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = EventOrchestrator()


# ===============================
# Helper for LangGraph resume
# ===============================

async def resume_graph(thread_id: str, payload: dict):
    return await orchestrator.graph.ainvoke(
        Command(resume=payload),
        config={"configurable": {"thread_id": thread_id}}
    )


# ===============================
# WebSocket (Live Swarm Stream)
# ===============================

@app.websocket("/ws/swarm")
async def websocket_endpoint(websocket: WebSocket):

    await swarm_streamer.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        swarm_streamer.disconnect(websocket)


# ===============================
# Event Planning
# ===============================

@app.post("/plan_event")
async def plan_event(event_data: dict):

    result = await orchestrator.plan_event(event_data, swarm_streamer)

    return result


@app.post("/approve_plan")
async def approve_plan(event_data: dict):

    thread_id = event_data.get("thread_id")

    payload = {"action": "approve"}

    return await resume_graph(thread_id, payload)


# ===============================
# Crisis Simulation
# ===============================

@app.post("/simulate_crisis")
async def crisis(data: dict):

    result = await orchestrator.handle_crisis(data, swarm_streamer)

    return result


# ===============================
# Status
# ===============================

@app.get("/status")
def status():

    return {"system": "EventOS DeepMind Swarm running"}


# ===============================
# Manual Override
# ===============================

@app.post("/manual_override")
async def manual_override(data: dict):

    thread_id = data.get("thread_id")

    payload = {
        "action": "direct_edit",
        "schedule": data.get("new_schedule"),
        "agent_outputs": data.get("agent_outputs")
    }

    return await resume_graph(thread_id, payload)


# ===============================
# Resume Crashed Event
# ===============================

@app.post("/resume_event")
async def resume_crashed_event():

    try:

        result = await orchestrator.resume_event(swarm_streamer)

        return result

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ===============================
# Thread History
# ===============================

@app.get("/history")
async def get_history():

    threads = orchestrator.get_thread_history()

    return {"threads": threads}


# ===============================
# Fork Event
# ===============================

@app.post("/fork_event")
async def fork_event(req: ForkRequest):

    payload = {
        "action": "replan_all",
        "message": req.new_prompt
    }

    return await resume_graph(req.thread_id, payload)


# ===============================
# Get Thread State
# ===============================

@app.get("/thread/{thread_id}")
async def get_thread_state(thread_id: str):

    try:

        config = {"configurable": {"thread_id": thread_id}}

        state = orchestrator.graph.get_state(config)

        if not state.values:
            raise HTTPException(status_code=404, detail="Thread not found")

        is_waiting = len(state.next) > 0

        return {
            "schedule": state.values.get("schedule", []),
            "agent_outputs": state.values.get("agent_outputs", {}),
            "audit_log": state.values.get("audit_log", []),
            "requires_approval": is_waiting,
            "status": "AWAITING_APPROVAL" if is_waiting else "COMPLETED"
        }

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# ===============================
# API History
# ===============================

@app.get("/api/history/{thread_id}")
async def get_history(thread_id: str):

    return orchestrator.get_event_details(thread_id)


# ===============================
# Prompt Edit
# ===============================

@app.post("/api/edit/prompt")
async def edit_via_prompt(request: Request):

    data = await request.json()

    thread_id = data["thread_id"]

    prompt = data["prompt_text"]

    payload = {
        "action": "prompt",
        "message": prompt
    }

    return await resume_graph(thread_id, payload)


# ===============================
# Manual Edit
# ===============================

@app.post("/api/edit/manual")
async def edit_manual(request: Request):

    data = await request.json()

    thread_id = data["thread_id"]

    payload = {
        "action": "direct_edit",
        "schedule": data.get("schedule"),
        "agent_outputs": data.get("agent_outputs")
    }

    return await resume_graph(thread_id, payload)


# ===============================
# Smart Chat
# ===============================

@app.post("/api/chat")
async def handle_smart_chat(request: Request):

    data = await request.json()

    thread_id = data.get("thread_id")

    prompt = data.get("prompt_text")

    payload = {
        "action": "prompt",
        "message": prompt
    }

    result = await resume_graph(thread_id, payload)

    return {
        "schedule": result.get("schedule"),
        "agent_outputs": result.get("agent_outputs"),
        "audit_log": result.get("audit_log", [])
    }


# ===============================
# Approve Event
# ===============================

@app.post("/api/approve")
async def approve_event(request: Request):

    data = await request.json()

    thread_id = data.get("thread_id")

    payload = {"action": "approve"}

    return await resume_graph(thread_id, payload)