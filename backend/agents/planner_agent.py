from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, CLOUD_MODEL
from tools.system_tools import swarm_tools
import json
import asyncio

class PlannerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=CLOUD_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.4 
        )
        
        # 🧠 THE MASSIVE UPGRADE: We bind the tools to the LLM to create a ReAct Agent
        # Note: Your local model MUST support tool calling (like Llama-3.1, Qwen2.5, or OpenAI gpt-4o)
        self.agent_executor = create_react_agent(self.llm, swarm_tools)

    async def _generate_single_branch(self, prompt, i):
        try:
            # Instead of a basic LLM invoke, we trigger the ReAct Cognitive Loop
            # The agent will loop: Thought -> Action (Use Tool) -> Observation -> Final Answer
            response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            
            # Extract the final answer after the agent finishes using tools
            final_text = response["messages"][-1].content
            clean_json = final_text.replace("```json", "").replace("```", "").strip()
            
            plan_data = json.loads(clean_json)
            plan_data["content"] = str(plan_data) 
            return plan_data
        except Exception as e:
            print(f"Agent/Tool Error on branch {i}: {e}")
            return {
                "plan_overview": f"Emergency Contingency Plan Option {i+1}",
                "sessions": [{"name": "Core Phase", "duration_hours": 4, "requires_main_stage": False}],
                "content": "Emergency Fallback"
            }

    async def generate_multiple_plans(self, event_data, count=3):
        event_name = event_data.get('name', 'Hackathon')
        crowd = event_data.get('expected_crowd', 500)
        history = event_data.get("historical_context", "No past data.")
        rl_strategy = event_data.get("learned_strategy", "Prioritize balanced scheduling.")
        
        tasks = []
        for i in range(count):
            # We explicitly instruct the AI to use its tools in the prompt
            prompt = f"""
            You are an elite event architect planning '{event_name}' for {crowd} people.
            
            YOUR MANDATORY DIRECTIVES BEFORE PLANNING:
            1. Use the 'web_search' tool to look up "Current trending topics in technology and AI 2026" and integrate one trend into a session.
            2. Use the 'check_calendar' tool for tomorrow's date to ensure we don't schedule a keynote when the speaker is busy.
            
            🧠 SWARM INTELLIGENCE:
            - Past memory: {history}
            - RL Policy Suggestion: {rl_strategy}
            
            Design a UNIQUE variation (Option {i+1}) of an event plan based on your web research and tool data.
            Break the event down into exactly 5 logical sessions.
            
            Respond ONLY in valid JSON format:
            {{
                "plan_overview": "String describing the vibe and mentioning the web research you did",
                "sessions": [
                    {{"name": "Opening Ceremony", "duration_hours": 1, "requires_main_stage": true}}
                ]
            }}
            """
            tasks.append(self._generate_single_branch(prompt, i))
            
        print(f"[*] Waking up ReAct Agent. Firing {count} sequential planning branches to respect cloud limits...")
        plans = []
        for task in tasks:
            plans.append(await task)
        
        return list(plans)