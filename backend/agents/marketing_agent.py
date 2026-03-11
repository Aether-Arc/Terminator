# REMOVE THIS:
# from langchain_google_genai import ChatGoogleGenerativeAI

# ADD THIS:
from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, AI_MODEL

class MarketingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=AI_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.2 # Crucial: Keep this low so Gemma outputs strict JSON
        )

    async def generate_campaign(self, event):
        event_name = event.get('name', 'the upcoming event')
        prompt = f"""
        Create social media campaign for {event_name}.
        Include LinkedIn, Twitter and Instagram posts.
        """
        response = await self.llm.ainvoke(prompt)
        return response.content