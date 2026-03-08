from langchain_google_genai import ChatGoogleGenerativeAI

class CriticAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    def review(self, plan):
        prompt = f"""
        Evaluate this event plan.
        Identify problems and suggest improvements.

        {plan}
        """
        return self.llm.invoke(prompt).content