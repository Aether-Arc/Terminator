from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
from tools.system_tools import swarm_tools
import json
from pydantic import BaseModel, Field
from typing import List

from config import get_resilient_llm

class LineItem(BaseModel):
    category: str = Field(description="e.g., 'Lunch Catering'")
    cost: float = Field(description="Calculated cost in USD")
    notes: str = Field(description="Brief explanation of the calculation")

class BudgetOutput(BaseModel):
    total_calculated_cost: float = Field(description="The total sum of all line items")
    pricing_location: str = Field(description="The city where these prices apply")
    line_items: List[LineItem] = Field(description="List of specific budget allocations")

class BudgetAgent:
    def __init__(self):
        self.llm = get_resilient_llm(temperature=0.2)
        # 🚀 Bind tools so the agent can look up current local prices
        self.agent_executor = create_react_agent(self.llm, swarm_tools)
        self.llm = get_resilient_llm(temperature=0.2).with_structured_output(BudgetOutput)

    # 🚀 Notice we added `schedule` so it can see exactly what the other agents planned!
    async def calculate(self, event_data, schedule, specifics):
        crowd = event_data.get("expected_crowd", 500)
        location = event_data.get("location", "a major tech hub")
        event_name = event_data.get("name", "Event")
        
        prompt = f"""
        You are the Chief Financial Officer (CFO) for '{event_name}' in {location}.
        
        CRITICAL EVENT CONTEXT:
        - Expected Crowd: {crowd} people
        - Location: {location}
        - Exact Schedule Planned by the Swarm: {json.dumps(schedule, indent=2)}
        
        SPECIFIC TASK: {specifics}
        
        BOTTOM-UP BUDGETING PROTOCOL:
        1. Do NOT use a predefined total. You must build the budget from the bottom up.
        2. Analyze the Schedule carefully. If there is a lunch break, budget for catering. If there is a keynote, budget for AV & speaker fees. If it's a 2-day schedule, double the venue costs.
        3. MANDATORY TOOL USE: Use the 'web_search' tool to find realistic 2024-2025 average prices IN {location} for the specific line items you identify.
        
        Calculate the exact total by summing up your researched line items.
        
        Respond ONLY in valid JSON format:
        {{
            "total_calculated_cost": 54200,
            "pricing_location": "{location}",
            "line_items": [
                {{"category": "Lunch Catering", "cost": 15000, "notes": "Based on $30/head for {crowd} people in {location}"}},
                {{"category": "AV Rental", "cost": 5000, "notes": "Required for 'Technical Keynote' session"}}
            ]
        }}
        """
        try:
            print("[*] BudgetAgent: Cross-referencing schedule & researching local prices...")
            response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            clean_json = response["messages"][-1].content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Budget Agent Error: {e}")
            return {"total_calculated_cost": 0, "pricing_location": location, "line_items": [{"error": "Failed to calculate budget."}]}