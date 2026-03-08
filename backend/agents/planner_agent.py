from langchain.chat_models import ChatOpenAI

class PlannerAgent:
    def __init__(self):
        self.llm = ChatOpenAI()

    def generate_plan(self, event):
        # Existing single plan logic
        prompt = f"Design an event plan for {event.get('name')}..."
        return self.llm.predict(prompt)

    def generate_multiple_plans(self, event_data, count=3):
        """NEW: Allows the Reasoning Loop to function"""
        plans = []
        for i in range(count):
            # We add a slight variation to the prompt to get different candidates
            prompt = f"Design a unique version (Option {i+1}) of an event plan for {event_data.get('name')}."
            plans.append({"id": i, "content": self.llm.predict(prompt)})
        return plans