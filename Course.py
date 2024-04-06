"""
Class for representing a single course within the genetic algorithm. Each course has a name, instructor, and the number
of students enrolled. Each course is assigned to a specific time block in a classroom containing at least as many seats
as the number of students enrolled.

Author: Ryan Johnson
"""


class Course:
    def __init__(self, name, enrolled, instructor):
        self.name = name
        self.enrolled = enrolled
        self.instructor = instructor

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
