import json
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent # 🚀 Required for Web Search abilities
from langchain_core.utils.json import parse_json_markdown
from config import CLOUD_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY
from tools.system_tools import swarm_tools # 🚀 Import your tools!
from config import get_resilient_llm
from pydantic import BaseModel, Field
from typing import List

class CardDesign(BaseModel):
    type: str = Field(description="e.g., Countdown, Keynote Spotlight")
    title: str = Field(description="Main bold text")
    subtitle: str = Field(description="Smaller context text")
    body: str = Field(description="The main descriptive text")
    gradient: str = Field(description="Tailwind CSS gradient, e.g., 'from-indigo-50 to-blue-100'")
    platform: str = Field(description="Target platform, e.g., Instagram / LinkedIn")

class DesignOutput(BaseModel):
    cards: List[CardDesign]

class DesignAgent:
    def __init__(self):
        # Temperature 0.5 allows for creative gradients and punchy copywriting
        self.llm = get_resilient_llm(temperature=0.5)
        # 🚀 THE UPGRADE: We bind the web search tools so the agent can browse the internet!
        self.agent_executor = create_react_agent(self.llm, swarm_tools)
        self.formatter_llm = get_resilient_llm(temperature=0).with_structured_output(DesignOutput)

    async def generate_cards(self, event_data, specifics):
        """
        Generates structured JSON representing Social Media Cards (Generative UI).
        """
        event_name = event_data.get("name", "The Event")
        theme = event_data.get("theme", "corporate event")
        location = event_data.get("location", "the venue")
        
        prompt = f"""
        You are an elite Art Director and UI/UX Designer.
        Event Context: {json.dumps(event_data)}
        Task: {specifics}

        🔥 MANDATORY RESEARCH PROTOCOL:
        1. Use the 'web_search' tool FIRST. Search the internet for current visual design trends, buzzwords, or aesthetics related to "{theme} events in {location}".
        2. Incorporate these real-world trends into your design concepts.

        🔥 DESIGN PROTOCOL:
        Design a series of 3 highly engaging "Social Media Cards" for this event.
        Think in terms of visuals: A "T-Minus" hype card, a "Schedule Sneak Peek", and a "Keynote Spotlight".

        Return ONLY a valid JSON array of objects. 
        CRITICAL: We use a CLEAN, ELEGANT LIGHT THEME. Choose beautiful, modern, soft Tailwind gradients for the 'gradient' field. 
        Good examples: "from-blue-50 to-indigo-100", "from-slate-50 to-slate-200", "from-rose-50 to-orange-50", "from-emerald-50 to-teal-100".
        DO NOT use dark gradients like from-slate-900.
        
        Format exactly like this:
        [
            {{
                "type": "Countdown",
                "title": "⏳ 3 Days Left!",
                "subtitle": "Get Ready for {event_name}",
                "body": "The biggest tech summit is almost here. Secure your spot now.",
                "gradient": "from-indigo-50 to-blue-100",
                "platform": "Instagram / LinkedIn"
            }}
        ]
        """
        
        try:
            print(f"[*] DesignAgent: Browsing the web for design inspiration for {event_name}...")
            # 🚀 Use the agent_executor to trigger the internet search loop
            res = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            
            # The bulletproof parser extracts the JSON safely from the final LLM message
            final_text = res["messages"][-1].content
            cards = parse_json_markdown(final_text)
            return cards
            
        except Exception as e:
            print(f"[*] DesignAgent Error: {e}")
            return [{"type": "Error", "title": "Generation Failed", "subtitle": "System", "body": "Could not generate design tokens.", "gradient": "from-red-50 to-orange-100", "platform": "System"}]