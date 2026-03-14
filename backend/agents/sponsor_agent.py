import json
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.system_tools import swarm_tools
from config import get_resilient_llm

class SponsorTier(BaseModel):
    name: str = Field(description="Name of the tier (e.g., Title, Gold, Silver)")
    price: str = Field(description="Estimated price (e.g., $10,000 or INR 5,00,000)")
    perks: str = Field(description="List of key benefits for the sponsor")

class TargetSponsor(BaseModel):
    company: str = Field(description="Real-world company name")
    pitch: str = Field(description="A highly customized 1-sentence pitch for this company")

class SponsorOutput(BaseModel):
    pitch_subject: str = Field(description="Catchy email subject line for the sponsorship pitch")
    pitch_body: str = Field(description="A short, persuasive 2-paragraph email body to send to sponsors")
    tiers: List[SponsorTier] = Field(description="3 tailored sponsorship tiers")
    target_sponsors: List[TargetSponsor] = Field(description="3 specific real-world companies to target")

class SponsorAgent:
    def __init__(self):
        self.llm = get_resilient_llm(temperature=0.5)
        # Agent for live web research
        self.agent_executor = create_react_agent(self.llm, swarm_tools)
        # Formatter to guarantee perfect dictionary output
        self.formatter_llm = get_resilient_llm(temperature=0).with_structured_output(SponsorOutput)

    async def draft_sponsorships(self, event_data, specifics):
        event_name = event_data.get("name", "Event")
        theme = event_data.get("event_type", "General") 
        crowd_size = event_data.get("expected_crowd", 500)

        # 🚀 STEP 1: Let the React Agent do the live web research
        research_prompt = f"""
You are researching sponsorship strategy for an event.

Event: {event_name}
Type: {theme}
Expected crowd: {crowd_size}

Task:
{specifics}

===============================
MANDATORY WEB SEARCH LOOP
===============================

You MUST use web_search.

Search multiple times.

Find:

companies sponsoring {theme} events
brands sponsoring college fests
event sponsorship price range
sponsorship packages examples
brands targeting young audience
brands marketing in this industry

Use real companies only.

Do NOT invent companies.

===============================
EVENT TYPE MATCHING
===============================

Tech → IT, startups, electronics
Cultural → music, fashion, media
Social → FMCG, food, apps
Sports → sports brands
Business → banks, fintech
Fest → mix of brands
Workshop → education, tools
Music → audio, streaming, lifestyle

Sponsors must match event type.

===============================
CROWD SIZE LOGIC
===============================

Small event → small sponsors
Large event → big sponsors

Use crowd to estimate sponsor value.

===============================
PRICING RESEARCH
===============================

Search real prices.

Search:

event sponsorship cost
college fest sponsorship price
brand activation cost
event branding cost

Collect realistic ranges.

Return research notes.
"""
        
        try:
            print("[*] SponsorAgent: Conducting live web research...")
            research_response = await self.agent_executor.ainvoke({"messages": [("user", research_prompt)]})
            research_data = research_response["messages"][-1].content

            # 🚀 STEP 2: Force the research into perfect JSON using the Formatter LLM
            print("[*] SponsorAgent: Formatting pitch deck...")
            format_prompt = f"""
Use this research:

{research_data}

Create a professional sponsorship deck.

Event: {event_name}
Type: {theme}
Crowd: {crowd_size}

===============================
TIER RULES
===============================

Create 3 tiers:

Title Sponsor
Gold Sponsor
Silver Sponsor

Rules:

Title = highest price
Gold = medium
Silver = low

Prices must scale with crowd.

Example:

500 people → small
2000 → medium
5000+ → large

Use realistic currency.

===============================
PERKS RULE
===============================

Title:
main banner
stage branding
naming rights

Gold:
logo
stall
ads

Silver:
logo
mention

===============================
TARGET SPONSORS RULE
===============================

Pick real companies.

Must match event type.

Tech → Google, Nvidia, Infosys
Cultural → Spotify, Nike, RedBull
Social → CocaCola, Zomato
Business → HDFC, Deloitte
Sports → Adidas, Puma
Fest → mix

No fake companies.

===============================
EMAIL RULE
===============================

Write real sponsor email.

2 paragraphs.

Professional + exciting.

Mention:

audience
reach
branding
benefits

===============================
OUTPUT STRICTLY SCHEMA
===============================
"""
            
            result: SponsorOutput = await self.formatter_llm.ainvoke(format_prompt)
            return result.model_dump()
            
        except Exception as e:
            print(f"[❌] Sponsor Agent Error: {e}")
            # Bulletproof fallback matching the exact schema
            return {
                "pitch_subject": f"Sponsorship Opportunity: {event_name}",
                "pitch_body": "We invite you to sponsor our upcoming event...",
                "tiers": [{"name": "Standard", "price": "$1000", "perks": "Logo on website"}], 
                "target_sponsors": [{"company": "Local Business", "pitch": "Connect with our audience."}]
            }