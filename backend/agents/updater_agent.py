import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from typing import Any
from config import get_resilient_llm

class UpdateOutput(BaseModel):
    schedule: list = Field(description="The fully updated chronological schedule")
    outputs: dict = Field(description="The fully updated agent outputs")

class UpdaterAgent:
    def __init__(self):
        print("[*] Initializing Advanced Dynamic Updater (Llama 3.1:8b)...")
        self.llm = get_resilient_llm(temperature=0).with_structured_output(UpdateOutput)

    async def process_update(self, instructions: str, schedule: list, outputs: dict) -> tuple[list, dict]:
        """
        An intelligent state mutator that applies delta changes to event plans.
        """
        parser = JsonOutputParser()

        # We give the model a reasoning framework to ensure it doesn't just "guess"
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Lead Event Strategist. Your goal is to apply surgical updates to an event plan.
            
            OPERATIONAL PROTOCOL:
            1. REASONING: First, analyze if the user's instruction affects the Timeline (schedule) or Content (outputs).
            2. TEMPORAL LOGIC: If a time is changed, shift all subsequent events in that day to maintain a logical flow.
            3. CONTENT INTEGRITY: If specific content is requested (e.g., 'Make emails more formal'), rewrite ONLY those parts.  "You must output ONLY valid JSON. Do not include markdown blocks or conversational text.\n"
                       "Do NOT rewrite everything. Only change the specific items requested.\n"
            4. JSON ONLY: You must output a JSON object with keys 'schedule' and 'outputs'.
            
            {format_instructions}"""),
            ("human", """CURRENT STATE:
            Schedule: {schedule}
            Outputs: {outputs}

            INSTRUCTION: {instructions}

            Apply the updates intelligently. If the instruction is a micro-edit, change only that line. If it is a global change, update all relevant fields.""")
        ])

        chain = prompt | self.llm | parser
        
        print(f"[*] Intelligence Swarm processing instruction: '{instructions}'")
        
        try:
            # We pass the current state as a shared context
            response = await chain.ainvoke({
                "schedule": json.dumps(schedule),
                "outputs": json.dumps(outputs),
                "instructions": instructions,
                "format_instructions": parser.get_format_instructions()
            })
            
            # Smart Key Recovery: If the model misses a key, we preserve the old one
            updated_schedule = response.get("schedule", schedule)
            updated_outputs = response.get("outputs", outputs)
            
            print("[✅] Intelligent Mutation Complete.")
            return updated_schedule, updated_outputs

        except Exception as e:
            print(f"[❌] Intelligent Mutation Failed: {e}")
            return schedule, outputs