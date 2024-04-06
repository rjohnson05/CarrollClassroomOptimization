from Schedule import Schedule


class Classroom:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.schedule = [-1] * (Schedule.MONDAY_TIME_SLOTS + Schedule.TUESDAY_TIME_SLOTS)

    def display_schedule(self):
        print(f"{self.name}: {self.schedule}")

    def __str__(self):
        return self.name
