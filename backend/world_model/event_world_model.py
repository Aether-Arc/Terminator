class WorldModelAgent:
    def __init__(self):
        # Realistic constraints
        self.max_safe_density = 4  # People per square meter
        self.venue_sqm = 1000      # 1000 sqm venue

    def simulate_crowd_flow(self, event_data, plan):
        crowd_size = event_data.get("expected_crowd", 500)
        
        # 1. Spatial Bottleneck Calculation
        # If crowd size exceeds safe density, bottlenecks skyrocket
        actual_density = crowd_size / self.venue_sqm
        
        if actual_density > self.max_safe_density:
            # Exponential penalty for overcrowding
            spatial_bottlenecks = int((actual_density - self.max_safe_density) * 20)
        else:
            spatial_bottlenecks = 0
            
        # 2. Temporal Delay Calculation based on crowd size
        # More people = longer lines = higher base delay
        base_delay_minutes = (crowd_size / 100) * 1.5 
        
        # Calculate Stability Score (Starts at 100)
        score = 100 - spatial_bottlenecks - int(base_delay_minutes)
        
        # Hard cap score between 0 and 100
        score = max(0, min(100, score))
        
        return {
            "spatial_bottlenecks": spatial_bottlenecks,
            "temporal_cascades": {"total_event_overrun": int(base_delay_minutes)},
            "overall_stability_score": score,
            "warning": "CRITICAL CROWD CRUSH RISK" if actual_density > self.max_safe_density else "Flow Optimal"
        }