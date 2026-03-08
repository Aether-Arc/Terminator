import numpy as np
from sklearn.ensemble import RandomForestRegressor

class EngagementPredictor:
    def __init__(self):
        self.model = RandomForestRegressor()
        # Mock training data: [Hour of day, Day of week (0=Mon), Days until event]
        X = np.array([[9, 1, 30], [14, 3, 15], [18, 5, 5], [20, 6, 2]])
        # Mock Engagement score
        y = np.array([50, 85, 120, 200]) 
        self.model.fit(X, y)

    def predict_best_time(self, days_until_event):
        best_score = 0
        best_hour = 0
        
        # Test hours from 8 AM to 10 PM
        for hour in range(8, 23):
            score = self.model.predict([[hour, 4, days_until_event]])[0]
            if score > best_score:
                best_score = score
                best_hour = hour
                
        return {"recommended_post_hour": f"{best_hour}:00", "expected_engagement_score": int(best_score)}