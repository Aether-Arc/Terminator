from langchain_google_genai import ChatGoogleGenerativeAI

class PlannerAgent:
    def __init__(self):
        # Swapped to Gemini 1.5 Flash for free, high-speed generation
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    def generate_plan(self, event):
        event_name = event_data.get('event_name', 'Neurathon 2026')
        prompt = f"Design an event plan for {event_name}..."
        return self.llm.invoke(prompt).content

    def generate_multiple_plans(self, event_data, count=3):
        plans = []
        for i in range(count):
            prompt = f"Design a unique version (Option {i+1}) of an event plan for {event_data.get('name')}."
            response = self.llm.invoke(prompt)
            plans.append({"id": i, "content": response.content})
        return plans