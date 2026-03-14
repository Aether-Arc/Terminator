import json
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
from tools.system_tools import swarm_tools
from ml_models.engagement_predictor import EngagementPredictor
from config import get_resilient_llm

class MarketingAgent:
    def __init__(self):
        # Temperature 0.4 allows for creative copywriting while remaining factual
        self.llm = get_resilient_llm(temperature=0.4)
        self.predictor = EngagementPredictor()
        # 🚀 Bind the internet search tools to the marketing agent
        self.agent_executor = create_react_agent(self.llm, swarm_tools)

    async def generate_campaign(self, event_data, specifics):
        event_name = event_data.get('name', 'the upcoming event')
        # Extract broader context so the AI knows WHAT the event actually is
        event_theme = event_data.get('event_type', 'Technology and Innovation')
        event_constraints = event_data.get('user_constraints', 'No specific constraints.')
        days_until = event_data.get('days_until_event', 14)
        
        prediction = self.predictor.predict_best_time(days_until)
        best_time = prediction.get("recommended_post_hour", "12:00")
        expected_score = prediction.get("expected_engagement_score", 0)

        prompt = f"""
        You are an elite Event Marketing Director and Copywriter. Create a viral social media campaign for the event: '{event_name}'.
        
        ===============================
        📅 EVENT CONTEXT
        ===============================
        - Event Name: {event_name}
        - Event Type/Theme: {event_theme}
        - User Constraints/Details: {event_constraints}
        
        SPECIFIC TASK TO GENERATE: {specifics}
        
        ===============================
        🔥 MANDATORY WEB RESEARCH PROTOCOL
        ===============================
        1. 🚫 DO NOT search for generic "Twitter trends" or "LinkedIn trends" (e.g., DO NOT pull in random trending topics like WWE #SmackDown, celebrity gossip, or generic platform advice).
        2. You MUST use the 'web_search' tool to research real, current news, breakthroughs, or trending topics SPECIFICALLY related to the Event Theme ({event_theme}) or the specific topics mentioned in the User Constraints.
        3. Incorporate at least ONE highly relevant, factual piece of industry news or tech trend from your search into the social media copy to make it authoritative and timely.
        
        ===============================
        🤖 ML INTELLIGENCE & DEPLOYMENT
        ===============================
        Our EngagementPredictor forecasts peak virality if the primary announcements are deployed exactly at {best_time}. 
        - Explicitly mention this posting time as an "Internal Deployment Instruction" at the bottom of your response.
        - DO NOT put this internal ML deployment time inside the actual public social media copy.
        
        ===============================
        📝 COPYWRITING RULES
        ===============================
        - NEVER hallucinate unrelated topics. The content MUST strictly relate to {event_name}.
        - The tone should be highly engaging, professional, and hyped, perfectly tailored to the requested format ({specifics}).
        - Keep hashtags highly relevant to the event's actual domain (e.g., #Tech, #Innovation, etc. NEVER use unrelated viral tags).
        """
        
        try:
            print(f"[*] MarketingAgent: Researching industry trends for {event_name}...")
            # 🚀 Execute through the ReAct agent so it can intelligently use the web_search tool
            response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            return response["messages"][-1].content
            
        except Exception as e:
            print(f"[🔥] MarketingAgent Error: {e}")
            return f"Error generating marketing copy: {e}"