from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, AI_MODEL
from ml_models.engagement_predictor import EngagementPredictor

class MarketingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=AI_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.4 # Slightly higher for creative marketing copy
        )
        # Initialize the actual ML Predictor
        self.predictor = EngagementPredictor()

    async def generate_campaign(self, event_data):
        event_name = event_data.get('name', 'the upcoming event')
        days_until = event_data.get('days_until_event', 14)
        
        # 1. Dynamically get ML Predictions
        prediction = self.predictor.predict_best_time(days_until)
        best_time = prediction.get("recommended_post_hour", "12:00")
        expected_score = prediction.get("expected_engagement_score", 0)

        # 2. Inject real ML data into the LLM context
        prompt = f"""
        You are an elite Growth Hacker. Create a viral social media campaign for '{event_name}'.
        Include specific copy for LinkedIn, Twitter, and Instagram.
        
        CRITICAL ML INTELLIGENCE: Our EngagementPredictor model forecasts peak virality (Score: {expected_score}/200) 
        if the primary announcements are deployed exactly at {best_time}. 
        
        You MUST explicitly build the timeline around this posting strategy and mention the time in your internal plan.
        """
        response = await self.llm.ainvoke(prompt)
        return response.content