import json
import asyncio
import re

from langgraph.prebuilt import create_react_agent
from langchain_core.utils.json import parse_json_markdown

from config import get_resilient_llm
from tools.system_tools import swarm_tools


class PlannerAgent:

    def __init__(self):
        self.llm = get_resilient_llm(temperature=0.45)
        self.agent_executor = create_react_agent(self.llm, swarm_tools)

    async def _generate_single_branch(self, prompt, i):

        try:

            response = await self.agent_executor.ainvoke(
                {"messages": [("user", prompt)]}
            )

            text = response["messages"][-1].content

            clean = text.replace("```json", "").replace("```", "").strip()

            match = re.search(r"\{.*\}", clean, re.DOTALL)

            if not match:
                raise ValueError("No JSON found")

            data = parse_json_markdown(match.group(0))

            data["content"] = str(data)

            return data

        except Exception as e:

            print("Planner error", e)

            return {
                "plan_overview": "fallback",
                "duration": "1 day",
                "event_type": "festival",
                "user_constraints": "",
                "sessions": [
                    {
                        "name": "Emergency Session",
                        "requires_main_stage": False,
                    }
                ],
            }

    # ============================================
    # MULTIPLE PLANS
    # ============================================

    async def generate_multiple_plans(self, event_data, count=1):

        event_name = event_data.get("name", "Event")
        crowd = event_data.get("expected_crowd", 100)

        history = event_data.get("historical_context", "")
        rl = event_data.get("learned_strategy", "")

        constraints = event_data.get("user_constraints", "")
        event_type = event_data.get("event_type", "festival")

        tasks = []

        for i in range(count):

            prompt = f"""
You are ELITE GLOBAL EVENT ARCHITECT AI.

Design realistic events like IIT fest, Mood Indigo, Techfest,
college fests, workshops, seminars, social events.

Event name: {event_name}
Expected crowd: {crowd}
Event type: {event_type}

===============================
MANDATORY WEB SEARCH
===============================

Use web_search before planning.

Search:

"{event_type} event ideas"
"{event_name} event format"
"college fest activities"
"interactive event ideas"

You MUST use search before generating sessions.

===============================
USER CONSTRAINTS
===============================

{constraints}

===============================
MEMORY
===============================

Past events:
{history}

Strategy:
{rl}

===============================
DURATION EXTRACTION
===============================

Extract duration from constraints.

Possible formats:

1 day
3 days
7 days
5 hours
3 hours
12 hours
24h
48h

If missing → default 1 day

===============================
SESSION COUNT RULE
===============================

If duration has days:
4–6 sessions per day

If duration is 1 day:
4–6 total

If duration is hours:
2–4 total

If overnight hackathon:
few sessions + 1 long event

===============================
BALANCE RULE
===============================

Sessions must include mix of:

technical
social
cultural
fun
competition
community
entertainment
talk
show
games
workshop

Do NOT generate only technical.

Do NOT generate many workshops.

Do NOT repeat same type.

Hackathon max 1.

===============================
EVENT TYPE RULE
===============================

Tech → hackathon allowed
Cultural → dance/music/art
Social → games/fun
Business → talks/network
Fest → mix
Sports → matches
Workshop → talk + activity
Seminar → talk + Q&A

===============================
NAMING RULE (STRICT)
===============================

Bad names:

Opening ceremony
Workshop
Session
Competition
Talk
Lunch
Break
Hackathon

Good names:

CodeStorm Arena
Street Games Carnival
Battle of Bands
Innovation Lab
Startup Pitch Clash
Campus Carnival
Fusion Night
Talent Showdown
RoboWar Trials
Community Impact Lab

Names must be unique.
Names must match event type.
Names must sound like real fest events.

===============================
ANTI GENERIC RULE
===============================

Do NOT create generic flow.

Do NOT copy conference template.

Make event feel real.

===============================
OUTPUT JSON ONLY
===============================

Return ONLY JSON.

{{
 "plan_overview": "explain logic",
 "duration": "3 days",
 "event_type": "{event_type}",
 "user_constraints": "{constraints}",
 "sessions": [
  {{
   "name": "Session name",
   "requires_main_stage": true
  }}
 ]
}}
"""

            tasks.append(self._generate_single_branch(prompt, i))

        plans = await asyncio.gather(*tasks)

        return list(plans)