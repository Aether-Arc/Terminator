from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
import json

class BudgetAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model=LOCAL_MODEL, base_url=OLLAMA_BASE_URL, api_key=OPENAI_API_KEY, temperature=0.2)
        self.baseline_budget = 50000

    async def calculate(self, event_data):
        crowd = event_data.get("expected_crowd", 500)
        venue = event_data.get("venue", "Convention Center")
        
        prompt = f"""
        You are the Chief Financial Officer (CFO) for an event.
        - Crowd: {crowd} people
        - Location/Style: {venue}
        - Total Available Budget: ${self.baseline_budget}
        
        Generate a highly realistic, itemized budget breakdown. You must factor in hidden costs (insurance, WiFi scaling, AV equipment).
        
        Respond ONLY in valid JSON format:
        {{
            "total_projected_cost": 48000,
            "status": "Under Budget",
            "line_items": [
                {{"category": "Catering", "cost": 15000, "notes": "$30 per head for 500 people"}}
            ]
        }}
        """
        response = await self.llm.ainvoke(prompt)
        try:
            return json.loads(response.content.replace("```json", "").replace("```", "").strip())
        except:
            return {"total_projected_cost": self.baseline_budget, "status": "Unknown", "line_items": []}