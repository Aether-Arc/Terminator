from sklearn.ensemble import GradientBoostingRegressor
import numpy as np
import pandas as pd

class AttendancePredictor:
    def __init__(self):
        self.model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
        self._train_synthetic_model()

    def _train_synthetic_model(self):
        # Generate 1000 rows of realistic event data
        np.random.seed(42)
        # Features: [Registrations, Marketing Spend ($), Days to Event, Is_Weekend (0/1)]
        n_samples = 1000
        registrations = np.random.randint(50, 2000, n_samples)
        marketing = np.random.randint(0, 5000, n_samples)
        days_out = np.random.randint(1, 60, n_samples)
        is_weekend = np.random.randint(0, 2, n_samples)
        
        X = np.column_stack((registrations, marketing, days_out, is_weekend))
        
        # Target: Actual Attendance (Usually lower than registrations, boosted by marketing and weekends)
        drop_off_rate = 0.30 + (days_out * 0.002) - (marketing * 0.00001) - (is_weekend * 0.05)
        drop_off_rate = np.clip(drop_off_rate, 0.1, 0.6) # Between 10% and 60% drop off
        
        y = registrations * (1 - drop_off_rate)
        # Add some random noise
        y = y + np.random.normal(0, registrations * 0.05) 
        
        self.model.fit(X, y)

    def predict_attendance(self, registrations, marketing_spend=1000, days_out=14, is_weekend=1):
        """Predicts actual physical attendance based on current metrics."""
        prediction = self.model.predict([[registrations, marketing_spend, days_out, is_weekend]])
        return int(max(0, prediction[0]))