from agents.planner_agent import PlannerAgent
from agents.scheduler_agent import SchedulerAgent
from agents.marketing_agent import MarketingAgent
from agents.critic_agent import CriticAgent
from agents.crisis_agent import CrisisAgent
from agents.copilot_agent import CopilotAgent
from orchestrator.workflow_graph import build_graph

class EventOrchestrator:

    def __init__(self):

        self.planner=PlannerAgent()
        self.scheduler=SchedulerAgent()
        self.marketing=MarketingAgent()
        self.critic=CriticAgent()
        self.crisis=CrisisAgent()
        self.copilot=CopilotAgent()

        self.graph=build_graph(
            self.planner,
            self.scheduler,
            self.marketing
        )

    async def plan_event(self,event):

        result=self.graph.invoke(event.dict())

        critique=self.critic.review(result)

        return {
            "workflow":result,
            "critic_feedback":critique
        }

    async def handle_crisis(self,data):

        solution=self.crisis.resolve(data)

        return {
            "crisis":data,
            "solution":solution
        }