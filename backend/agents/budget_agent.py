import json
from pydantic import BaseModel, Field
from typing import List

from langgraph.prebuilt import create_react_agent
from config import get_resilient_llm
from tools.system_tools import swarm_tools


# ==========================================
# SCHEMA
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

        # reasoning + tools
        self.reasoning_llm = get_resilient_llm(
            temperature=0.4
        )

        self.agent_executor = create_react_agent(
            self.reasoning_llm,
            swarm_tools
        )

        # formatter
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

================================
TOOL-DRIVEN BUDGET PROTOCOL
================================

You MUST use web_search before calculating.

Loop:

1. Read schedule
2. Detect needs
3. Search price
4. Calculate
5. Repeat search if needed

You MUST use web_search multiple times.

Example searches:

catering price {location}
hall rent {location}
sound system rental {location}
security guard cost {location}
generator rent {location}
wifi event cost {location}
stage setup cost {location}
event lighting cost {location}
poster printing cost {location}

Do NOT guess prices.

================================
SCHEDULE ANALYSIS
================================

Analyze schedule.

Look for:

days
hours
overnight
hackathon
workshop
speaker
competition
concert
sports
talk
food breaks
night sessions

Budget must match schedule.

Examples:

3 days → multiply venue

overnight → snacks + security

workshop → materials

speaker → travel

stage → AV

================================
EVENT TYPE RULE
================================

Tech → wifi, prizes, AV
Cultural → stage, lights
Social → decor, games
Workshop → materials
Seminar → speaker cost
Sports → ground + refs
Music → sound + stage

================================
CROWD SCALING
================================

All costs scale with crowd.

Food = per person × crowd × days

Security = per 100 people

Venue must fit crowd.

================================
DURATION SCALING
================================

Multi-day → multiply

Overnight → add

night staff
snacks
security
electricity

================================
MANDATORY CATEGORIES
================================

Venue
Food
Snacks
AV
Stage
Security
Staff
WiFi
Electricity
Marketing
Guest
Transport
Decoration
Permissions

================================
WEB SEARCH MINIMUM
================================

Use web_search at least 3 times.

If price missing → search again.

================================
LINE ITEMS
================================

Return 8–20 items.

Each must have:

category
cost
notes

================================
CURRENCY
================================

Use local currency.

India → INR
USA → USD
Europe → EUR

================================
MATH CHECK
================================

Sum(line_items) must equal total.

Fix if wrong.

================================
FINAL
================================

Use tools before answering.
"""

        try:

            print(
                f"[*] BudgetAgent researching prices in {location}"
            )

            res = await self.agent_executor.ainvoke(
                {"messages": [("user", prompt)]}
            )

            raw = res["messages"][-1].content

            print("[*] Formatting budget")

            formatted = await self.formatter_llm.ainvoke(
                f"""
Extract budget.

Text:

{raw}

Rules:

Return strict schema.

Ensure:

sum(line_items.cost)
==
total_calculated_cost
"""
            )

            return formatted.model_dump()

        except Exception as e:

            print("Budget error", e)

            return {
                "total_calculated_cost": 0,
                "currency": "Unknown",
                "pricing_location": location,
                "line_items": [
                    {
                        "category": "Error",
                        "cost": 0,
                        "notes": str(e),
                    }
                ],
            }