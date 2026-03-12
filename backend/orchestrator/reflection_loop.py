import asyncio

class ReflectionLoop:
    def __init__(self, critic_agent, rl_memory):
        self.critic = critic_agent
        self.rl_memory = rl_memory

    async def evaluate_candidates(self, state):
        candidates = state.get("candidates", [])
        sim_metrics = state.get("simulation_metrics", [])
        
        review_tasks = []
        for i, (plan, metrics) in enumerate(zip(candidates, sim_metrics)):
            # 🚀 FIX: Pass the two distinct arguments to the Critic review method
            review_tasks.append(self.critic.review(plan, metrics))
            
        # This executes them sequentially to respect API limits
        reviews = []
        for task in review_tasks:
            reviews.append(await task)
        
        best_score = -1
        best_plan = None
        best_metrics = None
        feedback_notes = ""
        
        for i, review in enumerate(reviews):
            score = review.get("score", 50)
            if score > best_score:
                best_score = score
                best_plan = candidates[i]
                best_metrics = sim_metrics[i]
                feedback_notes = review.get("feedback", "")
        
        crowd_size = state["event_data"].get("expected_crowd", 500)
        self.rl_memory.update_policy(state=str(crowd_size), action="selected_plan", reward=best_score, next_state="execution")
        
        return {
            "plan": best_plan, 
            "score": best_score, 
            "critic_feedback": feedback_notes, 
            "simulation_metrics": best_metrics
        }