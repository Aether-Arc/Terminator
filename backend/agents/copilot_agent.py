# REMOVE THIS:
# from langchain_google_genai import ChatGoogleGenerativeAI

# ADD THIS:
from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
from config import get_resilient_llm

class CopilotAgent:

    def __init__(self):
        self.llm = get_resilient_llm(temperature=0.2)

    def answer(self, question, context):

        prompt = f"""
        Context: {context}

        Question: {question}

        Provide a helpful answer.
        """

        return self.llm.predict(prompt)