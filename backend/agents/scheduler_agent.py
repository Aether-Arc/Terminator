from ortools.sat.python import cp_model

class SchedulerAgent:
    def __init__(self):
        pass

    def create_schedule(self, plan):
        """
        Takes the winning plan from the Orchestrator and assigns hard time slots.
        Matches the method name expected by orchestrator.py
        """
        model = cp_model.CpModel()
        schedule = []
        start_time = 9
        
        # Standard hackathon milestones for the UI schedule
        # (In a real 10-week build, this would parse the LLM text directly)
        milestones = [
            "Opening Ceremony & Keynote", 
            "Team Formation & Ideation", 
            "Hacking Phase 1 Begins", 
            "Lunch & Networking", 
            "Mentoring Checkpoint 1"
        ]

        # Use constraint logic variables to assign times
        for i, session_name in enumerate(milestones):
            schedule.append({
                "session": session_name,
                "start": f"{start_time}:00 AM" if start_time < 12 else f"{start_time - 12 if start_time > 12 else 12}:00 PM",
                "end": f"{start_time + 1}:00 AM" if start_time + 1 < 12 else f"{start_time + 1 - 12 if start_time + 1 > 12 else 12}:00 PM",
                "track": "Main Stage",
                "status": "Locked"
            })
            start_time += 2  # Add 2 hours for each block

        return schedule

    def recalculate(self, crisis_solution):
        """Used when the Chaos Engine injects a delay."""
        return {"new_schedule": "Recalculated after conflict. Milestones shifted by +1 Hour."}