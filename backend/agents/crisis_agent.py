# REMOVE THIS:
# from langchain_google_genai import ChatGoogleGenerativeAI

# ADD THIS:
from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, AI_MODEL
import json

class CrisisAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=AI_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.2 # Crucial: Keep this low so Gemma outputs strict JSON
        )

    async def resolve(self, crisis_description, current_schedule):
        prompt = f"""
        You are an emergency response AI for a national-level hackathon.
        A crisis has just been reported: "{crisis_description}"
        
        Here is the current locked schedule:
        {json.dumps(current_schedule, indent=2)}
        
        Figure out how to mathematically and logistically fix the schedule.
        Respond ONLY with valid JSON in this exact format:
        {{
            "mitigation_strategy": "Brief explanation of how you are solving this to announce to the crowd",
            "required_action": "reschedule" or "relocate" or "cancel",
            "delay_minutes": 30,
            "affected_sessions": ["Name of session 1", "Name of session 2"]
        }}
        """
        response = await self.llm.ainvoke(prompt)
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            return {
                "mitigation_strategy": "Emergency manual override required. System failure.", 
                "required_action": "manual", 
                "delay_minutes": 0,
                "affected_sessions": []
            }