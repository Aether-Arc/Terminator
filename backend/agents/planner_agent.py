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

    async def generate_multiple_plans(self, event_data, count=1):
        event_name = event_data.get('name', 'Hackathon')
        crowd = event_data.get('expected_crowd', 500)
        history = event_data.get("historical_context", "No past data.")
        rl_strategy = event_data.get("learned_strategy", "Prioritize balanced scheduling.")
        
        # FIX 1: Extract the new constraints we injected from the orchestrator
        user_constraints = event_data.get("user_constraints", "None")
        
        tasks = []
        for i in range(count):
            prompt = f"""
            You are an elite, highly adaptable event architect, planning '{event_name}' for {crowd} people.
            
            🔥 CRITICAL USER CONSTRAINTS (OBEY STRICTLY):
            {user_constraints}
            
            🧠 SWARM INTELLIGENCE & PAST MEMORY:
            - Past memory: {history}
            - RL Policy Suggestion: {rl_strategy}
            
            Design a highly realistic schedule that PERFECTLY adapts to the user's specific constraints.
            
            DYNAMIC SCHEDULING RULES & FALLBACK PROTOCOLS:
            1. DURATION: Analyze the constraints to determine the exact length of the event. 
               -> ⚠️ FALLBACK: If the user constraints are vague or DO NOT mention a specific time/duration, you MUST use your own judgment based on the event name. 
               (e.g., Default to a standard 1-day, 6-hour schedule for generic events. Default to 24-48 hours for a 'hackathon'. Default to 2 hours for a 'keynote').
            2. BREAKS: Add logical human breaks (lunch, sleep, networking) ONLY IF they make sense for the duration. (e.g., A 2-hour event does not need a lunch break. A full-day event MUST have a lunch break).
            3. FLEXIBILITY: Generate as many (or as few) sessions as necessary to fulfill the prompt. Ensure the start_time and end_time flow logically and sequentially.
            
            Respond ONLY in valid JSON format exactly like this structure:
            {{
                "plan_overview": "Explain your logic. If the prompt was vague, state the default assumptions you made regarding duration and structure.",
                "sessions": [
                    {{"name": "Opening Brief", "day": 1, "start_time": "09:00 AM", "end_time": "09:30 AM", "requires_main_stage": true}},
                    {{"name": "Core Activity", "day": 1, "start_time": "09:30 AM", "end_time": "02:00 PM", "requires_main_stage": false}}
                ]
            }}
            
            """
            tasks.append(self._generate_single_branch(prompt, i))
            
        print(f"[*] Waking up ReAct Agent. Firing {count} parallel planning branches...")
        
        # FIX 2: Run all branches concurrently instead of sequentially for better speed
        plans = await asyncio.gather(*tasks)
        
        return list(plans)