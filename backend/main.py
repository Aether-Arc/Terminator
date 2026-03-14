from dotenv import load_dotenv
load_dotenv()

import os
import json
import asyncio
import urllib.parse # 🚀 REQUIRED FOR URL DECODING
import uuid

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

from tools.system_tools import web_search
from langgraph.prebuilt import create_react_agent

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

    try:
        store_state("diagnostic_test", "system_online")
        result = get_state("diagnostic_test")
        if result: print("✅ REDIS MEMORY: ONLINE")
        else: print("⚠️ REDIS MEMORY: OFFLINE")
    except Exception as e:
        print(f"❌ REDIS ERROR: {e}")

    try:
        store_memory("Diagnostic event memory.")
        search_result = search_memory("Diagnostic")
        if search_result and "documents" in search_result: print("✅ VECTOR STORE: ONLINE")
        else: print("❌ VECTOR STORE FAILED")
    except Exception as e:
        print(f"❌ VECTOR STORE ERROR: {e}")

    llm = None
    try:
        llm = ChatOpenAI(
            model=LOCAL_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            max_tokens=100, 
            temperature=0
        )
        print(f"[*] Waking model {LOCAL_MODEL}...")
        response = llm.invoke("Respond with exactly one word: Ready")
        if response and response.content:
            print(f"✅ MODEL READY: {response.content.strip()}")
    except Exception as e:
        print(f"❌ MODEL ERROR: {e}")

    if llm:
        try:
            print("[*] Testing Web Search Engine...")
            search_result = asyncio.run(web_search.ainvoke({"query": "What is the capital of France?"}))
            
            if search_result and "failed" not in search_result.lower():
                print("✅ WEB SEARCH: ONLINE")
                print(f"   [Result Snippet]: '{search_result[:60]}...'")
            else:
                print("❌ WEB SEARCH FAILED")
                
        except Exception as e:
            print(f"❌ WEB SEARCH ERROR: {e}")
            print("   -> Check your API Keys (e.g., Tavily, DuckDuckGo, or Google) in your .env file.")

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
# Event Planning & Approval
# ===============================
@app.post("/plan_event")
async def plan_event(event_data: dict):
    result = await orchestrator.plan_event(event_data, swarm_streamer)
    return result

