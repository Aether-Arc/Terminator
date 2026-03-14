import json
import asyncio
import re
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.utils.json import parse_json_markdown

from config import OLLAMA_BASE_URL, OPENAI_API_KEY, CLOUD_MODEL, get_resilient_llm
from tools.system_tools import swarm_tools

class PlannerAgent:
    def __init__(self):
        self.llm = get_resilient_llm(temperature=0.4)
        # ReAct agent with tools
        self.agent_executor = create_react_agent(self.llm, swarm_tools)

    # ============================================
    # SINGLE BRANCH
    # ============================================
    async def _generate_single_branch(self, prompt, i):
        try:
            response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            final_text = response["messages"][-1].content

            # ---------- CLEAN JSON ----------
            clean_text = final_text.replace("```json", "").replace("```", "").strip()
            match = re.search(r"\{.*\}", clean_text, re.DOTALL)

            if not match:
                raise ValueError("No JSON found")

            json_text = match.group(0)
            plan_data = parse_json_markdown(json_text)
            plan_data["content"] = str(plan_data)
            return plan_data

        except Exception as e:
            print(f"Planner Error branch {i}: {e}")
            return {
                "plan_overview": f"Fallback Plan {i+1}",
                "duration": "1 day",
                "sessions": [
                    {
                        "name": "Emergency Core Phase",
                        "requires_main_stage": False
                    }
                ],
                "content": "Fallback"
            }

    # ============================================
    # MULTIPLE PLANS
    # ============================================
    async def generate_multiple_plans(self, event_data, count=1):
        event_name = event_data.get("name", "Event")
        crowd = event_data.get("expected_crowd", 100)
        history = event_data.get("historical_context", "No past data.")
        rl_strategy = event_data.get("learned_strategy", "Prioritize balanced scheduling.")
        user_constraints = event_data.get("user_constraints", "None")
        event_type = event_data.get("event_type", "general")

        tasks = []

        for i in range(count):
            prompt = f"""
                You are an ELITE GLOBAL EVENT ARCHITECT AI.

                You design world-class, immersive, modern events using real internet trends,
                real audience psychology, and real event formats.

                Event name: "{event_name}"
                Expected crowd: {crowd}
                EVENT TYPE: {event_type}

                ===============================
                🔥 MANDATORY WEB INTELLIGENCE
                ===============================
                You MUST use the web_search tool BEFORE generating sessions.
                Search queries should include: 
                "{event_name} event format"
                "{event_name} interactive ideas"
                "modern event engagement ideas"

                You MUST analyze the search results. DO NOT generate sessions until web search is done.

                ===============================
                🔥 USER CONSTRAINTS (STRICT)
                ===============================
                {user_constraints}

                ===============================
                🧠 SWARM MEMORY
                ===============================
                Past events: {history}
                RL Strategy: {rl_strategy}

                ===============================
                ⏱ DURATION EXTRACTION & AWARENESS
                ===============================
                Analyze the USER CONSTRAINTS above. Extract the intended duration (e.g., "3 days", "24 hours", "1 week").
                If the user does not specify a duration, default to "1 day".
                
                CRITICAL: You MUST generate enough sessions to fill the entire duration you extracted! 
                If the event is 3 days, you must generate enough distinct, interactive sessions to fill 3 whole days.

                ===============================
                🎯 DESIGN GOAL & NAMING RULES
                ===============================
                Create the most engaging, modern, non-boring event possible.
                
                DO NOT USE GENERIC NAMES: "Opening speech", "Keynote", "Lunch", "Break", "Session 1", "Hackathon", "Workshop".
                Every single name must be thematic, immersive, and interactive!

                Examples:
                Lunch → Neural Networking Banquet
                Break → Quantum Recharge Interval
                Talk → Fireside Chat: Future of AGI
                Workshop → Interactive Lab: Autonomous Agents
                Panel → Roundtable: AI Ethics War Room

                Use modern formats: lightning talks, live coding battles, speed mentoring, interactive labs, etc.

                ===============================
                📦 OUTPUT FORMAT (STRICT JSON)
                ===============================
                Escape quotes using \\"
                Return ONLY JSON. DO NOT create times. Only generate sessions.

                {{
                    "plan_overview": "Explain creative logic, trends from web search, and why this event will be engaging.",
                    "duration": "3 days", 
                    "sessions": [
                        {{
                            "name": "Ignition Sequence: Welcome Protocol",
                            "requires_main_stage": true
                        }},
                        {{
                            "name": "Interactive Lab: Building Autonomous Swarms",
                            "requires_main_stage": false
                        }}
                    ]
                }}
            """
            tasks.append(self._generate_single_branch(prompt, i))

        plans = await asyncio.gather(*tasks)
        return list(plans)