from Schedule import Schedule


class Classroom:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.schedule = self.create_empty_schedule()

    def create_empty_schedule(self):
        monday_blocks = [[-1] * Schedule.MONDAY_TIME_SLOTS]
        tuesday_blocks = [-1 * Schedule.TUESDAY_TIME_SLOTS]
        return [monday_blocks, tuesday_blocks]
