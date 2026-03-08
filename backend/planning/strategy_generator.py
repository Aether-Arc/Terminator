class StrategyGenerator:

    def generate(self, crisis):

        if crisis["type"] == "speaker_cancelled":

            return [
                "reschedule",
                "replace_speaker",
                "merge_sessions"
            ]

        if crisis["type"] == "room_overflow":

            return [
                "add_room",
                "split_audience",
                "stream_online"
            ]

        return []