import sqlite3
import json
import os

class RLPolicyMemory:
    def __init__(self, learning_rate=0.1, discount_factor=0.9):
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.db_path = os.path.join(os.getcwd(), "memory", "rl_policy.db")
        self._init_db()

    def _init_db(self):
        """Creates an async-safe SQLite database for the Q-Table."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS q_table
                            (state TEXT PRIMARY KEY, actions TEXT)''')
            conn.commit()

    def _get_state_actions(self, state_key):
        """Fetches the available actions and their Q-values for a given state."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT actions FROM q_table WHERE state=?", (state_key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return {}

    def _save_state_actions(self, state_key, actions_dict):
        """Saves the updated Q-values back to the database safely."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO q_table (state, actions) VALUES (?, ?)", 
                         (state_key, json.dumps(actions_dict)))
            conn.commit()

    def get_best_action(self, state):
        """Returns the action with the highest Q-value for a given crisis state."""
        state_key = str(state)
        actions = self._get_state_actions(state_key)
        
        if not actions:
            return None # Requires exploration
            
        return max(actions, key=actions.get)

    def update_policy(self, state, action, reward, next_state):
        """Updates the Q-table using the Bellman Equation based on the Critic's reward."""
        state_key = str(state)
        next_state_key = str(next_state)
        action_key = str(action)

        current_actions = self._get_state_actions(state_key)
        next_actions = self._get_state_actions(next_state_key)

        # Max Q for next state
        max_next_q = max(next_actions.values()) if next_actions else 0.0
        current_q = current_actions.get(action_key, 0.0)

        # Bellman Equation Update
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        
        current_actions[action_key] = new_q
        self._save_state_actions(state_key, current_actions)
        
        return new_q