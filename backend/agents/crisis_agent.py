class CrisisAgent:

    def resolve(self, issue):

        if issue["type"] == "speaker_cancelled":

            return {
                "action": "Reschedule session",
                "priority": "high"
            }

        if issue["type"] == "room_overflow":

            return {
                "action": "Move to bigger hall"
            }

        return {"action": "manual intervention"}