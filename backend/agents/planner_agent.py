from langchain_google_genai import ChatGoogleGenerativeAI
import json
import asyncio

class PlannerAgent:
    def __init__(self):
        # PROTECTION 1: Tell Langchain to auto-retry if it hits a 429 error
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", max_retries=3)

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
        """Generates multiple unique candidate plans asynchronously with API protections."""
        plans = []
        event_name = event_data.get('name', 'Hackathon')
        crowd = event_data.get('expected_crowd', 500)

        for i in range(count):
            prompt = f"""
            You are an elite event architect planning '{event_name}' for {crowd} people.
            Design a UNIQUE, distinct variation (Option {i+1}) of an event plan.
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
                plan_data = json.loads(clean_json)
                plan_data["content"] = str(plan_data) 
                plans.append(plan_data)
                
            except Exception as e:
                print(f"API Rate Limit hit on plan {i+1}. Using Emergency Fallback.")
                # PROTECTION 3: The Show Must Go On! Inject a valid fallback plan.
                fallback_plan = {
                    "plan_overview": f"Emergency Contingency Plan Option {i+1}",
                    "sessions": [
                        {"name": "Opening Ceremony & Briefing", "duration_hours": 1, "requires_main_stage": True},
                        {"name": "Team Formation & Setup", "duration_hours": 1, "requires_main_stage": False},
                        {"name": "Core Hacking Phase", "duration_hours": 4, "requires_main_stage": False},
                        {"name": "Mentorship Checkpoint", "duration_hours": 1, "requires_main_stage": True},
                        {"name": "Final Pitches & Awards", "duration_hours": 2, "requires_main_stage": True}
                    ]
                }
                fallback_plan["content"] = str(fallback_plan)
                plans.append(fallback_plan)
                
            # PROTECTION 2: Pacing. Wait 3.5 seconds before asking Gemini for the next plan.
            # This completely avoids the "Burst" API rate limit.
            if i < count - 1:
                await asyncio.sleep(3.5)
                
        return plans