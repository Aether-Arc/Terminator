from langchain_google_genai import ChatGoogleGenerativeAI
import json

class CriticAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    async def review(self, plan):
        prompt = f"""
        You are an elite event critic. Evaluate this hackathon plan mathematically and logistically.
        Plan: {plan}

        Identify one major vulnerability (e.g., bottleneck, timing issue, burnout risk).
        Rate the plan on a scale of 0 to 100.

        Respond ONLY in valid JSON format:
        {{
            "vulnerability": "String describing the main flaw",
            "score": 85
        }}
        """
        response = await self.llm.ainvoke(prompt)
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            return {"vulnerability": "Formatting error in evaluation", "score": 50}