from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
from tools.system_tools import swarm_tools
import json

class ResourceAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LOCAL_MODEL, 
            base_url=OLLAMA_BASE_URL, 
            api_key=OPENAI_API_KEY, 
            temperature=0.1 # Very low for logical allocation
        )
        self.agent_executor = create_react_agent(self.llm, swarm_tools)
        
        # You can eventually fetch this from a database
        self.facility_inventory = {
            "Main Exhibition Hall": {"capacity": 1000, "av_ready": True, "type": "Stage"},
            "Workshop Room A": {"capacity": 150, "av_ready": True, "type": "Classroom"},
            "Workshop Room B": {"capacity": 100, "av_ready": False, "type": "Classroom"},
            "Networking Lounge": {"capacity": 300, "av_ready": False, "type": "Open Area"}
        }

    async def allocate(self, event_data, schedule, specifics):
        crowd = event_data.get("expected_crowd", 500)
        
        prompt = f"""
        You are the Head of Operations and Venue Management.
        
        FACILITY INVENTORY:
        {json.dumps(self.facility_inventory, indent=2)}
        
        EVENT SCHEDULE:
        {json.dumps(schedule, indent=2)}
        
        SPECIFIC TASK: {specifics}
        
        PROTOCOL:
        Analyze every session in the schedule. Map each session to the most logical room from the facility inventory.
        - Keynotes require large capacities and AV.
        - Breaks/Networking should be in the Lounge or Hall.
        - Standard sessions should go to Workshop rooms if capacity allows.
        Assume baseline attendance for general sessions is the full crowd ({crowd}), while specialized tracks split the crowd.
        
        Respond ONLY in valid JSON format:
        {{
            "resource_allocations": [
                {{"session": "Opening Brief", "assigned_room": "Main Exhibition Hall", "reason": "Requires AV and fits full crowd."}}
            ]
        }}
        """
        try:
            print("[*] ResourceAgent: Analyzing schedule to allocate physical spaces...")
            response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            clean_json = response["messages"][-1].content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Resource Agent Error: {e}")
            return {"resource_allocations": [{"error": "Failed to map resources."}]}