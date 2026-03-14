import json
from typing import List
from pydantic import BaseModel, Field
from config import get_resilient_llm

# 🚀 Added explicit field descriptions to make the AI hyper-intelligent
class VolunteerRole(BaseModel):
    role_name: str = Field(description="Name of the specific volunteer role (e.g., 'Stage Hand', 'Crowd Control')")
    headcount: int = Field(description="Precise number of volunteers needed for this role")
    active_time: str = Field(description="The exact shift duration based on the schedule")
    reason: str = Field(description="Operational justification for why this role is needed at this specific time")

class VolunteerOutput(BaseModel):
    total_volunteers_required: int = Field(description="The sum of all required volunteers")
    roles: List[VolunteerRole] = Field(description="Chronological list of volunteer shifts")

class VolunteerAgent:
    def __init__(self):
        # with_structured_output guarantees we get a structured Pydantic object back
        self.llm = get_resilient_llm(temperature=0.2).with_structured_output(VolunteerOutput)

    async def assign_shifts(self, event_data, schedule, specifics):
        crowd = event_data.get("expected_crowd", 500)
        
        prompt = f"""
You are the Elite Volunteer Coordinator.

Event crowd: {crowd}

Full locked schedule:

{json.dumps(schedule, indent=2)}

Task:
{specifics}

================================
OPERATIONAL ASSIGNMENT PROTOCOL
================================

You MUST analyze the schedule line by line.

For EACH session decide:

What volunteers needed
How many needed
How long needed
Why needed

Do NOT guess.

================================
SCALE WITH CROWD
================================

Use crowd size.

Rules:

50 people → small team
200 → medium
500 → large
1000+ → large crew

Examples:

Crowd control → 1 per 50 people
Registration → 1 per 40 people
Food → 1 per 30 people
Security support → 1 per 100 people
Stage crew → 2–5 per stage
AV → 2–4
Logistics → 3–6

================================
USE SESSION TYPE
================================

Check session name.

Lunch / Food → catering + crowd control
Registration → desk + queue
Workshop → desk + AV
Talk / keynote → AV + stage
Competition → judges + helpers
Concert → stage + crowd
Sports → field + refs
Hackathon → overnight crew
Break → minimal staff
Opening / closing → large team

Do NOT assign same role to all.

================================
TIME AWARENESS
================================

Use time field.

If session is:

Day 1 | 9:00 - 10:00

Shift must match.

Do not assign all day if short.

================================
MULTI DAY RULE
================================

If multiple days:

Repeat shifts per day.

Do not assign one team for all days.

================================
OVERNIGHT RULE
================================

If overnight:

Add night shift
Add security
Add support crew

================================
EVENT TYPE RULE
================================

Tech → AV + IT + desk
Cultural → stage + decor
Social → games + crowd
Sports → field crew
Workshop → helpers
Seminar → AV + registration
Fest → mix

================================
ROLE RULE
================================

Create realistic roles:

Registration Desk
Crowd Control
Stage Crew
AV Support
Food Service
Logistics Runner
Help Desk
Security Support
Technical Support
Event Coordinator

================================
HEADCOUNT RULE
================================

Do NOT give random numbers.

Use logic.

Explain reason.

================================
OUTPUT RULE
================================

Return roles in time order.

Total must equal sum.

Do not skip sessions.
"""
        
        try:
            # 🚀 RESULT IS ALREADY PARSED! No need for manual JSON parsing or regex.
            result: VolunteerOutput = await self.llm.ainvoke(prompt)
            
            # Convert the Pydantic object back into a clean dictionary for the React UI
            return result.model_dump()
            
        except Exception as e:
            print(f"[❌] VolunteerAgent Error: {e}")
            # 🚀 Safe Fallback: Returns a valid schema if the AI ever times out
            fallback_count = max(1, crowd // 20)
            return {
                "total_volunteers_required": fallback_count, 
                "roles": [
                    {
                        "role_name": "General Operations Floater", 
                        "headcount": fallback_count, 
                        "active_time": "All Day", 
                        "reason": f"Fallback assignment triggered."
                    }
                ]
            }