from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, CLOUD_MODEL
from tools.system_tools import swarm_tools
from langchain_core.utils.json import parse_json_markdown
import json
import asyncio
import re
from config import get_resilient_llm

class PlannerAgent:
    def __init__(self):
        self.llm = get_resilient_llm(temperature=0.4)
        
        # This wrapper gives Llama 3.1 the ability to Web Scrape!
        self.agent_executor = create_react_agent(self.llm, swarm_tools)

    async def _generate_single_branch(self, prompt, i):
        try:
            # 1. Trigger the ReAct Cognitive Loop
            response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            final_text = response["messages"][-1].content
            
            # 2. BULLETPROOF JSON EXTRACTOR
            # Clean markdown code blocks if the LLM wrapped the output
            clean_text = final_text.replace("```json", "").replace("```", "").strip()
            
            # Extract everything from the first '{' to the last '}'
            match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            
            if not match:
                raise ValueError("No JSON object found in LLM response.")
                
            clean_json_string = match.group(0)
            
            # strict=False allows unescaped control characters (like newlines) inside strings
            plan_data = parse_json_markdown(final_text)
            plan_data["content"] = str(plan_data) 
            return plan_data
            
        except Exception as e:
            print(f"Agent/Tool Error on branch {i}: {e}")
            return {
                "plan_overview": f"Emergency Contingency Plan Option {i+1}. The AI failed to output strictly valid JSON.",
                "sessions": [
                    {"name": "Emergency Core Phase", "day": 1, "start_time": "10:00 AM", "end_time": "02:00 PM", "requires_main_stage": False}
                ],
                "content": "Emergency Fallback"
            }

    async def generate_multiple_plans(self, event_data, count=1): 
        event_name = event_data.get('name', 'Event')
        crowd = event_data.get('expected_crowd', 100)
        history = event_data.get("historical_context", "No past data.")
        rl_strategy = event_data.get("learned_strategy", "Prioritize balanced scheduling.")
        user_constraints = event_data.get("user_constraints", "None")
        
        tasks = []
        for i in range(count):
            prompt = f"""
            You are an elite, highly adaptable event architect planning '{event_name}' for {crowd} people.
            
            🔥 MANDATORY TOOL PROTOCOL:
            You MUST use the 'web_search' tool right now to search the internet for context about "{event_name}" or its underlying theme.
            DO NOT generate the schedule until you have read the web search results.
            
            🔥 CRITICAL USER CONSTRAINTS (OBEY STRICTLY):
            {user_constraints}
            
            🧠 SWARM INTELLIGENCE & PAST MEMORY:
            - Past memory: {history}
            - RL Policy Suggestion: {rl_strategy}
            
            Design a highly realistic schedule that PERFECTLY adapts to the user's specific constraints and your web research.
            
            DYNAMIC SCHEDULING RULES & FALLBACK PROTOCOLS:
            1. DURATION: Analyze the constraints to determine the exact length of the event. 
               -> ⚠️ FALLBACK: If constraints are vague, default to standard times (e.g., 24-48 hours for a 'hackathon', 1-day for a conference).
            2. BREAKS: Add logical human breaks (lunch, sleep, networking) ONLY IF they make sense for the duration.
            3. FLEXIBILITY: Generate as many (or as few) sessions as necessary to fulfill the prompt.
            
            Respond ONLY in valid JSON format exactly like this structure:
            CRITICAL RULE: Escape all double quotes inside your text values using a backslash (e.g., \\"). 
            {{
                "plan_overview": "Explain your logic. Include what you learned from the web search.",
                "sessions": [
                    {{"name": "Opening Brief", "day": 1, "start_time": "09:00 AM", "end_time": "09:30 AM", "requires_main_stage": true}}
                ]
            }}
            """
            tasks.append(self._generate_single_branch(prompt, i))
            
        plans = await asyncio.gather(*tasks)
        return list(plans)