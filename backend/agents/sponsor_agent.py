from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
from tools.system_tools import swarm_tools
import json
from config import get_resilient_llm

class SponsorAgent:
    def __init__(self):
        self.llm = get_resilient_llm(temperature=0.5)
        self.agent_executor = create_react_agent(self.llm, swarm_tools)

    # ADDED 'specifics' parameter
    async def draft_sponsorships(self, event_data, specifics):
        event_name = event_data.get("name", "Tech Event")
        theme = event_data.get("marketing_prompt", "Technology")
        crowd_size = event_data.get("expected_crowd", 500)

        prompt = f"""
        You are the Head of Corporate Partnerships for '{event_name}', a {theme} event with {crowd_size} attendees.
        
        SPECIFIC TASK: {specifics}
        
        MANDATORY TOOL USE:
        Use the 'web_search' tool to find "companies currently sponsoring {theme} hackathons and conferences in 2026".
        
        Based on your live research, generate 3 sponsorship tiers (e.g., Title, Gold, Silver) and identify 3 specific real-world companies to target, including a custom 1-sentence pitch for why they should sponsor this specific crowd.
        
        Respond ONLY in valid JSON format:
        {{
            "tiers": [{{"name": "Gold", "price": "$5,000", "perks": "Booth + Keynote"}}],
            "target_sponsors": [{{"company": "Google", "pitch": "Access to 500 top AI developers."}}]
        }}
        """
        try:
            response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            clean_json = response["messages"][-1].content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Sponsor Agent Error: {e}")
            return {"tiers": [{"name": "Standard", "price": "$1000", "perks": "Logo on website"}], "target_sponsors": []}