from langchain_google_genai import ChatGoogleGenerativeAI

class MarketingAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    async def generate_campaign(self, event):
        event_name = event.get('name', 'the upcoming event')
        prompt = f"""
        Create social media campaign for {event_name}.
        Include LinkedIn, Twitter and Instagram posts.
        """
        response = await self.llm.ainvoke(prompt)
        return response.content