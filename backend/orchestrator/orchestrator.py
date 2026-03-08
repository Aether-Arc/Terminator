from agents.planner_agent import PlannerAgent
from agents.scheduler_agent import SchedulerAgent
from agents.marketing_agent import MarketingAgent
from agents.critic_agent import CriticAgent
from orchestrator.workflow_graph import build_graph


class EventOrchestrator:

    def __init__(self):

        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.marketing = MarketingAgent()
        self.critic = CriticAgent()

        self.graph = build_graph(
            self.planner,
            self.scheduler,
            self.marketing
        )

    async def plan_event(self, event):

        result = self.graph.invoke(event.dict())

        critique = self.critic.review(result)

        return {
            "plan": result,
            "critic_feedback": critique
        }

    async def handle_crisis(self, crisis):

        return {"crisis": crisis}