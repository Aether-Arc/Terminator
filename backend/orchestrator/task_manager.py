class TaskManager:
    @staticmethod
    def run_supervisor(state):
        event_prompt = str(state["event_data"]).lower()
        agents_to_wake_up = ["marketing", "email"] 
        
        if "physical" in event_prompt or "summit" in event_prompt or state["event_data"].get("expected_crowd", 0) > 100:
            agents_to_wake_up.extend(["volunteer", "budget", "attendance_ml", "sponsor"])
            
        if "requested_agents" in state["event_data"]:
            agents_to_wake_up.extend(state["event_data"]["requested_agents"])

        agents_to_wake_up = list(set(agents_to_wake_up))
        
        # Contextual Intelligence Injection
        if "sponsor" in agents_to_wake_up:
            state["event_data"]["sponsor_directive"] = "Strictly target elite MBB management consulting firms for sponsorships. Exclude B4."

        return {
            "pending_agents": agents_to_wake_up, 
            "active_agents": agents_to_wake_up,
            "event_data": state["event_data"]
        }