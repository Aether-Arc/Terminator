import json
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from config import get_resilient_llm

class UpdateOutput(BaseModel):
    schedule: list = Field(description="The fully updated chronological schedule array. CRITICAL: NEVER include cancelled events in this array.")
    explanation: str = Field(description="A brief explanation of the time-math you just performed")

class UpdaterAgent:
    def __init__(self):
        print("[*] Initializing Advanced Dynamic Updater...")
        self.llm = get_resilient_llm(temperature=0).with_structured_output(UpdateOutput)

    async def process_update(self, instructions: str, schedule: list, outputs: dict) -> tuple[list, dict]:
        """An intelligent state mutator that applies delta changes and time-math to event plans."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Elite Event Timekeeper & Strategist. Your goal is to cleanly mutate an event schedule based on user instructions.
            
            CRITICAL TEMPORAL LOGIC (AVOID OVERLAPS):
            1. SEARCH & MATCH: Find the session that semantically matches the user's request.
            2. CANCELLATIONS (STRICT): If the user asks to cancel a session, you MUST completely DELETE its dictionary object from the array. DO NOT keep it and rename it to 'Cancelled'. It must vanish from the JSON array.
            3. DELAYS/PREPONES: Shift the start and end times of EVERY subsequent event. Zero overlaps.
            4. TIME FORMAT: Maintain strict formatting: "Day X | HH:MM AM - HH:MM PM".
            
            Always return the ENTIRE modified schedule array. Do not truncate it.
            """),
            ("human", """CURRENT SCHEDULE:
            {schedule}

            INSTRUCTION: {instructions}

            Apply the updates intelligently, do the necessary time-math to prevent overlaps, and return the fully updated schedule.""")
        ])

        chain = prompt | self.llm 
        
        print(f"[*] Intelligence Swarm processing instruction: '{instructions}'")
        
        try:
            result = await chain.ainvoke({
                "schedule": json.dumps(schedule),
                "instructions": instructions
            })
            
            is_dict = isinstance(result, dict)
            explanation = result.get("explanation", "Schedule updated") if is_dict else getattr(result, "explanation", "Schedule updated")
            raw_new_schedule = result.get("schedule", schedule) if is_dict else getattr(result, "schedule", schedule)
            
            # ========================================================
            # 🚀 THE FIX: Python-Level Local LLM Safety Filter
            # ========================================================
            # Local models (like Llama 3) often ignore deletion instructions and just rename things to "Cancelled".
            # We will aggressively filter them out in Python to ensure the UI updates correctly.
            
            clean_schedule = []
            for item in raw_new_schedule:
                # Safely extract the strings to check
                session_name = str(item.get("session", "")).lower()
                status_name = str(item.get("status", "")).lower()
                
                # 1. Purge any cancelled items
                if "cancel" not in session_name and "cancel" not in status_name:
                    
                    # 2. Clean up ugly "(DELAYED BY X HOURS)" tags from the title 
                    # so the UI looks professional (the time shift is enough visual info)
                    clean_session = item.get("session", "").split("(DELAYED")[0].split("(delayed")[0].strip()
                    item["session"] = clean_session
                    
                    clean_schedule.append(item)

            print(f"[✅] Intelligent Mutation Complete: {explanation}")
            
            return clean_schedule, outputs

        except Exception as e:
            print(f"[❌] Intelligent Mutation Failed: {e}")
            return schedule, outputs