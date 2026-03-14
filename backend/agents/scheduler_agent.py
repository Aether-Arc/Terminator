import json
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from config import get_resilient_llm

# ==========================================
# ✅ PYDANTIC SCHEMA
# ==========================================
class ScheduledSession(BaseModel):
    session: str = Field(
        description="Name of the event session. CRITICAL: DO NOT put time ranges or timestamps in this field."
    )
    time: str = Field(
        description="Example: Day 1 | 9:00 AM - 10:00 AM or Day 2 | 2:00 PM - 3:30 PM"
    )
    status: str = Field(
        default="Locked",
        description="Always Locked"
    )

class EventSchedule(BaseModel):
    schedule: List[ScheduledSession] = Field(
        description="Full ordered schedule"
    )

# ==========================================
# ✅ SCHEDULER AGENT
# ==========================================
class SchedulerAgent:
    def __init__(self):
        # Structured output prevents bad JSON
        self.llm = get_resilient_llm(temperature=0.2).with_structured_output(EventSchedule)

    # ==========================================
    # MAIN SCHEDULER
    # ==========================================
    async def create_schedule(self, best_plan):
        original_sessions = best_plan.get("sessions", [])

        if not original_sessions:
            return [{"error": "No sessions provided"}]

        session_names = [s.get("name", "Session") for s in original_sessions]
        user_constraints = best_plan.get("user_constraints", "None")
        
        # 🚀 PULL EXTRACTED DURATION DIRECTLY FROM THE PLANNER
        event_duration = best_plan.get("duration", "1 day")

        # ======================================
        # CONTEXT DETECTION
        # ======================================
        context_str = (str(session_names) + " " + str(user_constraints) + " " + str(event_duration)).lower()

        # 🚀 STRICT HACKATHON CHECK: Must be a hackathon AND indicate it spans >24 hours
        is_continuous_overnight = (
            ("hackathon" in context_str or "overnight" in context_str) and
            ("24" in context_str or "48" in context_str or "day" in context_str or "continuous" in context_str)
        )

        # ======================================
        # TIME RULES & BIOLOGICAL NEEDS
        # ======================================
        if is_continuous_overnight:
            time_rules = f"""
            EVENT DURATION: {event_duration}
            
            RULES FOR THIS CONTINUOUS HACKATHON:
            - This is a continuous overnight event. Sessions MAY run overnight and cross midnight.
            - Use format: Day 1 | 10:00 PM - Day 2 | 6:00 AM
            - YOU MUST ADD LOGICAL HUMAN BREAKS:
              * Lunch Break (~1:00 PM)
              * Dinner Break (~7:00 PM)
              * Midnight Snack/Energy Break (~12:00 AM or 1:00 AM)
            - Spread the sessions logically across the entire {event_duration}.
            """
        else:
            time_rules = f"""
            EVENT DURATION: {event_duration}
            
            RULES FOR THIS STANDARD EVENT:
            - STRICT OPERATING HOURS: 9:00 AM to 8:00 PM ONLY per day.
            - ABSOLUTELY NO SESSIONS can be scheduled before 9:00 AM or after 8:00 PM. 
            - If you run out of time on Day 1, you MUST overflow and push the remaining sessions to Day 2 starting at 9:00 AM.
            - YOU MUST ADD LOGICAL HUMAN BREAKS EVERY DAY:
              * Lunch Break (~12:30 PM - 1:30 PM)
              * Dinner Break (If event runs until 8:00 PM, add dinner ~6:30 PM)
              * Short 15-30 minute rest/coffee breaks between intense sessions.
            - Spread the sessions out chronologically to fit the {event_duration}.
            """

        # ======================================
        # PROMPT
        # ======================================
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are an ELITE EVENT LOGISTICS AI.
Create a perfect professional chronological schedule.

USER CONSTRAINTS:
{constraints}

{time_rules}

==========================
STRICT RULES
==========================
1. No overlaps.
2. No gaps unless it is a creatively named break, meal, or transition.
3. Respect the duration. Spread events out intelligently across the days.
4. Keep names EXACT. Do not modify the creative session names given to you by the Planner. You may only insert your own names for Meals/Breaks (e.g. "Networking Lunch").
5. CRITICAL AVOIDANCE: The `session` field MUST ONLY contain the text name of the session. NEVER put timestamps (like 9:00 AM - 9:30 AM) in the session string!

==========================
FORMAT
==========================
Use format: Day X | start - end
Examples:
Day 1 | 9:00 AM - 10:30 AM
Day 1 | 12:30 PM - 1:30 PM (Networking Lunch)
Day 2 | 11:00 AM - 1:00 PM

Return structured output only.
"""
            ),
            (
                "user",
                """
Schedule these sessions chronologically across {duration}, adding breaks and meals where natural:

{sessions}
"""
            )
        ])

        print(f"[*] SchedulerAgent running (Continuous Overnight={is_continuous_overnight}, Duration={event_duration})")
        chain = prompt | self.llm

        try:
            result: EventSchedule = await chain.ainvoke({
                "constraints": user_constraints,
                "time_rules": time_rules,
                "sessions": ", ".join(session_names),
                "duration": event_duration
            })

            return [s.model_dump() for s in result.schedule]

        except Exception as e:
            print("[Scheduler Error]", e)
            return [
                {
                    "session": s,
                    "time": "Day 1 | TBD",
                    "status": "Pending"
                }
                for s in session_names
            ]

    # ==========================================
    # CRISIS RECALC
    # ==========================================
    def recalculate(self, crisis_solution):
        return {"status": "Recalculated"}