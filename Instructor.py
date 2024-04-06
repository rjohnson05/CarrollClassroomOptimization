"""
Class for representing an instructor in the genetic algorithm. Each instructor has a name and a list of courses they
teach. This list is used when calculating the fitness score, ensuring that an instructor is not teaching two courses
at the same time.

Author: Ryan Johnson
"""


class Instructor:
    def __init__(self, name):
        self.name = name
        self.courses = []
