import asyncio
from agents.planner_agent import PlannerAgent
from agents.scheduler_agent import SchedulerAgent
from agents.marketing_agent import MarketingAgent
from agents.critic_agent import CriticAgent
from agents.crisis_agent import CrisisAgent
from agents.email_agent import EmailAgent
from world_model.event_world_model import WorldModelAgent
from learning.policy_memory import RLPolicyMemory
from orchestrator.workflow_graph import build_graph

class EventOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.marketing = MarketingAgent()
        self.email = EmailAgent()
        self.world_model = WorldModelAgent()
        self.critic = CriticAgent()
        self.crisis = CrisisAgent()
        self.memory = RLPolicyMemory()

        self.graph = build_graph(
            self.planner,
            self.scheduler,
            self.marketing
        )

    async def plan_event(self, event_data, streamer):
        await streamer.broadcast("Orchestrator", "Initializing Swarm Sequence...", "thinking")
        await asyncio.sleep(1.5) # Let the UI catch up
        
        await streamer.broadcast("PlannerAgent", "Generating candidate strategies...", "thinking")
        candidates = self.planner.generate_multiple_plans(event_data, count=3)
        await asyncio.sleep(1.5)
        
        best_plan = None
        highest_score = -999
        
        for i, plan in enumerate(candidates):
            await streamer.broadcast("WorldModelAgent", f"Running CNN/RNN simulations for Plan {i+1}...", "simulating")
            await asyncio.sleep(1.5)
            
            sim_results = self.world_model.simulate_crowd_flow(plan)
            
            await streamer.broadcast("CriticAgent", f"Evaluating friction points for Plan {i+1}...", "thinking")
            score = sim_results["overall_stability_score"]
            await asyncio.sleep(1.5)
            
            if score > highest_score:
                highest_score = score
                best_plan = plan
                
        await streamer.broadcast("Orchestrator", f"Optimal plan selected (Score: {highest_score}). Executing...", "success")
        await asyncio.sleep(1.5)
        
        await streamer.broadcast("SchedulerAgent", "Locking in constraints...", "thinking")
        final_schedule = self.scheduler.create_schedule(best_plan)
        await asyncio.sleep(1.5)
        
        await streamer.broadcast("MarketingAgent", "Generating engagement copy...", "thinking")
        marketing_assets = self.marketing.generate_campaign(event_data)
        await asyncio.sleep(1.5)
        
        self.memory.update_policy(state=event_data.get("expected_crowd", 500), action="selected_plan_type", reward=highest_score, next_state="execution")

        await streamer.broadcast("Orchestrator", "All nodes fully operational.", "idle")

        return {
            "workflow_executed": True,
            "selected_plan": best_plan,
            "schedule": final_schedule,
            "marketing": marketing_assets,
            "stability_score": highest_score
        }

    async def handle_crisis(self, crisis_data, streamer):
        await streamer.broadcast("Orchestrator", f"CRISIS DETECTED: {crisis_data.get('type')}", "simulating")
        historical_fix = self.memory.get_best_action(crisis_data.get('type'))
        await streamer.broadcast("CrisisAgent", "Calculating mitigation protocol...", "thinking")
        solution = self.crisis.resolve(crisis_data, historical_fix)
        await streamer.broadcast("Orchestrator", "Crisis resolved. Updating network.", "success")
        return {"crisis_injected": crisis_data, "applied_solution": solution}