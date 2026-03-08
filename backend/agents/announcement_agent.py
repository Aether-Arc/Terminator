class AnnouncementAgent:
    def generate_alert(self, crisis_data):
        issue = crisis_data.get("type")
        
        if issue == "speaker_cancelled":
            return "URGENT UPDATE: Unfortunately, our speaker for the 10 AM slot had to cancel. We are extending the networking break. Enjoy the free coffee in Hall B!"
        elif issue == "room_overflow":
            return "VENUE UPDATE: The AI Workshop is packed! We are streaming it live on the main screens in the cafeteria."
        else:
            return "Schedule has been updated. Please refresh your dashboard."