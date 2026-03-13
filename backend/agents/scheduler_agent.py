from ortools.sat.python import cp_model
import math
import json
import re
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
from tools.system_tools import swarm_tools

class SchedulerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LOCAL_MODEL, 
            base_url=OLLAMA_BASE_URL, 
            api_key=OPENAI_API_KEY, 
            temperature=0.4 
        )
        self.agent_executor = create_react_agent(self.llm, swarm_tools)

    async def create_schedule(self, best_plan):
        original_sessions = best_plan.get("sessions", [])
        if not original_sessions:
            return [{"error": "No sessions provided to schedule"}]

        session_names = [s.get("name", "Session") for s in original_sessions]
        user_constraints = best_plan.get("user_constraints", "None specified.")
        
        # 🚀 DYNAMIC DURATION CHECK: Is this a hackathon/overnight event?
        context_str = (str(session_names) + " " + str(user_constraints)).lower()
        is_continuous = "hackathon" in context_str or "overnight" in context_str
        limit_hours = 24.0 if is_continuous else 11.0

        if is_continuous:
            time_rule = "1. CONTINUOUS EVENT: This is a hackathon or continuous event. You can schedule up to 24 hours per day. Overnight activities are allowed."
            duration_rule = "4. ASSIGN DURATIONS: Assign a realistic 'duration_hours'. The total sum of `duration_hours` for ANY single day MUST NOT exceed 24.0."
        else:
            time_rule = "1. STRICT 11-HOUR LIMIT: The event runs exclusively from 9:00 AM to 8:00 PM. If the user's total request requires more than 11 hours, you MUST split the event across multiple days (Day 1, Day 2, etc.). DO NOT schedule overnight activities."
            duration_rule = "4. ASSIGN DURATIONS: Assign a realistic 'duration_hours' (e.g., 0.5 for 30 mins, 4.0 for a coding sprint). The total sum of `duration_hours` for ANY single day MUST NOT exceed 11.0."

        # --- 1. AI RESEARCH & INTELLIGENT STRUCTURING ---
        prompt = f"""
        You are an elite event logistics AI. 
        Core requested sessions: {session_names}
        User Context/Prompt: "{user_constraints}"
        
        MANDATORY RULES:
        {time_rule}
        2. ASSIGN DAYS: Assign a "day" integer (1, 2, 3...) to every single session.
        3. INJECT BREAKS & FUN: Inject natural breaks (Meals). If the user asked for specific things (like "mini-games", "networking"), YOU MUST add them as explicit sessions.
        {duration_rule}
        
        Use the 'web_search' tool if you need to look up standard durations for specific technical events or activities.
        
        Return ONLY a valid JSON array of objects in chronological sequence.
        CRITICAL RULE: Escape all inner double quotes using a backslash.
        Example multi-day format: 
        [
            {{"name": "Opening Brief", "duration_hours": 1.0, "day": 1}},
            {{"name": "Hackathon Phase 1", "duration_hours": 6.0, "day": 1}},
            {{"name": "Morning Mini-Games", "duration_hours": 1.5, "day": 2}},
            {{"name": "Hackathon Phase 2", "duration_hours": 7.0, "day": 2}}
        ]
        """
        
        ordered_sessions = []
        try:
            print(f"[*] SchedulerAgent: Determining optimal days. Dynamic limit set to {limit_hours} hours/day...")
            response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            
            # --- 🚀 BULLETPROOF REGEX PARSER FOR SCHEDULER ---
            final_text = response["messages"][-1].content
            clean_text = final_text.replace("```json", "").replace("```", "").strip()
            
            # Search specifically for a JSON Array [...]
            match = re.search(r'\[.*\]', clean_text, re.DOTALL)
            if not match:
                raise ValueError("No JSON array found in LLM response.")
                
            clean_json_string = match.group(0)
            durations_data = json.loads(clean_json_string, strict=False)
            # -------------------------------------------------
            
            for item in durations_data:
                orig = next((s for s in original_sessions if s.get("name") == item.get("name")), {})
                ordered_sessions.append({
                    "name": item.get("name"),
                    "duration_hours": float(item.get("duration_hours", 1.0)),
                    "day": int(item.get("day", 1)),
                    "requires_main_stage": orig.get("requires_main_stage", False),
                    "is_break": any(word in item.get("name", "").lower() for word in ["break", "lunch", "dinner", "mixer", "sleep", "downtime"])
                })
        except Exception as e:
            print(f"[*] SchedulerAgent AI Error: {e}")
            # Intelligent fallback: Distributes exactly 2-hour blocks, auto-spilling to next day if it hits the dynamic limit
            ordered_sessions = []
            current_day = 1
            current_hours = 0
            for s in original_sessions:
                dur = 2.0
                if current_hours + dur > limit_hours:
                    current_day += 1
                    current_hours = 0
                ordered_sessions.append({"name": s.get("name"), "duration_hours": dur, "day": current_day, "is_break": False})
                current_hours += dur

        # --- 2. MULTI-DAY MATHEMATICAL LOCKING (OR-TOOLS) ---
        days_dict = {}
        for s in ordered_sessions:
            d = s.get("day", 1)
            if d not in days_dict: days_dict[d] = []
            days_dict[d].append(s)

        final_schedule = []

        for day, day_sessions in sorted(days_dict.items()):
            model = cp_model.CpModel()
            # 🚀 DYNAMIC HORIZON: Either 660 mins (11 hr) or 1440 mins (24 hr)
            horizon_minutes = int(limit_hours * 60) 
            intervals = []
            session_vars = {}

            for i, session in enumerate(day_sessions):
                duration_mins = int(math.ceil(session.get("duration_hours", 1.0) * 60))
                
                # Prevent negative domain errors if a single day gets overpacked past the limit
                if duration_mins > horizon_minutes:
                    duration_mins = horizon_minutes

                start_var = model.NewIntVar(0, horizon_minutes - duration_mins, f'start_d{day}_{i}')
                end_var = model.NewIntVar(duration_mins, horizon_minutes, f'end_d{day}_{i}')
                interval_var = model.NewIntervalVar(start_var, duration_mins, end_var, f'interval_d{day}_{i}')
                
                intervals.append(interval_var)
                session_vars[i] = {
                    "name": session["name"], 
                    "start": start_var, 
                    "end": end_var
                }

                # Chronological forcing: Next event starts exactly when the last one ends
                if i > 0:
                    model.Add(start_var == session_vars[i-1]['end'])
                else:
                    model.Add(start_var == 0) # Minute 0 = 9:00 AM

            model.AddNoOverlap(intervals)
            solver = cp_model.CpSolver()
            status = solver.Solve(model)

            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                for i in range(len(day_sessions)):
                    start_mins = solver.Value(session_vars[i]['start'])
                    end_mins = solver.Value(session_vars[i]['end'])
                    
                    # Math maps perfectly for both 11h and 24h wrapping
                    start_hour = 9 + (start_mins // 60)
                    start_min = start_mins % 60
                    end_hour = 9 + (end_mins // 60)
                    end_min = end_mins % 60
                    
                    def format_time(h, m):
                        period = "AM" if (h % 24) < 12 else "PM"
                        display_h = h % 12
                        if display_h == 0: display_h = 12 
                        return f"{display_h}:{m:02d} {period}"
                    
                    # Formatted to perfectly match what the React Frontend expects
                    final_schedule.append({
                        "session": session_vars[i]["name"],
                        "time": f"Day {day} | {format_time(start_hour, start_min)} - {format_time(end_hour, end_min)}",
                        "status": "Locked"
                    })
            else:
                final_schedule.append({
                    "session": f"Day {day} Overpacked",
                    "time": f"Too many events to fit within the {int(limit_hours)}-hour daily limit.",
                    "status": "Error"
                })

        return final_schedule

    def recalculate(self, crisis_solution):
        return {"status": "Recalculated"}