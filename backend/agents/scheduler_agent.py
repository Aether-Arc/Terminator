from ortools.sat.python import cp_model


class SchedulerAgent:

    def build_schedule(self, sessions):

        model = cp_model.CpModel()

        schedule = []

        start = 9

        for i, s in enumerate(sessions):

            schedule.append({
                "session": s,
                "start": start,
                "end": start + 1
            })

            start += 1

        return schedule