# Genetic Algorithm for Carroll College Classrooms

This project contains a genetic algorithm with the purpose of creating an ideal course schedule for Carroll College. The algorithm begins by creating many course schedules, with no regard as to whether these 
how good these schedules are. A schedule is created by attempting to assign each course to a time slot within a classroom that is capable of seating all students enrolled in the course. This data is imported from
two Excel sheets provided by Carroll College. However, note that the number of seats is not provided for every classroom used within the course spreadsheet. Since classroom size is vital to creating a feasible
course schedule, only classrooms that have a known size and courses that are currently held within these classrooms were used in this algorithm.

Once several schedules have been created, they are combined to form the initial population. Once the population has been created, the fitness score is calculated for each schedule, using the following goals:
  - No instructor may teach more than one course during a single time block
  - All courses must be included in the final schedule
  - Courses may be assigned as either a MWF or Tth course, but not both
  - Ideal schedules will use less classrooms
Parents are then selected from this population using tournament selection, with more fit schedules being more likely to be chosen. The genomes of the two parents are combined to create a child schedule, which is
then mutated by moving a course from a lesser-used classroom to a greater-used classroom. This mutation has the goal of moving course schedules toward solutions using less classrooms. Many children are created in
this same manner. Once all children have been created, the most fit schedules (including both the original and child schedules) are chosen to form the next generation. The algorithm will continue this process until
the average fitness score of a generation converges upon the same score for five generations. Upon completion, the final course schedule is displayed.

To run this algorithm, clone this repository to your local machine by running *git clone https://github.com/rjohnson05/CarrollClassroomOptimization/tree/main* on your command-line. Next, ensure that you have Python installed
on your machine by running *python --version*. If you have Python installed, you should see something like *Python 3.12.1*, although the version number might differ. If this command throws an error, you can install
Python [here](https://www.python.org/downloads/). Once you have Python installed, navigate to the root directory of this project and run *pip install -r requirements.txt* to install all necessary dependencies. 
Finally, run *py Optimizer.py* to start the algorithm.
