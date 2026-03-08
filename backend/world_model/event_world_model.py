import random

class WorldModelAgent: # Renamed to match the import in orchestrator.py
    def __init__(self):
        # Base state for the event environment
        self.state = {
            "crowd_size": 500,
            "rooms": 5,
            "speakers": 10,
            "delay": 0
        }

    def clone(self):
        return dict(self.state)

    def simulate_action(self, state, action):
        """Simulates the effect of a specific action on the environment state."""
        new_state = dict(state)
        
        if action == "reschedule":
            new_state["delay"] += random.randint(5, 15)
        if action == "add_room":
            new_state["rooms"] += 1
        if action == "replace_speaker":
            new_state["speakers"] += 0
            
        return new_state

    def simulate_crowd_flow(self, plan):
        """
        DeepMind-style World Model Simulation.
        This method is called by the Orchestrator to evaluate candidate plans.
        It uses your state actions to predict spatial and temporal bottlenecks.
        """
        # 1. Spatial Simulation (Mocking the CNN logic)
        # Calculate potential room overflows based on current rooms vs expected crowd
        crowd_density = self.state["crowd_size"] / max(1, self.state["rooms"])
        spatial_bottlenecks = int(crowd_density // 50) # Assuming >50 per room is a bottleneck
        
        # 2. Temporal Simulation (Mocking the RNN logic)
        temp_state = self.clone()
        
        # Randomly inject a realistic delay to test the plan's resilience
        if random.random() > 0.5:
            temp_state = self.simulate_action(temp_state, "reschedule")
            
        delay_minutes = temp_state["delay"]
        
        # 3. Calculate Reward/Stability Score for the Critic Agent
        # Higher score is better. Max is 100.
        score = 100 - (spatial_bottlenecks * 5) - delay_minutes
        
        return {
            "spatial_bottlenecks": spatial_bottlenecks,
            "temporal_cascades": {"total_event_overrun": delay_minutes},
            "overall_stability_score": score
        }