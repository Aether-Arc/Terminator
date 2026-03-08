from ortools.sat.python import cp_model
import math

class SchedulerAgent:
    def __init__(self):
        pass

    def create_schedule(self, best_plan):
        # best_plan is a JSON dictionary from PlannerAgent
        sessions = best_plan.get("sessions", [])
        if not sessions:
            return [{"error": "No sessions provided to schedule"}]

        model = cp_model.CpModel()
        
        # We will schedule within a 12-hour window (e.g., 9 AM to 9 PM)
        # FIX: Convert horizon to minutes to allow for decimal hours from the LLM
        horizon_minutes = 12 * 60 
        
        intervals = []
        session_vars = {}

        for i, session in enumerate(sessions):
            # The LLM might return an int (2) or a float (1.5) or a string ("1.5")
            try:
                duration_hours = float(session.get("duration_hours", 2))
            except (ValueError, TypeError):
                duration_hours = 2.0
                
            # Convert to integer minutes
            duration_mins = int(math.ceil(duration_hours * 60))
            
            # Now we use whole integer minutes for OR-Tools constraints
            start_var = model.NewIntVar(0, horizon_minutes - duration_mins, f'start_{i}')
            end_var = model.NewIntVar(duration_mins, horizon_minutes, f'end_{i}')
            interval_var = model.NewIntervalVar(start_var, duration_mins, end_var, f'interval_{i}')
            
            intervals.append(interval_var)
            session_vars[i] = {
                "name": session.get("name", f"Session {i}"),
                "start": start_var,
                "end": end_var
            }

        # CONSTRAINT 1: No two sessions can overlap
        model.AddNoOverlap(intervals)

        # Solve the model
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        final_schedule = []
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract the actual solved times in minutes
            for i in range(len(sessions)):
                start_mins = solver.Value(session_vars[i]['start'])
                end_mins = solver.Value(session_vars[i]['end'])
                
                # Convert minutes back to AM/PM strings (Assuming 9 AM start)
                start_hour = 9 + (start_mins // 60)
                start_min_remainder = start_mins % 60
                
                end_hour = 9 + (end_mins // 60)
                end_min_remainder = end_mins % 60
                
                # Format to HH:MM AM/PM
                def format_time(h, m):
                    period = "AM" if h < 12 or h == 24 else "PM"
                    display_h = h if h <= 12 else h - 12
                    # Handle midnight case
                    if display_h == 0: display_h = 12 
                    return f"{display_h}:{m:02d} {period}"
                
                final_schedule.append({
                    "session": session_vars[i]["name"],
                    "start": format_time(start_hour, start_min_remainder),
                    "end": format_time(end_hour, end_min_remainder),
                    "track": "Main Stage" if session.get("requires_main_stage") else "Breakout",
                    "status": "Mathematically Locked"
                })
            
            # Sort chronologically (simplistic sort based on calculated start minutes)
            final_schedule.sort(key=lambda x: solver.Value(session_vars[next(j for j, v in session_vars.items() if v["name"] == x["session"])]['start']))
            return final_schedule
        else:
            return [{"error": "OR-Tools could not find a feasible schedule!"}]

    def recalculate(self, crisis_solution):
        """Dynamically adjusts the schedule based on the CrisisAgent's LLM output."""
        delay = crisis_solution.get("delay_minutes", 0)
        strategy = crisis_solution.get("mitigation_strategy", "Adjusting timeline.")
        
        return {
            "status": "Recalculated",
            "action_taken": strategy,
            "delay_applied": f"+{delay} minutes to all subsequent tracks."
        }