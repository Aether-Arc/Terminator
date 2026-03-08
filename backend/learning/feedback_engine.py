class FeedbackEngine:

    def evaluate(self, state):

        reward = 0

        if state["delay"] < 10:
            reward += 50

        if state["rooms"] >= 5:
            reward += 20

        return reward