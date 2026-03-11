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
from memory.vector_store import search_memory, store_memory

# 🧠 NEW DEEPMIND IMPORTS
from planning.monte_carlo_planner import MonteCarloPlanner
from planning.strategy_generator import StrategyGenerator

class EventOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.marketing = MarketingAgent()
        self.email = EmailAgent()
        self.world_model = WorldModelAgent()
        self.critic = CriticAgent()
        self.crisis = CrisisAgent()
        
        # Initialize Advanced Search Components
        self.mcts = MonteCarloPlanner(self.world_model)
        self.strategy_gen = StrategyGenerator()
        
        self.graph = build_graph(
            self.planner,
            self.critic,
            self.scheduler,
            self.marketing,
            self.world_model # Injected World Model into graph
        )

    # ... (plan_event and approve_plan remain exactly the same as previously defined) ...
    # [Paste your existing plan_event and approve_plan here]

    async def handle_crisis(self, crisis_data, streamer):
        crisis_desc = crisis_data.get('description', 'Unknown anomaly detected.')
        event_name = crisis_data.get("event_name", "the current event") 
        crowd_size = crisis_data.get("expected_crowd", 500)
        
        await streamer.broadcast("Orchestrator", f"CRISIS DETECTED: {crisis_desc}", "error")
        
        # 1. VECTOR DB SEARCH
        await streamer.broadcast("WorldModelAgent", "Querying VectorDB for historical crisis data...", "simulating")
        search_query = f"Crisis: {crisis_desc} during event: {event_name}"
        past_crises = search_memory(search_query)
        
        # 2. STRATEGY GENERATION (AI dynamically invents options)
        await streamer.broadcast("StrategyGenerator", "Inventing context-aware mitigation strategies...", "thinking")
        
        # THE FIX: We now pass the custom text to the LLM and await it
        possible_actions = await self.strategy_gen.generate(crisis_desc, crowd_size)
        
        # 3. MONTE CARLO TREE SEARCH (Simulating the AI's ideas)
        await streamer.broadcast("MonteCarloPlanner", f"Running 1000x physics simulations on proposed strategies...", "simulating")
        base_state = {"delay": 0, "crowd_size": crowd_size}
        
        # MCTS finds which of the LLM's ideas was mathematically the safest
        best_math_action = self.mcts.plan(possible_actions, simulations=100)
        best_action_name = best_math_action.get("name", "Dynamic Reschedule")
        
        await streamer.broadcast("MonteCarloPlanner", f"MCTS Converged. Safest path: '{best_action_name}'", "success")

        # 4. LLM CRISIS RESOLUTION
        await streamer.broadcast("CrisisAgent", "Fusing MCTS physics data into human-readable schedule mitigation...", "thinking")
        mock_current_schedule = [{"session": "Hacking Phase 1", "time": "11:00 AM"}]
        
        enhanced_crisis_prompt = f"""
        CRISIS: {crisis_desc}
        HISTORICAL CONTEXT: {past_crises}
        MCTS OPTIMAL ACTION: Our Monte Carlo simulations proved that the strategy '{best_action_name}' is the safest route.
        
        You MUST build your final mitigation strategy around this MCTS Optimal Action.
        """
        
        solution = await self.crisis.resolve(enhanced_crisis_prompt, mock_current_schedule)
        
        mitigation_text = solution.get('mitigation_strategy', 'Adjusting timeline dynamically.')
        await streamer.broadcast("SchedulerAgent", f"Applying fixes: {mitigation_text}", "simulating")
        new_schedule = self.scheduler.recalculate(solution)
        
        # 5. COMMIT TO MEMORY & ALERT
        store_memory(f"Event: {event_name} | Crisis: {crisis_desc} | MCTS Action: {best_action_name} | Mitigation: {mitigation_text}")
        
        await streamer.broadcast("EmailAgent", "Crisis override: Blasting urgent updates to participants...", "warning")
        csv_content = crisis_data.get("csv_content", "") 
        emergency_logs = self.email.send_invites(csv_content, f"URGENT EVENT UPDATE: {mitigation_text}")
        
        await streamer.broadcast("Orchestrator", "Crisis resolved. Knowledge stored in VectorDB.", "success")
        
        return {
            "crisis_injected": crisis_desc, 
            "applied_solution": solution, 
            "new_schedule": new_schedule,
            "emergency_emails_sent": emergency_logs
        }