from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
from tools.system_tools import swarm_tools
from ml_models.engagement_predictor import EngagementPredictor

class MarketingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LOCAL_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.4
        )
        self.predictor = EngagementPredictor()
        # 🚀 Bind the internet search tools to the marketing agent
        self.agent_executor = create_react_agent(self.llm, swarm_tools)

    async def generate_campaign(self, event_data, specifics):
        event_name = event_data.get('name', 'the upcoming event')
        days_until = event_data.get('days_until_event', 14)
        
        prediction = self.predictor.predict_best_time(days_until)
        best_time = prediction.get("recommended_post_hour", "12:00")
        expected_score = prediction.get("expected_engagement_score", 0)

        prompt = f"""
        You are an elite Growth Hacker. Create a viral social media campaign for '{event_name}'.
        
        SPECIFIC TASK: {specifics}
        
        MANDATORY TOOL USE: 
        Before writing the copy, use the 'web_search' tool to research current viral trends, news, or popular hashtags related to this specific task. 
        Incorporate at least ONE real, current fact or trending topic from your search into the social media copy.
        
        CRITICAL ML INTELLIGENCE: Our EngagementPredictor forecasts peak virality 
        if the primary announcements are deployed exactly at {best_time}. 
        Explicitly mention this posting time in your internal plan.
        """
        
        # 🚀 Execute through the ReAct agent so it can use tools
        response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
        return response["messages"][-1].content