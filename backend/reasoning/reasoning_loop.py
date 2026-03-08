class ReasoningLoop:

    def __init__(self, planner, strategy):

        self.planner = planner
        self.strategy = strategy

    def solve(self, crisis):

        actions = self.strategy.generate(crisis)

        best_action = self.planner.plan(actions)

        return best_action