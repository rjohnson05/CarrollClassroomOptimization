import random
import pandas as pd

from Classroom import Classroom
from Course import Course
from Instructor import Instructor
from Schedule import Schedule


class Optimizer:
    def __init__(self):
        self.POPULATION_SIZE = 20
        self.CROSSOVER_RATE = 0.8
        self.MUTATION_RATE = 0.2

        self.classroom_list, self.course_list, self.instructor_list = self.upload_data()

        # self.classroom_list = ['SIMP-120', 'SIMP-200', 'SIMP-300', 'SIMP-400', 'OCON-123', 'STCH-343', 'STCH-234']
        # self.course_list = ['CS-1', 'CS-2', 'CS-3', 'CS-4', 'CS-5', 'CS61', 'CS-7']
        # self.instructor_list = {"Nate Williams": [1, 2], "Ted Wendt": [3, 4], "Jodi Fasteen": [5, 6, 7]}

        self.population = self.form_population(self.POPULATION_SIZE)
        self.average_fitness = 0
        self.total_fitness = 0

    def upload_data(self):
        classroom_data = pd.read_excel("classroom_info.xlsx", engine="openpyxl")
        course_data = pd.read_excel("schedule.xlsx", engine="openpyxl").dropna(subset=['CSM_BLDG', 'CSM_ROOM'])

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
        # print(classroom_data['CSM_ROOM'])
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

        print(classrooms_list, courses_list, instructors_list)
        return classrooms_list, courses_list, instructors_list

    def form_population(self, pop_size: int):
        population = []
        for i in range(pop_size):
            schedule = Schedule(self.course_list, self.classroom_list, self.instructor_list)
            schedule.create_genome()
            population.append(schedule)
        return population

    def calculate_fitness(self, schedule: Schedule):
        """
        Calculates the "goodness" of a given schedule. Schedules are penalized for using more classrooms and for having
        two courses in the same time blocks that are taught by the same instructor.

        @param: Schedule object to be evaluated
        @return: Fitness score for the Schedule object, with larger scores being better
        """
        # Don't recalculate the fitness if it's already been calculated
        if schedule.fitness != 0:
            return schedule.fitness

        # Penalizes for using more classrooms
        num_classrooms_used = 0
        for classroom in schedule.schedule:
            for time_block in classroom:
                if time_block != -1:
                    num_classrooms_used += 1
                    break
        fitness = 1 / num_classrooms_used

        # Penalizes for assigning an instructor to a time block more than once
        for instructor, course_list in schedule.instructor_list.items():
            # Find the number of courses taught by an instructor during a single time block. Ideal solutions should
            # have a value of 1.
            for i in range(schedule.MONDAY_TIME_SLOTS + schedule.TUESDAY_TIME_SLOTS):
                num_courses_taught = 0
                for classroom in schedule.schedule:
                    if classroom[i] in course_list:
                        num_courses_taught += 1
                # Subtract a fitness point for every time an instructor is assigned more than once to a time block
                if num_courses_taught > 1:
                    fitness -= 1
        # print("Fitness after Penalizing Instructors: ", fitness)

        # Penalizes for not including all courses in the final schedule
        not_all_courses_penalty = 0
        for course_id in range(len(self.course_list)):
            course_found = False
            for classroom in schedule.schedule:
                if course_id in classroom:
                    course_found = True
                    break
            if course_found:
                continue
            fitness -= 1
        # print("Fitness after Penalizing Not all Courses: ", fitness)

        # Penalizes for assigning a course to both MWF and Tth
        for classroom in schedule.schedule:
            for monday_time_block in classroom[0:schedule.MONDAY_TIME_SLOTS]:
                for tuesday_time_block in classroom[schedule.MONDAY_TIME_SLOTS: schedule.TUESDAY_TIME_SLOTS]:
                    if monday_time_block == tuesday_time_block:
                        fitness -= 1
                        break
        # print("Fitness after Penalizing All Days: ", fitness)

        schedule.fitness = fitness
        return fitness

    def assign_selection_probs(self):
        """
        Calculates the probability that each schedule the has of being selected for parenthood, based upon its fitness
        level and the fitness of the population as a whole.
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

        # Calculate the probability that each individual is chosen for parenthood
        for i in range(len(fitness_levels)):
            selection_prob = fitness_levels[i] / total_fitness
            self.population[i].selection_prob = selection_prob

    def tournament_selection(self, size=3):
        # Tournament selection: Randomly select 'size' schedules and return the most fit among them
        selected = random.sample(self.population, size)
        return max(selected, key=lambda x: self.calculate_fitness(x))

    def select_parents(self):
        """
        Selects two parent schedules from the population. A random number probability is then chosen, and two parents
        are selected by roulette wheel selection. In this process, the population is looped through, stopping once the
        sum of the selection probabilities of schedules seen thus far surpasses the randomly generated number. The schedule
        stopped on is selected for parenthood.

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
        used_classrooms_indices = []
        for classroom in schedule.schedule:
            for time_block in classroom:
                if time_block != -1:
                    used_classrooms_indices.append(schedule.schedule.index(classroom))

        # Can't mutate if there aren't at least 2 courses that host courses
        if len(used_classrooms_indices) < 2:
            return

        # Choose 2 used classrooms to mutate
        classroom_index1, classroom_index2 = random.sample(used_classrooms_indices, 2)
        classroom1, classroom2 = schedule.schedule[classroom_index1], schedule.schedule[classroom_index2]

        # Determine which classrooms hosts fewer courses
        lesser_courses_room, greater_courses_room = max([(classroom2, classroom1), (classroom1, classroom2)], key=lambda classroom: classroom[0].count(-1))
        lesser_room_index, greater_room_index = ((classroom_index1, classroom_index2) if classroom1.count(-1) > classroom2.count(-1) else (classroom_index2, classroom_index1))

        # Pick a random course to move to the other classroom
        course_index, course = random.choice([(index, course) for index, course in enumerate(lesser_courses_room) if course != -1])

        # Find an empty slot to move the course to
        course_placement_index = random.choice([index for index, course in enumerate(greater_courses_room) if course == -1])
        lesser_courses_room[course_index] = -1
        greater_courses_room[course_placement_index] = course
        schedule.schedule[lesser_room_index] = lesser_courses_room
        schedule.schedule[greater_room_index] = greater_courses_room

    def create_single_offspring(self):
        """
        Creates a new child schedule by mixing the genomes of two parent schedules.

        :return: Child Schedule object, having been mutated already
        """
        parents = self.select_parents()
        offspring = Schedule(self.course_list, self.classroom_list, self.instructor_list)
        offspring.schedule = self.crossover(parents)
        self.mutate(offspring)

        return offspring

    def form_next_generation(self):
        # Calculate the fitness score for each schedule in the population
        self.assign_selection_probs()

        # Create a population of offspring
        offspring = []
        for _ in range(len(self.population)):
            offspring_schedule = self.create_single_offspring()
            offspring.append([self.calculate_fitness(offspring_schedule), offspring_schedule])

        parents = []
        for schedule in self.population:
            parents.append([self.calculate_fitness(schedule), schedule])

        sorted_by_fitness = sorted(parents + offspring, key=lambda x: x[0], reverse=True)
        # print(sorted_by_fitness[0][1].display_genotype())
        next_generation = [sorted_by_fitness[i][1] for i in range(self.POPULATION_SIZE)]

        self.population = next_generation

    def run_optimization(self):
        generation_num = 0
        for i in range(100):
            self.form_next_generation()
            generation_num += 1
            print(f"Generation {i + 1}  -  Fitness Score: {self.average_fitness}")
        print("Final Schedule:"
              f"{self.population[0].display_phenotype()}")


if __name__ == "__main__":
    opt = Optimizer()
    opt.run_optimization()
