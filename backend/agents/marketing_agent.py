from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, AI_MODEL
from ml_models.engagement_predictor import EngagementPredictor

class MarketingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=AI_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.2 
        )
        # 1. Initialize the ML Model
        self.predictor = EngagementPredictor()

    async def generate_campaign(self, event):
        event_name = event.get('name', 'the upcoming event')
        days_until = event.get('days_until_event', 14) # Default to 14 days out
        
        # 2. Get ML Prediction
        prediction = self.predictor.predict_best_time(days_until)
        best_time_data = self.predictor.predict_best_time(event_data['category'])
        best_time = best_time_data['optimal_hour']
        expected_reach = best_time_data['confidence_score']

        # 2. Inject this into the LLM prompt
        prompt = f"""
        Generate a viral marketing campaign for: {event_data['name']}.
        TECHNICAL CONSTRAINT: Our ML models predict peak engagement at {best_time}:00. 
        The campaign MUST include a post scheduled for this exact time to maximize 
        the expected reach of {expected_reach} users.
        """
        expected_score = prediction["expected_engagement_score"]

        # 3. Inject ML data into the LLM prompt
        prompt = f"""
        Create a social media campaign for {event_name}.
        Include LinkedIn, Twitter and Instagram posts.
        
        CRITICAL DATA: Our Machine Learning model predicts the highest engagement score ({expected_score}) 
        will occur if we release these posts at {best_time}. You MUST explicitly mention this posting strategy 
        and time in your campaign plan.
        """
        response = await self.llm.ainvoke(prompt)
        return response.content