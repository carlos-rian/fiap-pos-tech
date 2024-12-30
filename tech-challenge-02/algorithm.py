# Function to create the schedule with start times for visualization
from time import monotonic, sleep
import pygame
import random
from logger import logger
from collections import deque
from models import Chromosome, Resource, SelectionType, Task
from consts import ScheduleReturnType
from operators import (
    calculate_fitness,
    crossover,
    fitness_value,
    mutation,
    selection_best_chromosome_pair,
    selection_by_tournament,
)
from draw import (
    draw_schedule,
    draw_time,
    draw_solution,
    start_pygame,
    stop_pygame,
)


def create_schedule(
    chromosome: Chromosome, tasks: list[Task], resources: list[Resource]
) -> ScheduleReturnType:
    """
    Create a schedule with start and finish times for each task assigned to resources.

    Args:
        chromosome (Chromosome): The chromosome representing the task-resource assignments.
        tasks (list[Task]): The list of tasks to be scheduled.
        resources (list[Resource]): The list of available resources.

    Returns:
        ScheduleReturnType: A dictionary where keys are resource IDs and values are lists of
                            dictionaries containing task, start time, and finish time.
    """
    schedule = {r.id: [] for r in resources}
    resource_end_times = {r.id: 0 for r in resources}

    for task_idx, resource_id in enumerate(chromosome.gene):
        task = tasks[task_idx]
        start_time = resource_end_times[resource_id]
        finish_time = start_time + task.duration
        schedule[resource_id].append(
            {
                "Task": task,
                "Start": start_time,
                "Finish": finish_time,
            }
        )
        resource_end_times[resource_id] = finish_time

    return schedule


# Genetic Algorithm function with Pygame visualization
def genetic_algorithm(
    tasks: list[Task],
    resources: list[Resource],
    population_size: int,
    generations: int,
    selection_type: SelectionType,
    delay: int = 0.1,
):
    """
    Run a genetic algorithm to optimize task scheduling on resources with Pygame visualization.

    Args:
        tasks (list[Task]): The list of tasks to be scheduled.
        resources (list[Resource]): The list of available resources.
        population_size (int): The size of the population for the genetic algorithm.
        generations (int): The number of generations to run the genetic algorithm.

    Returns:
        Chromosome: The best chromosome found after the specified number of generations.
    """
    start = monotonic()
    num_tasks = len(tasks)
    num_resources = len(resources)
    total_duration = sum([task.duration for task in tasks])
    last_10_best_fitness = deque(maxlen=10)
    last_10_fitness = deque(maxlen=10)

    # Initialize population
    population: list[Chromosome] = []
    selection = (
        selection_by_tournament
        if selection_type == SelectionType.TOURNAMENT
        else selection_best_chromosome_pair
    )

    gen_without_improvement = 0
    last_best_fitness = 0

    for _ in range(population_size):
        gene = [random.randint(0, num_resources - 1) for _ in range(num_tasks)]
        chromosome = Chromosome(gene)
        chromosome.fitness = calculate_fitness(chromosome, tasks, resources)
        population.append(chromosome)

    start_pygame()

    # Evolution process
    for gen in range(generations):
        new_population: list[Chromosome] = []

        # Elitism: Keep the best chromosome
        population.sort(reverse=True)
        new_population.append(population[0])

        while len(new_population) < population_size:
            # Selection
            parent1, parent2 = selection(population=population)

            # Crossover
            child = crossover(parent1=parent1, parent2=parent2)

            # Mutation
            mutation(chromosome=child, num_resources=num_resources)

            # Calculate fitness
            child.fitness = calculate_fitness(
                chromosome=child, tasks=tasks, resources=resources
            )
            new_population.append(child)

        population = new_population

        best_chromosome = max(population, key=lambda c: c.fitness)

        if best_chromosome.fitness <= last_best_fitness:
            gen_without_improvement += 1
        else:
            gen_without_improvement = 0

        last_best_fitness = best_chromosome.fitness

        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return best_chromosome

        # Create schedule with start and finish times
        schedule = create_schedule(best_chromosome, tasks, resources)

        if best_chromosome.fitness not in last_10_best_fitness:
            last_10_best_fitness.append(best_chromosome.fitness)

        # Draw the schedule
        draw_schedule(
            schedule=schedule,
            generation=gen,
            best_fitness=best_chromosome.fitness,
            total_duration=total_duration,
            last_10_fitness=last_10_best_fitness,
            population_size=population_size,
            selection_type=selection_type.name,
            max_generation=generations,
            current_time=monotonic() - start,
            gen_without_improvement=gen_without_improvement,
        )

        fitness = fitness_value(
            chromosome=best_chromosome, tasks=tasks, resources=resources
        )
        if fitness not in last_10_fitness:
            last_10_fitness.append(fitness)

        if fitness.load_balance <= 0.0:
            msg = f"Best solution found at generation: {gen + 1}"
            draw_solution(solution="best", text_value=msg)
            break
        # Control the speed of visualization
        sleep(delay)

    fitness = last_10_fitness[-1]
    if fitness.load_balance > 0.0 and fitness.load_balance < 1:
        msg = "Good solution found, but not the best!"
        draw_solution(solution="good", text_value=msg)

    elif fitness.load_balance >= 1:
        msg = "The solution is not so good!"
        draw_solution(solution="bad", text_value=msg)

    for idx, fitness in enumerate(last_10_fitness):
        logger.info(f"Last Fitness {idx + 1}: {fitness}")

    # write the time in the pygame window
    end = monotonic()
    draw_time(time=end - start)

    sleep(60)
    stop_pygame()
    return best_chromosome
