import random
import numpy as np

class DelaySimulator:
    def simulate_stochastic_delay(self, base_risk=0.15):
        """Simulates real-world chaos using probabilistic models."""
        chaos_triggered = random.random() < base_risk
        
        if chaos_triggered:
            # Poisson distribution creates realistic random delays (e.g., avg 15 min, but sometimes 45 min)
            delay_minutes = np.random.poisson(lam=15)
            reasons = ["AV Equipment Failure", "Keynote Speaker Stuck in Traffic", "Wi-Fi Outage"]
            return {"delay_minutes": delay_minutes, "reason": random.choice(reasons)}
        
        return {"delay_minutes": 0, "reason": "Operations Normal"}