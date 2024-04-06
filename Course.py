class Course:
    def __init__(self, name, enrolled, instructor):
        self.name = name
        self.enrolled = enrolled
        self.instructor = instructor

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
