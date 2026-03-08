from langchain.chat_models import ChatOpenAI


class MarketingAgent:

    def __init__(self):
        self.llm = ChatOpenAI()

    def generate_campaign(self, event):

        prompt = f"""
        Create social media campaign for {event.name}.
        Include LinkedIn, Twitter and Instagram posts.
        """

        return self.llm.predict(prompt)