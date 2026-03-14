import json
from pydantic import BaseModel, Field
from typing import List
from config import get_resilient_llm

# ==========================================
# 🚀 PYDANTIC SCHEMA
# ==========================================
class DetailedEvent(BaseModel):
    id: int
    session: str = Field(description="The exact session name from the base schedule")
    time: str = Field(description="The exact time from the base schedule")
    location: str = Field(description="Logical physical location (e.g., 'Main Stage', 'Workshop Room A')")
    description: str = Field(description="Brief operational description (AV needs, catering, etc.)")
    volunteersRequired: int = Field(description="Number of volunteers needed for this specific session")
    status: str = Field(default="Locked")
    type: str = Field(description="Categorize as: Keynote, Break, Interactive, Panel, Workshop, or General")

class DetailedScheduleOutput(BaseModel):
    detailed_schedule: List[DetailedEvent]

# ==========================================
# 🚀 ITINERARY AGENT
# ==========================================
class ItineraryAgent:
    def __init__(self):
        # Structured output guarantees perfectly formatted JSON for the React UI
        self.llm = get_resilient_llm(temperature=0.2).with_structured_output(DetailedScheduleOutput)

    async def expand_schedule(self, event_data, schedule):
        if not schedule:
            return [{"error": "No base schedule provided to expand."}]
            
        prompt = f"""
        You are an elite Event Operations Director. 
        Take the following high-level schedule and expand it into a detailed operational itinerary.
        
        EVENT CONTEXT:
        - Name: {event_data.get('name', 'Event')}
        - Type: {event_data.get('event_type', 'General')}
        - Crowd: {event_data.get('expected_crowd', 500)}
        - Location: {event_data.get('location', 'TBD')}
        
        BASE SCHEDULE:
        {json.dumps(schedule, indent=2)}
        
        CRITICAL RULES:
        1. Keep the original 'session' and 'time' EXACTLY as provided in the base schedule.
        2. Assign a realistic physical location/room for the crowd size.
        3. Write a 1-sentence operational description (what happens, AV setup needed, catering notes).
        4. Estimate realistic volunteer numbers.
        """
        
        try:
            print(f"[*] ItineraryAgent: Expanding schedule into detailed operational view...")
            result = await self.llm.ainvoke(prompt)
            
            # Convert Pydantic models to standard dictionaries
            detailed_list = []
            for idx, item in enumerate(result.detailed_schedule):
                dump = item.model_dump()
                dump["id"] = idx + 1 # Assign a unique ID for the React keys
                detailed_list.append(dump)
                
            return detailed_list
            
        except Exception as e:
            print(f"[!] ItineraryAgent Error: {e}")
            return [{"id": 1, "session": "Error generating details", "time": "N/A", "location": "N/A", "description": str(e), "volunteersRequired": 0, "status": "Error", "type": "Error"}]