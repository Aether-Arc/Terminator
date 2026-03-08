class ResourceAgent:
    def __init__(self):
        self.available_rooms = {
            "Main Hall": {"capacity": 1000, "av_ready": True},
            "Workshop Room A": {"capacity": 150, "av_ready": True},
            "Workshop Room B": {"capacity": 100, "av_ready": False}
        }

    def allocate(self, schedule_plan):
        allocations = []
        for session in schedule_plan:
            expected_crowd = session.get("expected_attendance", 50)
            
            # Find the best fit room
            best_room = None
            for room, details in self.available_rooms.items():
                if details["capacity"] >= expected_crowd:
                    if not best_room or details["capacity"] < self.available_rooms[best_room]["capacity"]:
                        best_room = room
            
            if best_room:
                allocations.append({
                    "session": session["session"],
                    "room": best_room,
                    "status": "Allocated"
                })
            else:
                allocations.append({
                    "session": session["session"],
                    "error": "CRISIS: No room large enough"
                })
        return allocations