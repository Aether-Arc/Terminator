import json

class PolicyMemory:

    def __init__(self):

        self.memory = []

    def store(self, crisis, action, reward):

        self.memory.append({
            "crisis": crisis,
            "action": action,
            "reward": reward
        })

    def get_history(self):

        return self.memory