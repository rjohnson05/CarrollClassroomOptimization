from Schedule import Schedule

"""
Class for representing a single classroom within the genetic algorithm. Each classroom has a name (e.g. SIMP-120), a
number of seats, and a schedule. The schedule is a list as large as the sum of the number of time blocks on
both Monday and Tuesday, with each element representing an approved class period (e.g. 8:00 - 8:50). Initially, all 
elements in the list are -1. Whenever a course is added to the classroom for a time block, -1 is changed to the course 
object.

Author: Ryan Johnson
"""


class Classroom:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.schedule = [-1] * (Schedule.MONDAY_TIME_SLOTS + Schedule.TUESDAY_TIME_SLOTS)

    def __str__(self):
        return self.name
