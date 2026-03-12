from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, CLOUD_MODEL
import json

class CrisisAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=CLOUD_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.2 
        )

    async def resolve(self, crisis_description, current_schedule, historical_context="None"):
        prompt = f"""
        You are an emergency response AI for a national-level hackathon.
        A crisis has just been reported: "{crisis_description}"
        
        Here is the current locked schedule:
        {json.dumps(current_schedule, indent=2)}
        
        🧠 HISTORICAL CONTEXT (How we solved similar issues in the past):
        {historical_context}
        
        Figure out how to mathematically and logistically fix the schedule, heavily favoring strategies that worked in the historical context if applicable.
        
        Respond ONLY with valid JSON in this exact format:
        {{
            "mitigation_strategy": "Brief explanation of how you are solving this, mentioning past lessons if used.",
            "required_action": "reschedule",
            "delay_minutes": 30,
            "affected_sessions": ["Name of session 1"]
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