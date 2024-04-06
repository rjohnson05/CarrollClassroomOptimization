import random
from copy import copy, deepcopy


class Schedule:
    MONDAY_TIME_SLOTS = 10
    TUESDAY_TIME_SLOTS = 7

    def __init__(self, course_list, classroom_list, instructor_list):
        self.MONDAY_TIME_SLOTS = 10
        self.TUESDAY_TIME_SLOTS = 7

        self.course_list = course_list
        self.classroom_list = deepcopy(classroom_list)
        self.instructor_list = instructor_list

        self.num_time_slots = (self.MONDAY_TIME_SLOTS + self.TUESDAY_TIME_SLOTS)
        self.schedule = [classroom for classroom in self.classroom_list]
        self.selection_prob = 0
        self.fitness = 0

    def create_genome(self):
        """
        Assigns each course in the course list to an available classroom and time. The chosen classroom must have enough
        seats to hold the number of students enrolled in the course. If an available time is not found within 10 iterations,
        the course is skipped.
        """
        for course in self.course_list:
            time_slot_index = None
            classroom_index = None

            # If an available time slot and classroom is not found within 10 iterations, skip the course
            for i in range(10):
                time_slot_index = random.randint(0, self.num_time_slots - 1)
                classroom_index = random.randint(0, len(self.classroom_list) - 1)
                time_available, days_index_list = self.time_available(classroom_index, time_slot_index, course.enrolled)
                if time_available:
                    break

            classroom_schedule = self.schedule[classroom_index].schedule
            classroom_schedule[time_slot_index] = course

    def time_available(self, classroom_index, time_slot_index, enrollment_num):
        """
        Determines if a classroom is available at the designated time.

        :param classroom_index: id number of the classroom to be checked
        :param time_slot_index: index of the time slot to be checked within the designated classroom
        :param enrollment_num: number of students enrolled in the course being added to the schedule
        :return: True if the classroom is available at the designated time; False otherwise
        """
        classroom = self.schedule[classroom_index]
        # Make sure the classroom has enough seats for the number of enrolled students
        if enrollment_num > self.schedule[classroom_index].size:
            return False, -1
        # If the chosen time index falls within the time slots for Monday, the course will be a MWF course
        if time_slot_index < self.MONDAY_TIME_SLOTS:
            classroom_schedule = classroom.schedule
            if classroom_schedule[time_slot_index] == -1:
                return True, time_slot_index
        # If the chosen time index falls within the time slots for Tuesday, the course will be a Tth course
        else:
            # Convert the time slot index to the correct index when only considering Tuesday's array
            classroom_schedule = classroom.schedule
            if classroom_schedule[time_slot_index] == -1:
                return True, time_slot_index
        return False, -1

    def display_genotype(self):
        for classroom in self.schedule:
            print(f"{classroom}: {classroom.schedule}")

    def display_phenotype(self):
        for classroom in self.schedule:
            monday_courses = [course for course in classroom.schedule[:self.MONDAY_TIME_SLOTS]]
            tuesday_courses = [course for course in classroom.schedule[self.MONDAY_TIME_SLOTS:]]

            print(f"\n{classroom}\n---------")

            print(f"Monday:")
            print(f"  8:00 - 8:50 AM : {"N/A" if monday_courses[0] == -1 else monday_courses[0]}")
            print(f"  9:00 - 9:50 AM : {"N/A" if monday_courses[1] == -1 else monday_courses[1]}")
            print(f"  10:00 - 10:50 AM : {"N/A" if monday_courses[2] == -1 else monday_courses[2]}")
            print(f"  11:00 - 11:50 AM : {"N/A" if monday_courses[3] == -1 else monday_courses[3]}")
            print(f"  12:00 - 12:50 PM : {"N/A" if monday_courses[4] == -1 else monday_courses[4]}")
            print(f"  1:00 - 1:50 PM : {"N/A" if monday_courses[5] == -1 else monday_courses[5]}")
            print(f"  2:00 - 2:50 PM : {"N/A" if monday_courses[6] == -1 else monday_courses[6]}")
            print(f"  3:00 - 3:50 PM : {"N/A" if monday_courses[7] == -1 else monday_courses[7]}")
            print(f"  4:00 - 4:50 PM : {"N/A" if monday_courses[8] == -1 else monday_courses[8]}")
            print(f"  5:00 - 5:50 PM : {"N/A" if monday_courses[9] == -1 else monday_courses[9]}")

            print(f"Tuesday:")
            print(f"  8:00 - 9:15 AM : {"N/A" if tuesday_courses[0] == -1 else tuesday_courses[0]}")
            print(f"  9:30 - 10:45 AM : {"N/A" if tuesday_courses[1] == -1 else tuesday_courses[1]}")
            print(f"  11:00 AM - 12:15 PM : {"N/A" if tuesday_courses[2] == -1 else tuesday_courses[2]}")
            print(f"  2:15 - 3:30 AM : {"N/A" if tuesday_courses[3] == -1 else tuesday_courses[3]}")
            print(f"  3:45 - 5:00 PM : {"N/A" if tuesday_courses[4] == -1 else tuesday_courses[4]}")
            print(f"  5:15 - 6:30 PM : {"N/A" if tuesday_courses[5] == -1 else tuesday_courses[5]}")
