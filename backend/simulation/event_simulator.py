import random


class EventSimulator:

    def simulate_delay(self):

        delay = random.choice([0, 5, 10, 15])

        return {"delay_minutes": delay}


    def simulate_cancellation(self):

        return {
            "speaker_cancelled": random.choice([True, False])
        }