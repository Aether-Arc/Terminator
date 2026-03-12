from simulation.crowd_simulation import CrowdSimulator
from simulation.delay_simulation import DelaySimulator

class EventSimulator:
    def __init__(self):
        self.crowd_sim = CrowdSimulator()
        self.delay_sim = DelaySimulator()

    def run_full_simulation(self, event_data, plan):
        crowd_size = event_data.get("expected_crowd", 500)
        
        # 1. Run Spatial Graph Simulation
        spatial_data = self.crowd_sim.calculate_bottlenecks(crowd_size, plan)
        
        # 2. Run Temporal Chaos Simulation
        temporal_data = self.delay_sim.simulate_stochastic_delay()
        
        # 3. Calculate Overall Stability
        base_score = 100
        score = base_score - (spatial_data["spatial_bottlenecks"] * 2) - temporal_data["delay_minutes"]
        
        return {
            "spatial_bottlenecks": spatial_data["spatial_bottlenecks"],
            "temporal_cascades": {"random_delay_injected": temporal_data["delay_minutes"], "reason": temporal_data["reason"]},
            "overall_stability_score": max(0, min(100, int(score))),
            "warning": "CRITICAL RISK" if spatial_data["density_warning"] else "Flow Optimal"
        }