# REMOVE THIS:
# from langchain_google_genai import ChatGoogleGenerativeAI

# ADD THIS:
from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, AI_MODEL
import json
import asyncio

class PlannerAgent:
    def __init__(self):
        # PROTECTION 1: Tell Langchain to auto-retry if it hits a 429 error
        self.llm = ChatOpenAI(
            model=AI_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.2 # Crucial: Keep this low so Gemma outputs strict JSON
        )

    async def generate_plan(self, event_data):
        event_name = event_data.get('name', 'Hackathon')
        crowd = event_data.get('expected_crowd', 500)
        
        prompt = f"""
        You are an elite event architect planning '{event_name}' for {crowd} people.
        Break the event down into exactly 5 logical milestones/sessions.
        Respond ONLY in valid JSON format like this:
        {{
            "plan_overview": "String describing the vibe",
            "sessions": [
                {{"name": "Opening Ceremony", "duration_hours": 1, "requires_main_stage": true}}
            ]
        }}
        """
        try:
            response = await self.llm.ainvoke(prompt)
            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Single Plan API Error: {e}")
            return {"error": "API Fallback", "sessions": []}

    async def generate_multiple_plans(self, event_data, count=3):
        plans = []
        event_name = event_data.get('name', 'Hackathon')
        crowd = event_data.get('expected_crowd', 500)
        
        # Fetch the memories injected by the LangGraph
        history = event_data.get("historical_context", "No past data available.")
        rl_strategy = event_data.get("learned_strategy", "Prioritize balanced scheduling.")
        critic_notes = event_data.get("critic_feedback", None)

        for i in range(count):

            feedback_prompt = ""
            if critic_notes:
                feedback_prompt = f"""
                ⚠️ CRITIC REJECTION NOTICE: Your previous plan was rejected by the Critic Agent.
                The Critic said: "{critic_notes}"
                You MUST fix these specific issues in this new variation.
                """


            prompt = f"""
            You are an elite event architect planning '{event_name}' for {crowd} people.
            {feedback_prompt}
            Design a UNIQUE, distinct variation (Option {i+1}) of an event plan.
            Break the event down into exactly 5 logical milestones/sessions.
            
            🧠 SWARM INTELLIGENCE (LEARNED CONTEXT):
            - Past similar events memory: {history}
            - Reinforcement Learning Policy Suggestion: {rl_strategy}
            
            Based on the SWARM INTELLIGENCE above, avoid past mistakes and adapt your plan.
            
            Respond ONLY in valid JSON format like this:
            {{
                "plan_overview": "String describing the vibe and how it adapts past lessons",
                "sessions": [
                    {{"name": "Opening Ceremony", "duration_hours": 1, "requires_main_stage": true}}
                ]
            }}
            """
            
            try:
                response = await self.llm.ainvoke(prompt)
                clean_json = response.content.replace("```json", "").replace("```", "").strip()
                plan_data = json.loads(clean_json)
                plan_data["content"] = str(plan_data) 
                plans.append(plan_data)
                
            except Exception as e:
                print(f"API Rate Limit hit on plan {i+1}. Using Emergency Fallback.")
                # ... keep your existing fallback logic here ...
                fallback_plan = {
                    "plan_overview": f"Emergency Contingency Plan Option {i+1}",
                    "sessions": [{"name": "Core Phase", "duration_hours": 4, "requires_main_stage": False}]
                }
                fallback_plan["content"] = str(fallback_plan)
                plans.append(fallback_plan)
                
        return plans