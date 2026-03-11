# REMOVE THIS:
# from langchain_google_genai import ChatGoogleGenerativeAI

# ADD THIS:
from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, AI_MODEL
import json

class CriticAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=AI_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.2 # Crucial: Keep this low so Gemma outputs strict JSON
        )

    async def review(self, plan):
        prompt = f"""
        You are an elite event critic. Evaluate this hackathon plan mathematically and logistically.
        Plan: {plan}

        Identify one major vulnerability (e.g., bottleneck, timing issue, burnout risk).
        Rate the plan on a scale of 0 to 100.

        Respond ONLY in valid JSON format:
        {{
            "vulnerability": "String describing the main flaw",
            "score": 85,
            "feedback": "Explain exactly what is wrong and what the Planner needs to fix."
        }}
        """
        response = await self.llm.ainvoke(prompt)
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            return {"vulnerability": "Formatting error in evaluation", "score": 50}