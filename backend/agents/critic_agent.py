# REMOVE THIS:
# from langchain_google_genai import ChatGoogleGenerativeAI

# ADD THIS:
from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, CLOUD_MODEL
import json

class CriticAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=CLOUD_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.2 # Crucial: Keep this low so Gemma outputs strict JSON
        )

    async def review(self, plan, simulation_metrics):
        prompt = f"""
        You are an elite event critic. Evaluate this hackathon plan mathematically and logistically.
        Plan: {plan}

        Evaluate this proposed event schedule:
        {json.dumps(plan, indent=2)}
        
        Physics Simulation Metrics:
        {json.dumps(simulation_metrics, indent=2)}

        Identify one major vulnerability (e.g., bottleneck, timing issue, burnout risk).
        Rate the plan on a scale of 0 to 100.

        Respond ONLY in valid JSON format:
        {{
            "vulnerability": "String describing the main flaw",
            "score": <int 0-100>,
            "feedback": "<string explaining deductions>",
            "approved": <boolean>
        }}
        """
        response = await self.llm.ainvoke(prompt)
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        
        try:
            # 🚀 Using ainvoke for the async Reflection Loop
            response = await self.llm.ainvoke(prompt)
            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Critic Error: {e}")
            return {"score": 50, "feedback": "Evaluation failed. Requires human review.", "approved": False}