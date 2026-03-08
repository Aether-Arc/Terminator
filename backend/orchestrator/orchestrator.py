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
        await asyncio.sleep(1) # Pacing for UI
        
        await streamer.broadcast("PlannerAgent", "Generating candidate strategies...", "thinking")
        # Planner makes 3 LLM calls here
        # Planner makes 3 LLM calls asynchronously here
        candidates = await self.planner.generate_multiple_plans(event_data, count=3)
        await asyncio.sleep(1)
        
        best_plan = None
        highest_score = -999
        
        for i, plan in enumerate(candidates):
            await streamer.broadcast("WorldModelAgent", f"Running Physics/Flow Simulation on Plan {i+1}...", "simulating")
            # 1. Evaluate physical crowd bottlenecks
            sim_results = self.world_model.simulate_crowd_flow(event_data, plan)
            await asyncio.sleep(1)
            
            await streamer.broadcast("CriticAgent", f"LLM Evaluating Plan {i+1}...", "thinking")
            
            # API PACING: 2-second delay to ensure we don't hit the 15 RPM burst limit
            await asyncio.sleep(2) 
            
            # 2. Critic LLM evaluates the plan's logic
            critic_review = await self.critic.review(plan.get("content", str(plan)))
            
            # Combine Physical World Score + LLM Critic Score
            combined_score = (sim_results["overall_stability_score"] + critic_review.get("score", 50)) / 2
            
            if combined_score > highest_score:
                highest_score = combined_score
                best_plan = plan
                
        await streamer.broadcast("Orchestrator", f"Optimal plan locked (Score: {highest_score}). Executing...", "success")
        await asyncio.sleep(1)
        
        await streamer.broadcast("SchedulerAgent", "Locking in constraints via OR-Tools...", "thinking")
        # Generate mathematical schedule based on the winning plan
        final_schedule = self.scheduler.create_schedule(best_plan)
        await asyncio.sleep(1)
        
        await streamer.broadcast("MarketingAgent", "Generating engagement copy...", "thinking")
        
        # API PACING: 2-second delay before the final LLM call
        await asyncio.sleep(2) 
        marketing_assets = await self.marketing.generate_campaign(event_data)
        
        # Save decision to memory for future optimization
        self.memory.update_policy(
            state=event_data.get("expected_crowd", 500), 
            action="selected_plan_type", 
            reward=highest_score, 
            next_state="execution"
        )

        await streamer.broadcast("Orchestrator", "All nodes fully operational.", "idle")

        return {
            "workflow_executed": True,
            "selected_plan": best_plan,
            "schedule": final_schedule,
            "marketing": marketing_assets,
            "stability_score": highest_score
        }

    async def handle_crisis(self, crisis_data, streamer):
        # Extract the crisis description from the incoming data
        crisis_desc = crisis_data.get('description', crisis_data.get('type', 'Unknown anomaly detected.'))
        
        await streamer.broadcast("Orchestrator", f"CRISIS DETECTED: {crisis_desc}", "error")
        await asyncio.sleep(1.5)
        
        await streamer.broadcast("CrisisAgent", "Analyzing impact and formulating mitigation...", "thinking")
        
        # In a fully deployed version, you would fetch this from a DB. 
        # For the MVP demo, we provide a mock current schedule state.
        mock_current_schedule = [
            {"session": "Main Keynote", "time": "10:00 AM"},
            {"session": "Hacking Phase 1", "time": "11:00 AM"}
        ]
        
        # 1. LLM calculates the logical fix
        solution = await self.crisis.resolve(crisis_desc, mock_current_schedule)
        await asyncio.sleep(1)
        
        mitigation_text = solution.get('mitigation_strategy', 'Adjusting timeline dynamically.')
        await streamer.broadcast("SchedulerAgent", f"Applying fixes: {mitigation_text}", "simulating")
        
        # 2. Scheduler applies the mathematical time delay
        new_schedule = self.scheduler.recalculate(solution)
        await asyncio.sleep(1.5)
        
        await streamer.broadcast("Orchestrator", "Crisis resolved. Network stabilized.", "success")
        
        return {
            "crisis_injected": crisis_desc, 
            "applied_solution": solution, 
            "new_schedule": new_schedule
        }