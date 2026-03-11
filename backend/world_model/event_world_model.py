import copy
from simulation.event_simulator import EventSimulator

class WorldModelAgent:
    def __init__(self):
        self.max_safe_density = 4  
        self.venue_sqm = 1000      
        self.simulator = EventSimulator() # Injecting stochastic simulation

    def clone(self):
        # MCTS requires cloning the state to simulate multiple futures
        return copy.deepcopy(self)

    def simulate_action(self, state, action_dict):
        # Applies an AI-generated action to a state using dynamic math
        new_state = copy.deepcopy(state)
        
        # Multiply the current crowd by the LLM's crowd modifier
        modifier = action_dict.get("crowd_modifier", 1.0)
        new_state["crowd_size"] = int(new_state.get("crowd_size", 500) * modifier)
        
        # Add the LLM's estimated delay
        new_state["delay"] = new_state.get("delay", 0) + action_dict.get("delay_minutes", 15)
            
        return new_state

    def simulate_crowd_flow(self, event_data, plan):
        crowd_size = event_data.get("expected_crowd", 500)
        
        # 1. Random Chaos Injection
        stochastic_event = self.simulator.simulate_delay()
        chaos_delay = stochastic_event["delay_minutes"]
        
        # 2. Spatial Bottleneck Calculation
        actual_density = crowd_size / self.venue_sqm
        spatial_bottlenecks = int((actual_density - self.max_safe_density) * 20) if actual_density > self.max_safe_density else 0
            
        # 3. Temporal Calculation
        base_delay = (crowd_size / 100) * 1.5 
        total_delay = base_delay + chaos_delay
        
        # Score calculation
        score = 100 - spatial_bottlenecks - int(total_delay)
        
        return {
            "spatial_bottlenecks": spatial_bottlenecks,
            "temporal_cascades": {"total_event_overrun": int(total_delay), "random_delay_injected": chaos_delay},
            "overall_stability_score": max(0, min(100, score)),
            "warning": "CRITICAL CROWD CRUSH RISK" if actual_density > self.max_safe_density else "Flow Optimal"
        }