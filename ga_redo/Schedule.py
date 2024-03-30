import random


class Schedule:
    def __init__(self, course_list, classroom_list, instructor_list):
        self.MONDAY_TIME_SLOTS = 9
        self.TUESDAY_TIME_SLOTS = 4
        self.WEDNESDAY_TIME_SLOTS = 9
        self.THURSDAY_TIME_SLOTS = 4
        self.FRIDAY_TIME_SLOTS = 9

        self.course_list = course_list
        self.classroom_list = classroom_list
        self.instructor_list = instructor_list

        self.num_time_slots = (self.MONDAY_TIME_SLOTS + self.TUESDAY_TIME_SLOTS + self.WEDNESDAY_TIME_SLOTS +
                               self.THURSDAY_TIME_SLOTS + self.FRIDAY_TIME_SLOTS)
        self.schedule = []
        self.selection_prob = 0
        self.fitness = 0

    def create_genome(self):
        schedule = [[-1] * self.num_time_slots for _ in range(len(self.classroom_list))]
        # Randomly assign courses to time slots and classrooms
        for course_id in range(len(self.course_list)):
            classroom_index = -1
            time_available = False
            days_index_list = []

            while not time_available:
                time_slot_index = random.randint(0, self.num_time_slots - 1)
                classroom_index = random.randint(0, len(self.classroom_list) - 1)
                time_available, days_index_list = self.time_available(classroom_index, time_slot_index, schedule)

            for time_block_index in days_index_list:
                schedule[classroom_index][time_block_index] = course_id
        self.schedule = schedule

    def time_available(self, classroom_index, time_slot_index, schedule):
        """
        Determines if a classroom is available at the designated time.

        :param classroom_index: id number of the classroom to be checked
        :param time_slot_index: index of the time slot to be checked within the designated classroom
        :return: True if the classroom is available at the designated time; False otherwise
        """
        # If the chosen time index falls within the time slots for Monday, the course will be a MWF course
        if time_slot_index < self.MONDAY_TIME_SLOTS:
            monday_slot_index = time_slot_index
            wednesday_slot_index = monday_slot_index + (
                    self.MONDAY_TIME_SLOTS - time_slot_index) + self.TUESDAY_TIME_SLOTS + monday_slot_index
            friday_slot_index = wednesday_slot_index + (
                    self.WEDNESDAY_TIME_SLOTS - time_slot_index) + self.THURSDAY_TIME_SLOTS + monday_slot_index
            if (schedule[classroom_index][monday_slot_index] == -1 and
                    schedule[classroom_index][wednesday_slot_index] == -1 and
                    schedule[classroom_index][friday_slot_index] == -1):
                return True, [monday_slot_index, wednesday_slot_index, friday_slot_index]
        # If the chosen time index falls within the time slots for Tuesday, the course will be a Tth course
        elif time_slot_index < (self.MONDAY_TIME_SLOTS + self.TUESDAY_TIME_SLOTS):
            tuesday_slot_index = time_slot_index
            thursday_slot_index = (
                    tuesday_slot_index + (self.TUESDAY_TIME_SLOTS - (time_slot_index - self.MONDAY_TIME_SLOTS)) +
                    self.WEDNESDAY_TIME_SLOTS + (time_slot_index - self.MONDAY_TIME_SLOTS))
            if (schedule[classroom_index][tuesday_slot_index] == -1 and
                    schedule[classroom_index][thursday_slot_index] == -1):
                return True, [tuesday_slot_index, thursday_slot_index]
        return False, []

    def display_genotype(self):
        print(self.schedule)

    def display_phenotype(self):
        monday_index = 0
        tuesday_index = self.MONDAY_TIME_SLOTS
        wednesday_index = self.MONDAY_TIME_SLOTS + self.TUESDAY_TIME_SLOTS
        thursday_index = self.MONDAY_TIME_SLOTS + self.TUESDAY_TIME_SLOTS + self.WEDNESDAY_TIME_SLOTS
        friday_index = self.MONDAY_TIME_SLOTS + self.TUESDAY_TIME_SLOTS + self.WEDNESDAY_TIME_SLOTS + self.THURSDAY_TIME_SLOTS
        for classroom_index in range(len(self.classroom_list)):
            monday_blocks = self.schedule[classroom_index][monday_index:tuesday_index]
            tuesday_blocks = self.schedule[classroom_index][tuesday_index:wednesday_index]
            wednesday_blocks = self.schedule[classroom_index][wednesday_index:thursday_index]
            thursday_blocks = self.schedule[classroom_index][thursday_index:friday_index]
            friday_blocks = self.schedule[classroom_index][friday_index:len(self.schedule[classroom_index])]

            print (f"\nClassroom #{classroom_index} Schedule: \n"
                  f"---------------------------\n"
                  f"Monday: {monday_blocks}\n"
                  f"Tuesday: {tuesday_blocks}\n"
                  f"Wednesday: {wednesday_blocks}\n"
                  f"Thursday: {thursday_blocks}\n"
                  f"Friday: {friday_blocks}")
