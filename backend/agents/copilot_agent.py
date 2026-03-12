# REMOVE THIS:
# from langchain_google_genai import ChatGoogleGenerativeAI

# ADD THIS:
from langchain_openai import ChatOpenAI
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL

class CopilotAgent:

    def __init__(self):
        self.llm = ChatOpenAI(
            model=LOCAL_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key=OPENAI_API_KEY,
            temperature=0.2 # Crucial: Keep this low so Gemma outputs strict JSON
        )

    def answer(self, question, context):

        prompt = f"""
        Context: {context}

        Question: {question}

        Provide a helpful answer.
        """

        return self.llm.predict(prompt)