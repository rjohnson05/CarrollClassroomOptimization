import random
from pathlib import Path

import pandas as pd
import chardet

from ga_redo.Schedule import Schedule


class Optimizer:
    def __init__(self):
        self.POPULATION_SIZE = 20
        self.CROSSOVER_RATE = 0.8
        self.MUTATION_RATE = 0.2

        # self.classroom_list, self.course_list, self.instructor_list = self.upload_data()

        self.classroom_list = ['SIMP-120', 'SIMP-200', 'SIMP-300', 'SIMP-400', 'OCON-123', 'STCH-343', 'STCH-234']
        self.course_list = ['CS-1', 'CS-1', 'CS-1', 'CS-1', 'CS-1', 'CS-1', 'CS-1', 'CS-1', 'CS-1']
        self.instructor_list = {"Nate Williams": [1, 2], "Ted Wendt": [3, 4], "Jodi Fasteen": [5, 6, 7]}

        self.population = self.form_population(self.POPULATION_SIZE)
        self.average_fitness = 0
        self.total_fitness = 0

    def upload_data(self):
        df = pd.read_excel("schedule.xlsx", engine="openpyxl")

        # Find all unique on-campus classrooms
        location_data = df[["CSM_BLDG", "CSM_ROOM"]].dropna()
        classroom_data = location_data[location_data['CSM_BLDG'] != "OFCP"]
        classroom_names = (classroom_data["CSM_BLDG"] + "-" + classroom_data["CSM_ROOM"]).unique()

        # Find all unique on-campus course names
        course_names = df["SEC_SHORT_TITLE"].unique()

        # Find all unique professor names
        prof_names = df["SEC_FACULTY_INFO"].unique()
        prof_dict = {}
        # for i in range(len(prof_names)):
        #     prof_dict[prof_names[i]] = df["SEC_SHORT_TITLE"][df["SEC_FACULTY_INFO"] == prof_names[i]].unique()
        #     print(f"Uploading Schedule Data: {i/len(prof_names) * 100}% Complete")
        prof_dict = {name: df["SEC_SHORT_TITLE"][df["SEC_FACULTY_INFO"] == name].unique() for name in prof_names}

        return classroom_names, course_names, prof_dict

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
        # Doesn't recalculate the fitness score if it's been calculated previously
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

        all_week_penalty = 0
        # Penalizes for assigning a course to both MWF and Tth
        for classroom in schedule.schedule:
            for monday_time_block in classroom[0:schedule.MONDAY_TIME_SLOTS]:
                for tuesday_time_block in classroom[schedule.MONDAY_TIME_SLOTS: schedule.TUESDAY_TIME_SLOTS]:
                    if monday_time_block == tuesday_time_block:
                        fitness -= 1
                        break
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

        # parents = []
        # for i in range(2):
        #     rand_num = random.uniform(0, 1)
        #     roulette_prob = 0
        #     for schedule in self.population:
        #         roulette_prob += schedule.selection_prob
        #         if roulette_prob > rand_num:
        #             parents.append(schedule)
        #             break
        return parents

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

        # # Combine MWF schedule from 1st parent and Tth schedule from 2nd parent
        # child_genome = []
        # for i in range(len(parent1.schedule)):
        #     num_timeblocks = len(parent1.schedule[i])
        #     monday_schedule = parent1.schedule[i][0:parent1.MONDAY_TIME_SLOTS]
        #     tuesday_schedule = parent2.schedule[i][parent2.MONDAY_TIME_SLOTS:
        #                                            parent2.MONDAY_TIME_SLOTS + parent1.TUESDAY_TIME_SLOTS]
        #     wednesday_schedule = parent1.schedule[i][parent1.MONDAY_TIME_SLOTS + parent1.TUESDAY_TIME_SLOTS:
        #                                              parent1.MONDAY_TIME_SLOTS + parent1.TUESDAY_TIME_SLOTS +
        #                                              parent1.WEDNESDAY_TIME_SLOTS]
        #     thursday_schedule = parent2.schedule[i][parent1.MONDAY_TIME_SLOTS + parent1.TUESDAY_TIME_SLOTS +
        #                                             parent2.WEDNESDAY_TIME_SLOTS:
        #                                             parent2.MONDAY_TIME_SLOTS + parent2.TUESDAY_TIME_SLOTS +
        #                                             parent2.WEDNESDAY_TIME_SLOTS + parent2.THURSDAY_TIME_SLOTS]
        #     friday_schedule = parent1.schedule[i][parent1.MONDAY_TIME_SLOTS + parent1.TUESDAY_TIME_SLOTS +
        #                                           parent1.WEDNESDAY_TIME_SLOTS + parent1.THURSDAY_TIME_SLOTS:
        #                                           parent1.MONDAY_TIME_SLOTS + parent1.TUESDAY_TIME_SLOTS +
        #                                           parent1.WEDNESDAY_TIME_SLOTS + parent1.THURSDAY_TIME_SLOTS +
        #                                           parent1.FRIDAY_TIME_SLOTS]
        #
        #
        #     # parent1_half = parent1.schedule[i][0:(round(num_timeblocks / 2))]
        #     # parent2_half = parent2.schedule[i][(round(num_timeblocks / 2)): num_timeblocks]
        #     child_genome.append(monday_schedule + tuesday_schedule + wednesday_schedule + thursday_schedule + friday_schedule)
        # return child_genome

    def mutate(self, schedule: Schedule):
        """
        Mutates a single schedule genome by swapping the times of two courses placed in a classroom

        :param schedule: Schedule object to be mutated
        """
        if random.random() < self.MUTATION_RATE:
            classroom_index = random.randint(0, len(schedule.schedule) - 1)
            time_block_index1, time_block_index2 = random.sample(range(len(schedule.schedule[classroom_index])), 2)
            schedule.schedule[classroom_index][time_block_index1], schedule.schedule[classroom_index][
                time_block_index2] = (
                schedule.schedule[classroom_index][time_block_index2],
                schedule.schedule[classroom_index][time_block_index1])

            # random_classroom_index = random.randint(0, len(self.classroom_list) - 1)
        # # Pick a random time slot on Monday or Tuesday to mutate
        # both_time_slots = []
        # first_time_slot = random.randint(0, schedule.MONDAY_TIME_SLOTS + schedule.TUESDAY_TIME_SLOTS - 1)
        # # If the chosen time index falls within the time slots for Monday, the other time slot to mutate must be on
        # # Monday
        # if first_time_slot < schedule.MONDAY_TIME_SLOTS:
        #     second_time_slot = first_time_slot
        #     while second_time_slot == first_time_slot:
        #         second_time_slot = random.randint(0, schedule.MONDAY_TIME_SLOTS - 1)
        #     # Find the corresponding time slots on Wednesday & Friday for the two chosen Monday time slots
        #     for time_slot in [first_time_slot, second_time_slot]:
        #         monday_slot_index = time_slot
        #         wednesday_slot_index = monday_slot_index + (
        #                 schedule.MONDAY_TIME_SLOTS - monday_slot_index) + schedule.TUESDAY_TIME_SLOTS + monday_slot_index
        #         friday_slot_index = wednesday_slot_index + (
        #                 schedule.WEDNESDAY_TIME_SLOTS - monday_slot_index) + schedule.THURSDAY_TIME_SLOTS + monday_slot_index
        #         time_slot_list = [monday_slot_index, wednesday_slot_index, friday_slot_index]
        #         both_time_slots.append(time_slot_list)
        #
        # # If the chosen time index falls within the time slots for Tuesday, the other time slot to mutate must be on
        # # Tuesday
        # elif first_time_slot < schedule.MONDAY_TIME_SLOTS + schedule.TUESDAY_TIME_SLOTS:
        #     second_time_slot = first_time_slot
        #     while second_time_slot == first_time_slot:
        #         second_time_slot = random.randint(schedule.MONDAY_TIME_SLOTS,
        #                                           schedule.MONDAY_TIME_SLOTS + schedule.TUESDAY_TIME_SLOTS - 1)
        #     # Find the corresponding time slots on Wednesday & Friday for the two chosen Monday time slots
        #     for time_slot in [first_time_slot, second_time_slot]:
        #         tuesday_slot_index = time_slot
        #         thursday_slot_index = (
        #                 tuesday_slot_index + (
        #                 schedule.TUESDAY_TIME_SLOTS - (tuesday_slot_index - schedule.MONDAY_TIME_SLOTS)) +
        #                 schedule.WEDNESDAY_TIME_SLOTS + (tuesday_slot_index - schedule.MONDAY_TIME_SLOTS))
        #         time_slot_list = [tuesday_slot_index, thursday_slot_index]
        #         both_time_slots.append(time_slot_list)
        #
        # # Swap the courses for the two randomly chosen time slots
        # for time_slot_index in range(len(both_time_slots[0])):
        #     second_time_slot_course = schedule.schedule[random_classroom_index][both_time_slots[1][time_slot_index]]
        #     first_time_slot_course = schedule.schedule[random_classroom_index][both_time_slots[0][time_slot_index]]
        #     schedule.schedule[random_classroom_index][both_time_slots[1][time_slot_index]] = schedule.schedule[random_classroom_index][both_time_slots[0][time_slot_index]]
        #     schedule.schedule[random_classroom_index][both_time_slots[0][time_slot_index]] = second_time_slot_course

    def create_single_offspring(self):
        """
        Creates a new child schedule by mixing the genomes of two parent schedules.

        :return: Child Schedule object, having been mutated already
        """
        parents = self.select_parents()
        offspring = Schedule(self.course_list, self.classroom_list, self.instructor_list)
        offspring.schedule = self.crossover(parents)
        self.mutate(offspring)
        print(offspring.display_phenotype())
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
