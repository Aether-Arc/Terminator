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
        # 1. Base Agents
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.marketing = MarketingAgent()
        self.email = EmailAgent()
        
        # 2. DeepMind Cognitive Agents
        self.world_model = WorldModelAgent() # Runs the CNN and RNN
        self.critic = CriticAgent()
        self.crisis = CrisisAgent()
        
        # 3. Learning System
        self.memory = RLPolicyMemory()

        # Build execution graph
        self.graph = build_graph(
            self.planner,
            self.scheduler,
            self.marketing
        )

    async def plan_event(self, event_data, streamer):
        """
        DeepMind-style Multi-Agent Reasoning Loop with Live WebSockets
        """
        await streamer.broadcast("Orchestrator", "Initializing Swarm Sequence...", "thinking")
        await asyncio.sleep(1) # UI effect
        
        # Step 1: Generate Candidate Plans (Tree Search)
        await streamer.broadcast("PlannerAgent", "Generating candidate strategies...", "thinking")
        candidates = self.planner.generate_multiple_plans(event_data, count=3)
        
        best_plan = None
        highest_score = -999
        
        # Step 2: World Model Simulation
        for i, plan in enumerate(candidates):
            await streamer.broadcast("WorldModelAgent", f"Running CNN/RNN simulations for Plan {i+1}...", "simulating")
            
            # Simulate physical bottlenecks and time delays
            sim_results = self.world_model.simulate_crowd_flow(plan)
            
            # Step 3: Critic Evaluation
            await streamer.broadcast("CriticAgent", f"Evaluating friction points for Plan {i+1}...", "thinking")
            score = sim_results["overall_stability_score"]
            
            if score > highest_score:
                highest_score = score
                best_plan = plan
                
        await streamer.broadcast("Orchestrator", f"Optimal plan selected (Score: {highest_score}). Executing...", "success")
        
        # Step 4: Execute the winning plan through the standard pipeline
        await streamer.broadcast("SchedulerAgent", "Locking in constraints...", "thinking")
        final_schedule = self.scheduler.create_schedule(best_plan)
        
        await streamer.broadcast("MarketingAgent", "Generating engagement copy...", "thinking")
        marketing_assets = self.marketing.generate_campaign(event_data)
        
        # Step 5: Reinforcement Learning Update
        # The system learns what event parameters yield high stability scores
        self.memory.update_policy(state=event_data["expected_crowd"], action="selected_plan_type", reward=highest_score, next_state="execution")

        await streamer.broadcast("Orchestrator", "All nodes fully operational.", "idle")

        return {
            "workflow_executed": True,
            "selected_plan": best_plan,
            "schedule": final_schedule,
            "marketing": marketing_assets,
            "stability_score": highest_score
        }

    async def handle_crisis(self, crisis_data, streamer):
        """
        Handles live injections from the Chaos Engine
        """
        await streamer.broadcast("Orchestrator", f"CRISIS DETECTED: {crisis_data.get('type')}", "simulating")
        
        # Query RL memory for the best historical fix
        historical_fix = self.memory.get_best_action(crisis_data.get('type'))
        
        await streamer.broadcast("CrisisAgent", "Calculating mitigation protocol...", "thinking")
        solution = self.crisis.resolve(crisis_data, historical_fix)
        
        await streamer.broadcast("Orchestrator", "Crisis resolved. Updating network.", "success")
        
        return {
            "crisis_injected": crisis_data,
            "applied_solution": solution
        }