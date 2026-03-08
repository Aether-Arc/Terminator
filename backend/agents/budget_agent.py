class BudgetAgent:
    def __init__(self):
        self.total_budget = 50000 
        self.allocated = 0

    def calculate_costs(self, event_data, predicted_attendance):
        food_cost_per_person = 15
        venue_base_cost = 10000
        swag_cost = 10 * predicted_attendance
        
        total_food = food_cost_per_person * predicted_attendance
        total_expense = total_food + venue_base_cost + swag_cost
        
        status = "Under Budget" if total_expense <= self.total_budget else "OVER BUDGET CRISIS"
        
        return {
            "total_budget": self.total_budget,
            "projected_expense": total_expense,
            "breakdown": {
                "food": total_food,
                "venue": venue_base_cost,
                "swag": swag_cost
            },
            "status": status
        }