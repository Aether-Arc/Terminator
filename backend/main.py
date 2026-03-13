from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.orchestrator import EventOrchestrator
from realtime.websocket_stream import swarm_streamer

# --- PRE-FLIGHT DIAGNOSTICS ---
from memory.redis_memory import store_state, get_state
from memory.vector_store import store_memory, search_memory
from langchain_openai import ChatOpenAI
from config import LOCAL_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY
from pydantic import BaseModel

class ForkRequest(BaseModel):
    thread_id: str
    new_prompt: str

def run_diagnostics():
    print("\n" + "⚙️ "*20)
    print("RUNNING PRE-FLIGHT SYSTEM CHECKS...")
    
    # 1. Test Redis
    try:
        store_state("diagnostic_test", "system_online")
        result = get_state("diagnostic_test")
        if result:
            print("✅ REDIS MEMORY:   ONLINE & Read/Write Confirmed")
        else:
            print("⚠️ REDIS MEMORY:   OFFLINE (Agents will use ephemeral local fallback)")
    except Exception as e:
        print(f"❌ REDIS ERROR:    {e}")

    # 2. Test Vector Store
    try:
        store_memory("Diagnostic test event memory initialized.")
        search_result = search_memory("Diagnostic test")
        if search_result and "documents" in search_result:
            print("✅ VECTOR STORE:   ONLINE & Semantic Search Active")
        else:
            print("❌ VECTOR STORE:   FAILED TO RETURN DATA")
    except Exception as e:
        print(f"❌ VECTOR STORE ERROR: {e}")
        
    # 3. Test LLM Engine (Ollama)
    try:
        llm = ChatOpenAI(
            model=LOCAL_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            max_tokens=10, # Keep it extremely short for speed
            temperature=0
        )
        print(f"[*] Waking up {LOCAL_MODEL} (this may take a few seconds on first run)...")
        response = llm.invoke("Respond with exactly one word: 'Ready'.")
        
        if response and response.content:
            print(f"✅ AI MODEL:       ONLINE & Responding ({LOCAL_MODEL})")
            print(f"   [Model Output]: '{response.content.strip()}'")
        else:
            print("❌ AI MODEL:       FAILED TO GENERATE TEXT")
    except Exception as e:
        print(f"❌ AI MODEL ERROR: {e}")
        print("   -> Did you forget to start Ollama in your terminal? Run 'ollama serve' or check your config.")

    print("⚙️ "*20 + "\n")

# Run the test before starting the app!
run_diagnostics()
# -------------------------------------

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
async def plan_event(event_data: dict): 
    result = await orchestrator.plan_event(event_data, swarm_streamer)
    return result

@app.post("/approve_plan")
async def approve_plan(event_data: dict): 
    result = await orchestrator.approve_plan(event_data, swarm_streamer)
    return result

@app.post("/simulate_crisis")
async def crisis(data: dict):
    result = await orchestrator.handle_crisis(data, swarm_streamer)
    return result

@app.get("/status")
def status():
    return {"system": "EventOS DeepMind Swarm running"}

@app.post("/manual_override")
async def manual_override(data: dict):
    """
    Accepts payload like:
    {
        "override_type": "edit_schedule",
        "new_schedule": [{"session": "Lunch", "start": "12:00 PM", "end": "1:00 PM"}],
        "csv_content": "name,email\nTest,test@test.com"
    }
    OR
    {
        "override_type": "custom_crisis",
        "description": "The internet went down in the main hall!",
        "expected_crowd": 500,
        "csv_content": "name,email\nTest,test@test.com"
    }
    """
    result = await orchestrator.manual_override(data, swarm_streamer)
    return result

@app.post("/resume_event")
async def resume_crashed_event():
    try:
        # We reuse the global orchestrator and streamer
        result = await orchestrator.resume_event(swarm_streamer)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/history")
async def get_history():
    threads = orchestrator.get_thread_history()
    return {"threads": threads}

@app.post("/fork_event")
async def fork_event(req: ForkRequest):
    try:
        result = await orchestrator.fork_and_update(req.thread_id, req.new_prompt, swarm_streamer)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/thread/{thread_id}")
async def get_thread_state(thread_id: str):
    try:
        # 1. Point LangGraph to the specific SQLite thread
        config = {"configurable": {"thread_id": thread_id}}
        
        # 2. Fetch the frozen state from the hard drive
        state = orchestrator.graph.get_state(config)
        
        if not state.values:
            raise HTTPException(status_code=404, detail="Thread not found")
            
        # 3. Check if the graph is currently paused waiting for human approval
        is_waiting = len(state.next) > 0
        
        return {
            "schedule": state.values.get("schedule", []),
            "marketing": state.values.get("marketing_copy", ""),
            "email_logs": state.values.get("email_logs") or [],
            "requires_approval": is_waiting,
            "status": "AWAITING_APPROVAL" if is_waiting else "COMPLETED"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


# GET /api/history/{thread_id}
@app.get("/api/history/{thread_id}")
async def get_history(thread_id: str):
    return orchestrator.get_event_details(thread_id)

# POST /api/edit/prompt
@app.post("/api/edit/prompt")
async def edit_via_prompt(request: Request):
    data = await request.json()
    return await orchestrator.fork_and_update(data["thread_id"], data["prompt_text"], websocket_streamer)

# POST /api/edit/manual
@app.post("/api/edit/manual")
async def edit_manual(request: Request):
    data = await request.json()
    return await orchestrator.manual_override(data, websocket_streamer)