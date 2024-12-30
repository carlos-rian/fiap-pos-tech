from generator import (
    generate_resources,
    generate_tasks,
    DEFAULT_TASKS,
    DEFAULT_RESOURCES,
)
from algorithm import genetic_algorithm
from models import SelectionType
from logger import logger
import logging


GENERATIONS = 500
POPULATION_SIZE = 10
MUTATION_RATE = 0.001

NUM_TASKS = 500
NUM_RESOURCES = 6

VISUALIZATION_DELAY = 0.03


def main():
    """
    Run the genetic algorithm to find the best chromosome for the given tasks and resources.

    This function first runs the algorithm with default tasks and resources, then prints the best fitness and chromosome.
    It then generates new tasks and resources, runs the algorithm again, and prints the results.
    """

    logging.basicConfig(level=logging.INFO)

    SELECTION_TYPE = SelectionType.BEST_INDIVIDUALS

    def default():
        ### default tasks and resources
        best_chromosome = genetic_algorithm(
            tasks=DEFAULT_TASKS,
            resources=DEFAULT_RESOURCES,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
            selection_type=SELECTION_TYPE,
            delay=VISUALIZATION_DELAY,
        )

        logger.info(f"Best fitness: {best_chromosome.fitness}")
        logger.info(f"Best chromosome: {best_chromosome.gene}")

    def randomize():
        ### generated tasks and resources
        # Generate tasks and resources
        tasks = generate_tasks(num_tasks=NUM_TASKS)
        resources = generate_resources(num_resources=NUM_RESOURCES)

        # Run the genetic algorithm
        best_chromosome = genetic_algorithm(
            tasks=tasks,
            resources=resources,
            population_size=POPULATION_SIZE,
            generations=GENERATIONS,
            selection_type=SELECTION_TYPE,
            delay=VISUALIZATION_DELAY,
        )
        print(f"Best fitness: {best_chromosome.fitness}")
        print(f"Best chromosome: {best_chromosome.gene}")

    # default()
    randomize()


if __name__ == "__main__":
    import pygame

    try:
        main()

    except KeyboardInterrupt:
        print("Process interrupted by user.")
        pygame.quit()

    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
