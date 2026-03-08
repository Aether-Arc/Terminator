import numpy as np
import json
import os

class RLPolicyMemory:
    def __init__(self, learning_rate=0.1, discount_factor=0.9):
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.q_table = {} # State-Action value mapping
        self.memory_file = "memory/q_table.json"
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                self.q_table = json.load(f)

    def _save_memory(self):
        # Ensure the memory directory exists
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.q_table, f)

    def get_best_action(self, state):
        """Returns the action with the highest Q-value for a given crisis state."""
        state_key = str(state)
        if state_key not in self.q_table or not self.q_table[state_key]:
            return None # Requires exploration
        return max(self.q_table[state_key], key=self.q_table[state_key].get)

    def update_policy(self, state, action, reward, next_state):
        """Updates the Q-table based on the Critic's reward."""
        state_key = str(state)
        next_state_key = str(next_state)
        action_key = str(action)

        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        if action_key not in self.q_table[state_key]:
            self.q_table[state_key][action_key] = 0.0

        # Max Q for next state
        max_next_q = 0.0
        if next_state_key in self.q_table and self.q_table[next_state_key]:
            max_next_q = max(self.q_table[next_state_key].values())

        # Bellman Equation Update
        current_q = self.q_table[state_key][action_key]
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        
        self.q_table[state_key][action_key] = new_q
        self._save_memory()
        
        return new_q