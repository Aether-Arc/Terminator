from langchain.chat_models import ChatOpenAI


class CopilotAgent:

    def __init__(self):
        self.llm = ChatOpenAI()

    def answer(self, question, context):

        prompt = f"""
        Context: {context}

        Question: {question}

        Provide a helpful answer.
        """

        return self.llm.predict(prompt)