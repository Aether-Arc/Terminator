from langchain.chat_models import ChatOpenAI


class CriticAgent:

    def __init__(self):
        self.llm = ChatOpenAI()

    def review(self, plan):

        prompt = f"""
        Evaluate this event plan.

        Identify problems and suggest improvements.

        {plan}
        """

        return self.llm.predict(prompt)