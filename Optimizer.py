import random
import pandas as pd

from Classroom import Classroom
from Course import Course
from Instructor import Instructor
from Schedule import Schedule

"""
Contains a genetic algorithm for creating an optimal course schedule for Carroll College. Course, classroom, and
instructor data are imported from the two spreadsheets included in this project. Using this data, the algorithm works
toward creating a schedule with the following goals:
  - No instructor may teach more than one course during a single time block
  - All courses must be included in the final schedule
  - Courses may be assigned as either a MWF or Tth course, but not both
  - Ideal schedules will use less classrooms

As the algorithm is running, the average fitness score is displayed. Once the fitness scores have converged to the same
score for five generations, the algorithm will end and display the final course schedule.

Author: Ryan Johnson
"""


class Optimizer:
    def __init__(self):
        self.POPULATION_SIZE = 500
        self.CROSSOVER_RATE = 0.001
        self.MUTATION_RATE = 0.9

        self.classroom_list, self.course_list, self.instructor_list = self.upload_data()

        self.population = self.form_population(self.POPULATION_SIZE)
        self.average_fitness = 0
        self.total_fitness = 0

    def upload_data(self):
        """
        Takes data from two Excel spreadsheets: one with classroom info and the other with course info. The data from
        these spreadsheets is combined to create the classroom, course, and instructor objects for scheduling. Each of
        these different types of object are returned as a separate list. Note that only classrooms with a known number
        of seats are used. Similarly, only courses currently located in rooms with a known number of seats are used.

        :return: list containing three sublists - classrooms, courses, and instructors
        """
        classroom_data = pd.read_excel("excel/classroom_info.xlsx", engine="openpyxl")
        course_data = pd.read_excel("excel/schedule.xlsx", engine="openpyxl").dropna(subset=['CSM_BLDG', 'CSM_ROOM'])

        # Create classroom object for each room with known number of seats
        classrooms_dict = {}
        for index, row in classroom_data.iterrows():
            room_name = row['Building Name'] + '-' + str(row['Room Number'])
            classroom = Classroom(room_name, row['Number of Student Seats in Room'])
            classrooms_dict[room_name] = classroom
        classrooms_list = list(classrooms_dict.values())

        # Create course object for each course currently located in one of the classrooms of known size
        courses_list = []
        instructors_dict = {}
        for index, row in course_data.iterrows():
            # Only use lecture courses in classrooms of known size
            room_name = row['CSM_BLDG'] + '-' + str(row['CSM_ROOM'])
            if row['CSM_INSTR_METHOD'] != "LEC" or room_name not in classrooms_dict.keys():
                continue
            instructor = Instructor(row['SEC_FACULTY_INFO'])
            course = Course(row['SEC_SHORT_TITLE'], row['SEC_CAPACITY'], instructor)
            courses_list.append(course)

            # Create a new instructor if not already in the dictionary
            if instructor.name not in instructors_dict.keys():
                instructors_dict[instructor.name] = instructor
        instructors_list = list(instructors_dict.values())
        return classrooms_list, courses_list, instructors_list

    def form_population(self, pop_size: int):
        """
        Creates the specified number of schedule objects and places them together in a single list.

        :param pop_size: Integer specifying how many individual schedules should be created
        :return: List of schedule objects
        """
        population = []
        for i in range(pop_size):
            schedule = Schedule(self.course_list, self.classroom_list, self.instructor_list)
            schedule.create_genome()
            population.append(schedule)
        return population

    def calculate_fitness(self, schedule: Schedule):
        """
        Calculates the "goodness" of a given schedule. A valid schedule will have a positive fitness score,
        while a larger positive fitness score indicates that less classrooms are being used. Schedules are penalized
        for the following:
          - Using more classrooms
          - Having instructors teaching more than one course during the same
            time block
          - Not containing all courses
          - Assigning a course to both a MWF and Tth time slot

        @param schedule: Schedule object to be evaluated
        @return: Fitness score for the Schedule object, with larger scores indicating better schedules
        """
        # Don't recalculate the fitness if it's already been calculated
        if schedule.fitness != 0:
            return schedule.fitness

        # Penalizes for using more classrooms
        num_classrooms_used = 0
        for classroom in schedule.schedule:
            for time_block in classroom.schedule:
                if time_block != -1:
                    num_classrooms_used += 1
                    break
        fitness = 1 / num_classrooms_used

        # Penalizes for assigning an instructor to a time block more than once
        for instructor in schedule.instructor_list:
            course_list = instructor.courses
            # Find the number of courses taught by an instructor during a single time block. Ideal solutions should
            # have a value of 1.
            for i in range(schedule.MONDAY_TIME_SLOTS + schedule.TUESDAY_TIME_SLOTS):
                num_courses_taught = 0
                for classroom in schedule.schedule:
                    if classroom.schedule[i] in course_list:
                        num_courses_taught += 1
                # Subtract a fitness point for every time an instructor is assigned more than once to a time block
                if num_courses_taught > 1:
                    fitness -= 1

        # Penalizes for not including all courses in the final schedule
        for course in self.course_list:
            course_found = False
            for classroom in schedule.schedule:
                if course in classroom.schedule:
                    course_found = True
                    break
            if course_found:
                continue
            fitness -= 1

        # Penalizes for assigning a course to both MWF and Tth
        for classroom in schedule.schedule:
            for monday_time_block in classroom.schedule[:schedule.MONDAY_TIME_SLOTS]:
                for tuesday_time_block in classroom.schedule[schedule.MONDAY_TIME_SLOTS:]:
                    if (monday_time_block == tuesday_time_block) and (monday_time_block != -1):
                        # print(monday_time_block, tuesday_time_block)
                        fitness -= 1
                        break

        schedule.fitness = fitness
        return fitness

    def calculated_average_fitness(self):
        """
        Calculates the average fitness score across the population as a whole. Used for determining whether the algorithm
        has converged onto a single fitness score yet.
        """
        total_fitness = 0
        fitness_levels = []
        # Add up all the fitness of each individual & store them in a list
        for schedule in self.population:
            ind_fitness = self.calculate_fitness(schedule)
            fitness_levels.append(ind_fitness)
            total_fitness += ind_fitness
        # Save the fitness of the population as a whole to be used for analysis purposes
        self.total_fitness = total_fitness
        self.average_fitness = total_fitness / len(self.population)

    def tournament_selection(self, size=3):
        """
        Randomly selects the specified number of schedules from the population and chooses the most fit of these
        schedules for parenthood
        :param size: Number of schedules to randomly choose from the population
        :return: Schedule that is most fit of the randomly selected schedules
        """
        selected = random.sample(self.population, size)
        return max(selected, key=lambda x: self.calculate_fitness(x))

    def select_parents(self):
        """
        Selects two parent schedules from the population. A random probability is then chosen, and two parents
        are selected by tournament selection. In this process, the population is looped through, stopping once the
        sum of the selection probabilities seen thus far surpasses the randomly generated number. The schedule landed on
        is selected for parenthood.

        :return: list of the two selected parents
        """
        # Selects two parents from the population. More fit schedules are more likely to be chosen than less fit
        # schedules. However, to allow for a wide search space, less fit schedules may still be selected for parenthood.
        parent1 = self.tournament_selection()
        parent2 = self.tournament_selection()
        return parent1, parent2

    def crossover(self, parents):
        """
        Mixes the genomes of two parent schedules to create a new schedule genome. For each classroom in the parent
        schedules, the genome is split in half. The first half of one parent's genome is combined with the second half
        of the other parent's genome.

        :param parents: list containing two parent schedules
        :return: child genome, created by combining the genomes of the two parent schedules
        """
        # Crossover doesn't occur (1 - CROSSOVER_RATE)% of the time
        if random.random() >= self.CROSSOVER_RATE:
            return parents[0].schedule

        parent1 = parents[0]
        parent2 = parents[1]

        crossover_point = random.randint(0, len(parent1.schedule) - 1)
        child_genome = parent1.schedule[:crossover_point] + parent2.schedule[crossover_point:]

        return child_genome

    def mutate(self, schedule: Schedule):
        """
        Mutates two schedule genomes by moving a random course from a lesser used classroom to a greater used classroom,
        moving toward fewer classrooms being used.

        :param schedule: Schedule object to be mutated
        """
        if random.random() < self.MUTATION_RATE:
            return

        # Find all classrooms hosting courses
        used_classrooms = []
        for classroom in schedule.schedule:
            for time_block in classroom.schedule:
                if time_block != -1:
                    used_classrooms.append(classroom)

        # Can't mutate if there aren't at least 2 classrooms that have courses
        if len(used_classrooms) < 2:
            return

        # Choose 2 used classrooms to mutate
        mutated_classrooms = random.sample(used_classrooms, 2)

        # Determine which classrooms hosts more courses
        greater_courses_num = 0
        greater_courses_room = None
        for classroom in mutated_classrooms:
            num_courses = classroom.schedule.count(-1)
            if num_courses > greater_courses_num:
                greater_courses_num = num_courses
                greater_courses_room = classroom
        mutated_classrooms.remove(greater_courses_room)
        lesser_courses_room = mutated_classrooms[0]

        # Pick a random course to move to the other classroom
        course_index, course = random.choice(
            [(index, course) for index, course in enumerate(lesser_courses_room.schedule) if course != -1])
        # Randomly choose courses until one is found that will fit in greater_used_room (or quit after 10 iterations)
        for i in range(10):
            if course.enrolled > greater_courses_room.size:
                course_index, course = random.choice(
                    [(index, course) for index, course in enumerate(lesser_courses_room.schedule) if course != -1])

        # Find an empty slot to move the course to
        course_placement_index = random.choice(
            [index for index, course in enumerate(greater_courses_room.schedule) if course == -1])
        lesser_courses_room.schedule[course_index] = -1
        greater_courses_room.schedule[course_placement_index] = course

    def create_single_offspring(self):
        """
        Creates a new child schedule by mixing the genomes of two parent schedules.

        :return: Schedule object, created from two parents, having been mutated already
        """
        parents = self.select_parents()
        offspring = Schedule(self.course_list, self.classroom_list, self.instructor_list)
        offspring.schedule = self.crossover(parents)
        self.mutate(offspring)

        return offspring

    def form_next_generation(self):
        """
        Creates a child population of schedules of the same size as the parent population. The child and parent schedule
        lists are combined and sorted based on their fitness score. From this combined list, the schedules with the best
        fitness scores are selected to be the next generation, selecting the same number of schedules as in the pevious
        generation.
        """
        # Calculate the fitness score for each schedule in the population
        self.calculated_average_fitness()

        # Create a population of offspring
        offspring = []
        for _ in range(len(self.population)):
            offspring_schedule = self.create_single_offspring()
            offspring.append([self.calculate_fitness(offspring_schedule), offspring_schedule])

        # Add the parent schedules along with their fitness score
        parents = []
        for schedule in self.population:
            parents.append([self.calculate_fitness(schedule), schedule])

        # Sort by fitness score and select the most fit of the parent/child schedules for the next generation
        sorted_by_fitness = sorted(parents + offspring, key=lambda x: x[0], reverse=True)
        next_generation = [sorted_by_fitness[i][1] for i in range(self.POPULATION_SIZE)]

        self.population = next_generation

    def run_optimization(self):
        """
        Runs the genetic algorithm until the last five generations have the same fitness score. Upon completion, the
        final score is displayed.
        """
        generation_num = 0
        fitness_scores = []
        converged = False
        while not converged:
            last_five_scores = fitness_scores[-5:] if len(fitness_scores) >= 5 else []
            converged = True if len(set(last_five_scores)) == 1 else False
            generation_num += 1
            self.form_next_generation()
            fitness_scores.append(self.average_fitness)
            print(f"Generation {generation_num}  -  Fitness Score: {self.average_fitness}")

        print("\n######  FINAL SCHEDULE  ######")
        print(self.population[0].display_phenotype())

if __name__ == "__main__":
    opt = Optimizer()
    opt.run_optimization()