import json
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from config import get_resilient_llm

class UpdateOutput(BaseModel):
    schedule: list = Field(description="The fully updated chronological schedule")
    outputs: dict = Field(description="The fully updated agent outputs")

class UpdaterAgent:
    def __init__(self):
        print("[*] Initializing Advanced Dynamic Updater (Llama 3.1:8b)...")
        # with_structured_output handles ALL the JSON extraction safely
        self.llm = get_resilient_llm(temperature=0).with_structured_output(UpdateOutput)

    async def process_update(self, instructions: str, schedule: list, outputs: dict) -> tuple[list, dict]:
        """
        An intelligent state mutator that applies delta changes to event plans.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Lead Event Strategist. Your goal is to apply surgical updates to an event plan.
            
            OPERATIONAL PROTOCOL:
            1. REASONING: First, analyze if the user's instruction affects the Timeline (schedule) or Content (outputs).
            2. TEMPORAL LOGIC: If a time is changed, shift all subsequent events in that day to maintain a logical flow. Do not leave overlaps.
            3. CONTENT INTEGRITY: If specific content is requested, rewrite ONLY those parts. 
            4. SURGICAL STRIKE: Do NOT rewrite everything. Only change the specific items requested.
            """),
            ("human", """CURRENT STATE:
            Schedule: {schedule}
            Outputs: {outputs}

            INSTRUCTION: {instructions}

            Apply the updates intelligently and return the new state.""")
        ])

        # Remove the parser from the chain
        chain = prompt | self.llm 
        
        print(f"[*] Intelligence Swarm processing instruction: '{instructions}'")
        
        try:
            # The LLM now returns the UpdateOutput Pydantic class directly
            result: UpdateOutput = await chain.ainvoke({
                "schedule": json.dumps(schedule),
                "outputs": json.dumps(outputs),
                "instructions": instructions
            })
            
            print("[✅] Intelligent Mutation Complete.")
            
            # Extract the raw lists/dicts from the Pydantic model
            return result.schedule, result.outputs

        except Exception as e:
            print(f"[❌] Intelligent Mutation Failed: {e}")
            return schedule, outputs