from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
import json
from config import get_resilient_llm

class VolunteerAgent:
    def __init__(self):
        self.llm = get_resilient_llm(temperature=0.3)

    # ADDED 'specifics' parameter
    async def assign_shifts(self, event_data, schedule, specifics):
        crowd = event_data.get("expected_crowd", 500)
        
        prompt = f"""
        You are the Volunteer Coordinator for an event of {crowd} people.
        Here is the locked mathematical schedule:
        {json.dumps(schedule, indent=2)}
        
        SPECIFIC TASK: {specifics}
        
        Analyze the schedule. Some sessions (like Lunch or Registration) require massive crowd control. Other sessions (like Keynotes) require AV support.
        
        Assign specific volunteer shifts and roles tailored EXACTLY to the timeline above.
        
        Respond ONLY in valid JSON format:
        {{
            "total_volunteers_required": 45,
            "roles": [
                {{"role_name": "Registration Desk", "headcount": 10, "active_time": "8:00 AM - 10:00 AM", "reason": "High traffic at start"}}
            ]
        }}
        """
        response = await self.llm.ainvoke(prompt)
        try:
            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except:
            return {"total_volunteers_required": crowd // 20, "roles": ["General Support"]}