import asyncio

class CognitiveLoop:
    def __init__(self, planner, world_model, critic):
        self.planner = planner
        self.world_model = world_model
        self.critic = critic

    async def generate_optimal_plan(self, event_data, streamer):
        await streamer.broadcast("PlannerAgent", "Generating candidate strategies...", "thinking")
        
        # 🚀 FIX: Added `await` because generate_multiple_plans is an async function
        candidates = await self.planner.generate_multiple_plans(event_data, count=3)
        
        best_plan = None
        highest_score = -1
        
        # 2. Simulate each plan in the World Model
        for i, plan in enumerate(candidates):
            await streamer.broadcast("WorldModelAgent", f"Simulating timeline for Plan {i+1}...", "simulating")
            await asyncio.sleep(1) # Artificial delay for UI effect
            
            simulation_results = self.world_model.simulate_crowd_flow(plan)
            
            # 3. Critic evaluates the simulation
            await streamer.broadcast("CriticAgent", f"Evaluating friction points for Plan {i+1}...", "thinking")
            
            # 🚀 FIX: Added `await` and passed the two correct arguments to `review`
            review_result = await self.critic.review(plan, simulation_results)
            score = review_result.get("score", 0)
            
            if score > highest_score:
                highest_score = score
                best_plan = plan
                
        await streamer.broadcast("Orchestrator", f"Selected optimal plan with score {highest_score}.", "success")
        return best_plan