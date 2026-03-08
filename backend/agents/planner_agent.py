from langchain.chat_models import ChatOpenAI


class PlannerAgent:

    def __init__(self):
        self.llm = ChatOpenAI()

    def generate_plan(self, event):

        prompt = f"""
        Design an event plan for {event.name}.
        Venue: {event.venue}
        Tracks: {event.tracks}
        Speakers: {event.speakers}

        Return sessions, workshops and panels.
        """

        response = self.llm.predict(prompt)

        return response