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

# 🚀 IMPORT TOOLS FOR WEB SEARCH TEST
from tools.system_tools import swarm_tools
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
    llm = None
    try:
        llm = ChatOpenAI(
            model=LOCAL_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            max_tokens=100, # Increased slightly to allow a real answer
            temperature=0
        )
        print(f"[*] Waking model {LOCAL_MODEL}...")
        response = llm.invoke("Respond with exactly one word: Ready")
        if response and response.content:
            print(f"✅ MODEL READY: {response.content.strip()}")
    except Exception as e:
        print(f"❌ MODEL ERROR: {e}")

    # 🚀 NEW: WEB SEARCH PRE-FLIGHT TEST
    if llm:
        try:
            print("[*] Testing Web Search Engine...")
            # Create a temporary diagnostic agent equipped with your tools
            test_agent = create_react_agent(llm, swarm_tools)
            
            # Force it to look up something realtime that isn't in its training data
            search_query = "What is the current time and weather in Tokyo right now? You MUST use the web_search tool to answer."
            
            search_response = test_agent.invoke({"messages": [("user", search_query)]})
            
            # Verify if the tool was actually invoked in the message history
            messages = search_response.get("messages", [])
            tool_was_called = any(msg.type == "tool" for msg in messages)
            
            if tool_was_called:
                print(f"✅ WEB SEARCH: ONLINE & Tool Execution Successful")
                print(f"   [Search Result]: '{messages[-1].content.strip()}'")
            else:
                print("⚠️ WEB SEARCH: LLM replied, but did NOT trigger the search tool. It might be hallucinating.")
                
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
# Helper for LangGraph resume
# ===============================
async def resume_graph(thread_id: str, payload: dict):
    # Safety check: Verify state exists and can be resumed
    config = {"configurable": {"thread_id": thread_id}}
    state = orchestrator.graph.get_state(config)
    if not state.next:
        raise HTTPException(status_code=400, detail="Graph is not currently paused for human review.")
        
    return await orchestrator.graph.ainvoke(
        Command(resume=payload),
        config=config
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
# Thread History
# ===============================
@app.get("/history")
async def get_history():
    threads = orchestrator.get_thread_history()
    return {"threads": threads}

@app.get("/api/history/{thread_id}")
async def get_api_history(thread_id: str):
    return orchestrator.get_event_details(thread_id)

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
            "agent_outputs": state.values.get("agent_outputs") or {"marketing": [{"task": "Archived", "output": state.values.get("marketing_copy", "")}]},
            "audit_log": state.values.get("audit_log", []),
            "requires_approval": is_waiting,
            "status": "AWAITING_APPROVAL" if is_waiting else "COMPLETED"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
# 🚀 SMART CHAT (The Brain Router)
# ===============================
@app.post("/api/chat")
async def handle_smart_chat(request: Request):
    """
    Handles chat commands, UI direct edits, and physical dispatches
    by routing them through the Orchestrator's Smart Brain.
    """
    data = await request.json()
    thread_id = data.get("thread_id")
    
    # 🚀 FIXED: We extract the 'payload' object passed by React
    payload = data.get("payload", {})
    
    if not thread_id:
        raise HTTPException(status_code=400, detail="Missing thread_id")

    try:
        # Route the request through the Orchestrator
        if payload.get("action") == "prompt":
            # If it's a typed instruction, let the LLM brain decide what to do!
            result = await orchestrator.route_user_intent(
                thread_id, 
                payload.get("message"), 
                swarm_streamer
            )
        else:
            # If it's a direct manual edit from the UI or an approval
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
# Get Master Ledger
# ===============================
@app.get("/api/ledger/{thread_id}")
async def get_master_ledger(thread_id: str):
    """Returns the entire centralized event state for the UI directly from LangGraph Memory."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = orchestrator.graph.get_state(config)
        
        if not state.values:
            return {"error": "Ledger not found", "is_empty": True}
            
        return {
            "thread_id": thread_id,
            "event_data": state.values.get("event_data", {}),
            "schedule": state.values.get("schedule", []),
            "agent_outputs": state.values.get("agent_outputs", {}),
            "audit_log": state.values.get("audit_log", []),
            "is_empty": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read LangGraph ledger: {e}")