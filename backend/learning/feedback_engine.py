class FeedbackEngine:
    def __init__(self):
        self.target_density = 2.0 # Optimal people per sq meter
        
    def calculate_reward(self, world_model_metrics, critic_score):
        """
        Calculates a deep reinforcement learning reward based on multi-objective optimization.
        """
        reward = 0.0
        
        # 1. Physics Engine Reward (Spatial Constraints)
        bottlenecks = world_model_metrics.get("spatial_bottlenecks", 0)
        if bottlenecks == 0:
            reward += 40
        else:
            reward -= (bottlenecks * 2) # Heavily penalize crowd crushes
            
        # 2. Temporal Constraints
        cascades = world_model_metrics.get("temporal_cascades", {})
        overrun = cascades.get("total_event_overrun", 0)
        if overrun < 15:
            reward += 30
        else:
            reward -= overrun
            
        # 3. LLM Strategic Evaluation
        # The critic score is out of 100. We weight it as 30% of the total reward.
        reward += (critic_score * 0.3)
        
        # Normalize between 0 and 100
        return max(0.0, min(100.0, reward))