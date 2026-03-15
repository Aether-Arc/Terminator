import json
from pydantic import BaseModel, Field
from typing import List
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
from tools.system_tools import swarm_tools
from config import get_resilient_llm

# ==========================================
# 🚀 1. PYDANTIC SCHEMA 
# ==========================================
class LineItem(BaseModel):
    category: str = Field(description="e.g., 'Lunch Catering', 'High-Speed Wi-Fi', 'Midnight Snacks', 'Security'")
    cost: float = Field(description="Calculated cost in the local currency")
    notes: str = Field(description="Brief explanation of the calculation (e.g., '₹500/head for 500 people')")

class BudgetOutput(BaseModel):
    total_calculated_cost: float = Field(description="The total sum of all line items")
    currency: str = Field(description="The currency used (e.g., 'INR', 'USD')")
    pricing_location: str = Field(description="The city where these prices apply")
    line_items: List[LineItem] = Field(description="List of specific budget allocations dynamically generated based on the schedule")

# ==========================================
# 🚀 2. BUDGET AGENT
# ==========================================
class BudgetAgent:
    def __init__(self):
        # LLM for reasoning, math, and internet searching
        self.reasoning_llm = get_resilient_llm(temperature=0.4)
        self.agent_executor = create_react_agent(self.reasoning_llm, swarm_tools)

        # Strictly enforces the Pydantic Schema for the frontend
        self.formatter_llm = get_resilient_llm(temperature=0).with_structured_output(BudgetOutput)

    async def calculate(self, event_data, schedule, specifics):
        crowd = event_data.get("expected_crowd", 500)
        location = event_data.get("location", "the target city")
        event_name = event_data.get("name", "Event")
        
        event_type = event_data.get("event_type", "Fest")
        duration = event_data.get("duration", "1 day")

        prompt = f"""
        You are the elite Chief Financial Officer (CFO) for '{event_name}' ({event_type}) in {location}.
        
        ===============================
        📊 EVENT CONTEXT
        ===============================
        - Expected Crowd: {crowd} people
        - Location: {location}
        - Event Duration: {duration}
        - Exact Schedule: {json.dumps(schedule, indent=2)}
        
        SPECIFIC TASK: {specifics}
        
        ===============================
        🔥 DYNAMIC BOTTOM-UP BUDGETING PROTOCOL
        ===============================
        1. 🚫 DO NOT USE HARDCODED ESTIMATES OR GUESSES. Do not use generic "$30/head" logic.
        2. 🔍 MANDATORY TOOL USE: You MUST use the 'web_search' tool to find realistic 2024-2025 average prices IN {location}. Search for things like:
           - "Average cost of per plate catering in {location} 2024"
           - "Auditorium or banquet hall rental cost in {location}"
           - "Event AV equipment rental cost in {location}"
        
        3. 🧠 ADAPTIVE SCHEDULING ANALYSIS: Read the exact schedule provided. You must budget for what is ACTUALLY happening in the schedule!
           - Are there multiple days? Multiply the daily venue/AV costs.
           - Is there an overnight hackathon? Budget for midnight snacks, 24-hour venue operations, overnight security, energy drinks, and high-speed WiFi infrastructure.
           - Are there guest speakers or keynotes? Budget for speaker travel/accommodation and stage setup.
           - Are there workshops? Budget for materials, desk setups, and power strips.
        
        4. 💱 LOCAL CURRENCY: Calculate all costs using the native currency of {location} (e.g., INR for Indian cities, USD for America, EUR for Europe).
        
        Analyze the schedule, run your web searches, and map out a highly detailed, realistic, bottom-up financial breakdown. Ensure the math adds up!
        """

        try:
            print(f"[*] BudgetAgent: Analyzing schedule & researching local {location} prices...")

            # 1. Let the ReAct agent do the internet searching and complex math
            res = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            raw_content = res["messages"][-1].content

            print("[*] BudgetAgent: Formatting financial data into strict UI schema...")

            # 2. Force the unstructured text through the Pydantic Formatter to guarantee perfect JSON
            formatted_result = await self.formatter_llm.ainvoke(
                f"Extract the budget breakdown from the following text and format it strictly according to the schema. Ensure the total_calculated_cost exactly equals the sum of the line items:\n\n{raw_content}"
            )

            # Convert the Pydantic model to a standard dictionary for the frontend
            return formatted_result.model_dump()

        except Exception as e:
            print(f"[🔥] Budget Agent Error: {e}")
            return {
                "total_calculated_cost": 0, 
                "currency": "Unknown", 
                "pricing_location": location, 
                "line_items": [{"category": "Error", "cost": 0, "notes": f"Failed to calculate budget: {str(e)}"}]
            }