import json
import random
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from config import get_resilient_llm


# =========================
# MEMORY FILE
# =========================

MEMORY_FILE = "schedule_memory.json"


def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem[-5:], f, indent=2)  # keep last 5 schedules


# =========================
# PYDANTIC
# =========================

class ScheduledSession(BaseModel):
    session: str = Field(description="The actual name of the event/session (e.g., 'Opening Keynote', 'Hackathon Start'). DO NOT put the day here.")
    time: str = Field(description="The day and time formatted EXACTLY as: 'Day X | HH:MM AM - HH:MM PM'")
    status: str = "Locked"

class EventSchedule(BaseModel):
    schedule: List[ScheduledSession]


# =========================
# SCHEDULER
# =========================

class SchedulerAgent:

    def __init__(self):
        self.llm = get_resilient_llm(
            temperature=0.35  # randomness for variation
        ).with_structured_output(EventSchedule)

    # =========================
    # DAY TEMPLATE GENERATOR
    # =========================

    def get_day_template(self):

        templates = [

            "competition + fun + show",

            "talk + competition + cultural",

            "games + workshop + concert",

            "tech + social + entertainment",

            "community + challenge + show",

            "sports + tech + music",

            "creative + competition + social",

        ]

        return random.choice(templates)

    # =========================
    # MAIN
    # =========================

    async def create_schedule(self, best_plan):

        sessions = best_plan.get("sessions", [])
        session_names = [s["name"] for s in sessions]

        duration = best_plan.get("duration", "1 day")
        constraints = best_plan.get("user_constraints", "")
        event_type = best_plan.get("event_type", "festival")

        memory = load_memory()

        context = (str(session_names) + str(duration)).lower()

        # ----------------------
        # overnight detection
        # ----------------------

        is_overnight = (
            "hackathon" in context
            and ("24h" in context or "48h" in context or "overnight" in context)
        )

        # ----------------------
        # day template
        # ----------------------

        template = self.get_day_template()

        # ----------------------
        # time rules
        # ----------------------

        if is_overnight:

            time_rules = f"""
Continuous hackathon allowed.

Sessions may cross midnight.

Still must add:
Lunch
Dinner
Energy break
Sleep break

Do not spam hackathon.
Only one long hackathon allowed.
"""

        else:

            time_rules = f"""
STRICT FESTIVAL RULES

Allowed time per day:
9:00 AM → 8:30 PM

NO session outside this.

Add daily:

Lunch ~1 PM
Tea ~4:30 PM
Dinner ~7 PM optional

Session limits:

normal 1–2h
competition 2–3h
show max 3h
talk 1–2h
break 30–60m

Each day must feel like festival.
"""

        # ----------------------
        # memory text
        # ----------------------

        memory_text = json.dumps(memory[-2:], indent=2)

        # ----------------------
        # prompt
        # ----------------------

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are ELITE FESTIVAL SCHEDULER AI.

Create realistic college fest schedules like:

Mood Indigo
Techfest IIT
NIT fests
College cultural fests

RULES:

{time_rules}

EVENT TYPE:
{event_type}

DAY TEMPLATE:
{template}

MEMORY OF OLD SCHEDULES:
{memory}

==========================
FESTIVAL STRUCTURE
==========================

Each day must include mix:

competition
fun
cultural
social
show
break

No generic template.

Do NOT repeat same pattern as memory.

Do NOT spam hackathon.

Do NOT spam break.

Keep planner names EXACT.

Add your own break names only.

Examples of good breaks:

Networking Lunch
Tea Recharge
Evening Chill Break
Dinner Connect

==========================
FORMAT

Day X | 9:00 AM - 10:30 AM

No overlaps.
No midnight unless hackathon.
No empty days.

Return structured only.
"""
                ),
                (
                    "user",
                    """
Duration:
{duration}

Sessions:
{sessions}

User constraints:
{constraints}
"""
                ),
            ]
        )

        chain = prompt | self.llm

        result: EventSchedule = await chain.ainvoke(
            {
                "sessions": ", ".join(session_names),
                "duration": duration,
                "constraints": constraints,
                "time_rules": time_rules,
                "template": template,
                "memory": memory_text,
                "event_type": event_type,
            }
        )

        schedule = [s.model_dump() for s in result.schedule]

        memory.append(schedule)
        save_memory(memory)

        return schedule