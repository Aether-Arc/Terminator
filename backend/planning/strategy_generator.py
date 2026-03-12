from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, CLOUD_MODEL
import json

class StrategyGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=CLOUD_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.6 # Slightly higher for creative problem solving
        )

    async def generate(self, crisis_description, crowd_size):
        prompt = f"""
        A crisis just occurred at an event with {crowd_size} people: "{crisis_description}"
        
        Invent 3 distinct strategies to handle this crisis. 
        For each strategy, estimate its mathematical impact:
        - crowd_modifier: A multiplier for how many people will stay (e.g., 1.0 means everyone stays, 0.5 means half leave).
        - delay_minutes: How many minutes this solution will delay the schedule.
        
        Respond ONLY in valid JSON format like this:
        [
            {{"name": "Evacuate and move to virtual format", "crowd_modifier": 0.2, "delay_minutes": 60}},
            {{"name": "Pause, clear the area, and resume later", "crowd_modifier": 0.9, "delay_minutes": 45}}
        ]
        """
        try:
            response = await self.llm.ainvoke(prompt)
            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Strategy Gen Error: {e}")
            # Fallback mathematical actions if the LLM fails
            return [{"name": "Emergency Dynamic Reschedule", "crowd_modifier": 0.8, "delay_minutes": 30}]