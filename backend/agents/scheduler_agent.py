import json
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from config import get_resilient_llm

# ==========================================
# 🚀 1. PYDANTIC SCHEMA (The Strict Formatter)
# ==========================================
class ScheduledSession(BaseModel):
    session: str = Field(description="Name of the event or activity")
    time: str = Field(description="Exact time window. Example format: 'Day 1 | 9:00 AM - 1:00 PM' or 'Day 1 | 10:00 PM - Day 2 | 6:00 AM'")
    status: str = Field(default="Locked", description="Always set to 'Locked'")

class EventSchedule(BaseModel):
    schedule: List[ScheduledSession] = Field(description="The chronologically ordered list of all scheduled sessions.")

class SchedulerAgent:
    def __init__(self):
        # We use the structured output wrapper so the LLM physically cannot hallucinate bad JSON
        self.llm = get_resilient_llm(temperature=0.2).with_structured_output(EventSchedule)

    async def create_schedule(self, best_plan):
        original_sessions = best_plan.get("sessions", [])
        if not original_sessions:
            return [{"error": "No sessions provided to schedule"}]

        session_names = [s.get("name", "Session") for s in original_sessions]
        user_constraints = best_plan.get("user_constraints", "None specified.")
        
        # 🚀 2. DYNAMIC CONTEXT INJECTION
        context_str = (str(session_names) + " " + str(user_constraints)).lower()
        is_hackathon = "hackathon" in context_str or "overnight" in context_str
        
        if is_hackathon:
            time_rules = """
            - This is a continuous Hackathon event. It runs through the night.
            - You can span sessions across midnight (e.g., 'Day 1 | 10:00 PM - Day 2 | 6:00 AM').
            - Intelligently place 'Mini Games' or 'Breaks' during late-night hours (e.g., 1:00 AM) to combat fatigue.
            - Ensure Day 2 sessions logically pick up where Day 1 ended.
            """
        else:
            time_rules = """
            - This is a standard corporate/educational event.
            - Strict operating hours: 9:00 AM to 8:00 PM ONLY. NO OVERNIGHT SESSIONS.
            - If the required sessions take more than 11 hours, spill them over into Day 2 starting at 9:00 AM.
            """

        # 🚀 3. THE SEMANTIC PROMPT
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an elite Event Logistics AI. Your job is to generate a flawless chronological schedule.
            
            USER CONSTRAINTS: {constraints}
            
            RULES FOR SCHEDULING:
            {time_rules}
            - Assign realistic durations for each task.
            - There must be NO time gaps unless it is an explicit 'Break'.
            - There must be NO overlapping times.
            - Follow the exact requested Output Schema format.
            """),
            ("user", "Please schedule the following sessions chronologically, adding explicit breaks/meals where natural: {sessions}")
        ])

        print(f"[*] SchedulerAgent: Utilizing Semantic AI Scheduling Engine (Hackathon Mode: {is_hackathon})...")
        
        # 🚀 4. EXECUTION
        chain = prompt | self.llm
        
        try:
            # The LLM does ALL the reasoning and formatting in one shot
            result: EventSchedule = await chain.ainvoke({
                "constraints": user_constraints,
                "time_rules": time_rules,
                "sessions": ", ".join(session_names)
            })
            
            # Convert the Pydantic object back into the dictionary array the frontend expects
            return [session.model_dump() for session in result.schedule]
            
        except Exception as e:
            print(f"[🔥] Semantic Scheduler Error: {e}")
            # Ultra-safe fallback just in case the LLM fails
            return [{"session": s, "time": f"Day 1 | TBD", "status": "Pending"} for s in session_names]

    def recalculate(self, crisis_solution):
        return {"status": "Recalculated"}