@app.post("/approve_plan")
async def approve_plan(event_data: dict):
    # 1. Decode the thread ID
    thread_id = urllib.parse.unquote(event_data.get("thread_id", ""))
    edited_plan = event_data.get("edited_plan")
    
    try:
        # 🚀 THE UPGRADE: Forcefully inject UI edits directly into LangGraph Memory!
        if edited_plan:
            config = {"configurable": {"thread_id": thread_id}}
            orchestrator.graph.update_state(config, {"schedule": edited_plan})
            print(f"[*] Successfully saved manual UI edits to thread: {thread_id}")
        
        # 2. Tell the graph to resume from its paused state
        payload = {"action": "approve"}
        return await orchestrator.resume_workflow(thread_id, payload, swarm_streamer)
        
    except Exception as e:
        print(f"[❌] Approve Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ===============================
# Fork / Time Travel
# ===============================
@app.post("/fork_event")
async def fork_event(request: ForkRequest):
    try:
        clean_thread_id = urllib.parse.unquote(request.thread_id)
        config = {"configurable": {"thread_id": clean_thread_id}}
        old_state = orchestrator.graph.get_state(config)
        
        if not old_state.values:
            print(f"[⚠️] Warning: Could not find thread '{clean_thread_id}'. Spawning a fresh event instead.")
            event_data = {"name": "Forked Event", "user_constraints": request.new_prompt}
            new_thread_id = f"Forked Event [{str(uuid.uuid4())[:4]}]"
            result = await orchestrator.plan_event(event_data, swarm_streamer, thread_id=new_thread_id)
            return result
            
        event_data = old_state.values.get("event_data", {}).copy()
        
        old_constraints = event_data.get("user_constraints", "")
        event_data["user_constraints"] = f"{old_constraints}\n[FORK UPDATE]: {request.new_prompt}"
        
        new_thread_id = f"{event_data.get('name', 'Forked Event')} [{str(uuid.uuid4())[:4]}]"
        
        result = await orchestrator.plan_event(event_data, swarm_streamer, thread_id=new_thread_id)
        return result
        
    except Exception as e:
        print(f"[❌] Fork Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
      
@app.post("/simulate_crisis")
async def crisis(data: dict):
    result = await orchestrator.handle_crisis(data, swarm_streamer)
    return result


@app.get("/status")
def status():
    return {"system": "EventOS DeepMind Swarm running"}

@app.get("/history")
async def get_history():
    threads = orchestrator.get_thread_history()
    return {"threads": threads}

@app.get("/api/history/{thread_id}")
async def get_api_history(thread_id: str):
    clean_thread_id = urllib.parse.unquote(thread_id)
    return orchestrator.get_event_details(clean_thread_id)

@app.get("/thread/{thread_id}")
async def get_thread_state(thread_id: str):
    try:
        clean_thread_id = urllib.parse.unquote(thread_id)
        config = {"configurable": {"thread_id": clean_thread_id}}
        state = orchestrator.graph.get_state(config)

        if not state.values:
            raise HTTPException(status_code=404, detail="Thread not found")

        is_waiting = len(state.next) > 0

        return {
            "schedule": state.values.get("schedule", []),
            "agent_outputs": state.values.get("agent_outputs") or {"marketing": [{"task": "Archived", "output": state.values.get("marketing_copy", "")}]},
            "audit_log": state.values.get("audit_log", []),
            "requires_approval": is_waiting,
            "status": "AWAITING_APPROVAL" if is_waiting else "COMPLETED"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ledger/{thread_id}")
async def get_master_ledger(thread_id: str):
    try:
        clean_thread_id = urllib.parse.unquote(thread_id)
        config = {"configurable": {"thread_id": clean_thread_id}}
        state = orchestrator.graph.get_state(config)
        
        if not state.values:
            return {"error": "Ledger not found", "is_empty": True}
            
        return {
            "thread_id": clean_thread_id,
            "event_data": state.values.get("event_data", {}),
            "schedule": state.values.get("schedule", []),
            "agent_outputs": state.values.get("agent_outputs", {}),
            "audit_log": state.values.get("audit_log", []),
            "is_empty": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read LangGraph ledger: {e}")


@app.post("/api/chat")
async def handle_smart_chat(request: Request):
    data = await request.json()
    raw_thread_id = data.get("thread_id")
    
    if not raw_thread_id:
        raise HTTPException(status_code=400, detail="Missing thread_id")
        
    thread_id = urllib.parse.unquote(raw_thread_id)
    payload = data.get("payload", {})

    try:
        if payload.get("action") == "prompt":
          
            result = await orchestrator.route_user_intent(
                thread_id, 
                payload, 
                swarm_streamer
            )
        else:
            result = await orchestrator.resume_workflow(thread_id, payload, swarm_streamer)
            
        return {
            "schedule": result.get("schedule"),
            "agent_outputs": result.get("agent_outputs"),
            "reply": "Intelligence Swarm applied your updates successfully."
        }
    except Exception as e:
        print(f"[❌] Orchestration Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

# ===============================
# UI Manual Edit & Approval Hooks
# ===============================
@app.post("/api/edit/manual")
async def api_edit_manual(data: dict):
    """Directly injects the user's UI edits into LangGraph memory without AI intervention."""
    try:
        thread_id = urllib.parse.unquote(data.get("thread_id", ""))
        schedule = data.get("schedule", [])
        
        config = {"configurable": {"thread_id": thread_id}}
        # Update the graph state directly
        orchestrator.graph.update_state(config, {"schedule": schedule})
        return {"status": "success", "message": "Manual edits saved to memory."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/approve")
async def api_approve(data: dict):
    """Triggers the graph to finalize the approved assets."""
    try:
        thread_id = urllib.parse.unquote(data.get("thread_id", ""))
        return await orchestrator.resume_workflow(thread_id, {"action": "approve"}, swarm_streamer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate_itinerary")
async def generate_itinerary(data: dict):
    """Bypasses the graph router and directly commands the ItineraryAgent to expand the schedule."""
    try:
        thread_id = urllib.parse.unquote(data.get("thread_id", ""))
        config = {"configurable": {"thread_id": thread_id}}
        
        # 1. Get the current memory state
        state = orchestrator.graph.get_state(config)
        event_data = state.values.get("event_data", {})
        schedule = state.values.get("schedule", [])
        agent_outputs = state.values.get("agent_outputs", {})
        
        # 2. Force the Itinerary Agent to run directly
        detailed_schedule = await orchestrator.itinerary.expand_schedule(event_data, schedule)
        
        # 3. Save the results back into the LangGraph state
        if "operations" not in agent_outputs:
            agent_outputs["operations"] = []
            
        # Clean out any old itinerary attempts
        agent_outputs["operations"] = [w for w in agent_outputs["operations"] if w.get("domain") != "itinerary"]
        
        # Append the new success
        agent_outputs["operations"].append({
            "domain": "itinerary", 
            "task": "Expand Base Schedule", 
            "output": detailed_schedule
        })
        
        orchestrator.graph.update_state(config, {"agent_outputs": agent_outputs})
        return {"status": "success"}
        
    except Exception as e:
        print(f"[❌] Itinerary Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))