import json
from pydantic import BaseModel, Field
from typing import List
from config import get_resilient_llm

class DetailedEvent(BaseModel):
    id: str = Field(description="Unique ID, e.g., 'evt_1'")
    session: str = Field(description="Exact session name from the base schedule")
    time: str = Field(description="Exact time from the base schedule")
    location: str = Field(description="Assigned room, venue, or area")
    description: str = Field(description="1-2 sentence operational description of what happens")
    volunteersRequired: int = Field(description="Number of physical volunteers needed")
    status: str = Field(description="Always default to 'Locked' or 'Pending AV'")
    type: str = Field(description="Event category: e.g., 'Keynote', 'Break', 'Interactive'")

class ItineraryOutput(BaseModel):
    details: List[DetailedEvent]

class ItineraryAgent:
    def __init__(self):
        # Structured output guarantees a perfect JSON array for your frontend
        self.llm = get_resilient_llm(temperature=0.2).with_structured_output(ItineraryOutput)

    async def expand_schedule(self, event_data, base_schedule):
        prompt = f"""
        You are the Elite Event Logistics Coordinator. 
        Take this basic schedule and expand it into a highly detailed operational itinerary.
        
        Event Context: {json.dumps(event_data)}
        Base Schedule: {json.dumps(base_schedule)}
        
        CRITICAL RULES:
        1. You MUST generate a detail block for every single session in the Base Schedule.
        2. Keep the 'session' and 'time' fields EXACTLY as they appear in the Base Schedule.
        3. Invent realistic, logical details for location, description, and volunteers based on the event context.
        """
        try:
            print("[*] ItineraryAgent: Expanding schedule details...")
            result = await self.llm.ainvoke(prompt)
            return [d.model_dump() for d in result.details]
        except Exception as e:
            print(f"[*] ItineraryAgent Error: {e}")
            return base_schedule