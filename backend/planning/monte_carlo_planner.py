import random

class MonteCarloPlanner:

    def __init__(self, world_model):

        self.world_model = world_model

    def evaluate_state(self, state):

        score = 100

        score -= state["delay"] * 2
        score -= abs(500 - state["crowd_size"]) * 0.1

        return score

    def plan(self, actions, simulations=50):

        best_action = None
        best_score = -999

        for action in actions:

            total_score = 0

            for _ in range(simulations):

                state = self.world_model.clone()

                new_state = self.world_model.simulate_action(state, action)

                score = self.evaluate_state(new_state)

                total_score += score

            avg_score = total_score / simulations

            if avg_score > best_score:

                best_score = avg_score
                best_action = action

        return best_action