import json
from pydantic import BaseModel, Field
from typing import List

from langgraph.prebuilt import create_react_agent
from config import get_resilient_llm
from tools.system_tools import swarm_tools


# ==========================================
# SCHEMA (USE FLOAT FOR STABILITY)
# ==========================================

class LineItem(BaseModel):
    category: str = Field(description="Budget category")
    cost: float = Field(description="Cost in local currency")
    notes: str = Field(description="Calculation explanation")


class BudgetOutput(BaseModel):

    total_calculated_cost: float

    currency: str

    pricing_location: str

    line_items: List[LineItem]


# ==========================================
# BUDGET AGENT
# ==========================================

class BudgetAgent:

    def __init__(self):

        # reasoning LLM (tools)
        self.reasoning_llm = get_resilient_llm(
            temperature=0.4
        )

        self.agent_executor = create_react_agent(
            self.reasoning_llm,
            swarm_tools
        )

        # formatter LLM (STRICT JSON)
        self.formatter_llm = get_resilient_llm(
            temperature=0
        ).with_structured_output(BudgetOutput)

    # ==========================================
    # MAIN
    # ==========================================

    async def calculate(self, event_data, schedule, specifics):

        crowd = event_data.get("expected_crowd", 300)

        location = event_data.get(
            "location",
            "India"
        )

        event_name = event_data.get(
            "name",
            "Event"
        )

        event_type = event_data.get(
            "event_type",
            "festival"
        )

        duration = event_data.get(
            "duration",
            "1 day"
        )

        prompt = f"""
You are the CFO for an event.

Event: {event_name}
Type: {event_type}
Location: {location}
Crowd: {crowd}
Duration: {duration}

FULL SCHEDULE:
{json.dumps(schedule, indent=2)}

Task:
{specifics}

===============================
RULES
===============================

You MUST use web_search before pricing.

Use multiple searches.

Budget must match schedule.

Scale with crowd and duration.

Return final budget text only.

Example format:

Venue - 50000 - hall rent
Food - 100000 - 200 x 500
Security - 15000 - guards

Total = 165000 INR

Do NOT return thoughts.
Do NOT return tool logs.
Return only final budget.
"""

        try:

            print(f"[*] BudgetAgent researching prices in {location}")

            res = await self.agent_executor.ainvoke(
                {"messages": [("user", prompt)]}
            )

            raw = res["messages"][-1].content

            print("RAW OUTPUT:\n", raw)

            if not raw or len(raw) < 10:
                raise Exception("Empty budget output")

            print("[*] Formatting budget")

            formatted = await self.formatter_llm.ainvoke(
                f"""
Extract budget from text.

Text:
{raw}

Rules:

Return strict schema.

Fix total if mismatch.

Costs must be numbers.
"""
            )

            result = formatted.model_dump()

            # ============================
            # SAFE STRING CONVERSION
            # ============================

            result["total_calculated_cost"] = str(
                result["total_calculated_cost"]
            )

            for item in result["line_items"]:
                item["cost"] = str(item["cost"])

            return result

        except Exception as e:

            print("Budget error:", e)

            return {
                "total_calculated_cost": "0",
                "currency": "Unknown",
                "pricing_location": location,
                "line_items": [
                    {
                        "category": "Error",
                        "cost": "0",
                        "notes": str(e),
                    }
                ],
            }
