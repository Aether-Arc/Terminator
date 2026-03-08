class VolunteerAgent:
    def assign_shifts(self, expected_crowd):
        base_volunteers = 10
        extra_volunteers = expected_crowd // 50  # 1 extra per 50 people
        
        total_needed = base_volunteers + extra_volunteers
        
        shifts = {
            "Morning (8AM - 2PM)": total_needed,
            "Afternoon (2PM - 8PM)": total_needed,
            "Night Hack (8PM - 8AM)": total_needed // 2 
        }
        
        return {
            "total_volunteers_needed": total_needed,
            "shift_distribution": shifts
        }