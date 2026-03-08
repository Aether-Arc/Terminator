import random

class EventWorldModel:

    def __init__(self):

        self.state = {
            "crowd_size": 500,
            "rooms": 5,
            "speakers": 10,
            "delay": 0
        }

    def clone(self):

        return dict(self.state)

    def simulate_action(self, state, action):

        new_state = dict(state)

        if action == "reschedule":

            new_state["delay"] += random.randint(5,15)

        if action == "add_room":

            new_state["rooms"] += 1

        if action == "replace_speaker":

            new_state["speakers"] += 0

        return new_state