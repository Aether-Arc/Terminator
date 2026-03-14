import json
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from config import get_resilient_llm

class UpdateOutput(BaseModel):
    schedule: list = Field(description="The fully updated chronological schedule array")
    explanation: str = Field(description="A brief explanation of the time-math you just performed")

class UpdaterAgent:
    def __init__(self):
        print("[*] Initializing Advanced Dynamic Updater...")
        # with_structured_output safely enforces the JSON schema
        self.llm = get_resilient_llm(temperature=0).with_structured_output(UpdateOutput)

    async def process_update(self, instructions: str, schedule: list, outputs: dict) -> tuple[list, dict]:
        """An intelligent state mutator that applies delta changes and time-math to event plans."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Elite Event Timekeeper & Strategist. Your goal is to cleanly mutate an event schedule based on user instructions.
            
            CRITICAL TEMPORAL LOGIC (AVOID OVERLAPS):
            1. DELAYS/PREPONES: If an event's time is changed, you MUST recalculate and shift the start and end times of EVERY subsequent event on that day. There must be absolutely ZERO overlaps.
            2. CANCELLATIONS: If the user asks to cancel or remove a specific session, you MUST delete it from the schedule array entirely. Then, shift the remaining events up to close the time gap.
            3. TIME FORMAT: Maintain strict formatting: "Day X | HH:MM AM - HH:MM PM".
            
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
            # 🚀 FIX: We ONLY pass the schedule to the LLM so it doesn't get confused by massive output dictionaries!
            result: UpdateOutput = await chain.ainvoke({
                "schedule": json.dumps(schedule),
                "instructions": instructions
            })
            
            print(f"[✅] Intelligent Mutation Complete: {result.explanation}")
            
            # Return the newly calculated schedule, but safely pass the old outputs through untouched
            return result.schedule, outputs

        except Exception as e:
            print(f"[❌] Intelligent Mutation Failed: {e}")
            return schedule, outputs