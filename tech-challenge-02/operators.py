import random
import numpy as np
from models import Chromosome, Task, Resource, FitnessValue
from logger import logger


def fitness_value(
    chromosome: Chromosome, tasks: list[Task], resources: list[Resource]
) -> FitnessValue:
    """
    Calculate the fitness values of a chromosome based on task durations, priorities, and resource usage.

    Args:
        chromosome (Chromosome): The chromosome representing the task-resource assignments.
        tasks (list[Task]): The list of tasks to be scheduled.
        resources (list[Resource]): The list of available resources.

    Returns:
        FitnessValues: The fitness values of the chromosome.
    """
    resource_times: dict[int, float] = {r.id: 0 for r in resources}
    priority_score = 0

    for task_idx, resource_id in enumerate(chromosome.gene):
        task = tasks[task_idx]
        resource_times[resource_id] += task.duration
        priority_score += task.priority

    makespan = max(resource_times.values())
    # Calculate the standard deviation of resource utilization
    load_balance = np.std(list(resource_times.values()))

    return FitnessValue(makespan, load_balance, priority_score, len(tasks))


# Fitness function
def calculate_fitness(
    chromosome: Chromosome, tasks: list[Task], resources: list[Resource]
) -> float:
    """
    Calculate the fitness of a chromosome based on task durations, priorities, and resource usage.

    Args:
        chromosome (Chromosome): The chromosome representing the task-resource assignments.
        tasks (list[Task]): The list of tasks to be scheduled.
        resources (list[Resource]): The list of available resources.

    Returns:
        float: The fitness value of the chromosome.
    """
    # Calculate total execution time and priority score
    fitness = fitness_value(chromosome, tasks, resources)

    logger.debug(f"Calculated fitness: {fitness}")
    return fitness.fitness


# Selection operator
def selection_by_tournament(
    population: list[Chromosome],
) -> tuple[Chromosome, Chromosome]:
    """
    Select two chromosomes from the population using tournament selection.

    Args:
        population (list[Chromosome]): The population of chromosomes.

    Returns:
        tuple[Chromosome, Chromosome]: The two selected chromosomes.
    """
    # Using tournament selection
    tournament_size = 3
    # select random chromosomes and return the best two
    selected = random.sample(population, tournament_size)
    selected.sort(reverse=True)
    parents = (selected[0], selected[1])
    logger.debug(f"Selected parents using tournament selection: {parents}")
    return parents


def selection_best_chromosome_pair(
    population: list[Chromosome],
) -> tuple[Chromosome, Chromosome]:
    """
    Select two chromosomes from the population based on their best fitness.

    Args:
        population (list[Chromosome]): The population of chromosomes.

    Returns:
        tuple[Chromosome, Chromosome]: The two selected chromosomes.
    """
    # select random chromosomes and return the best two
    selected = sorted(population, reverse=True)
    parents = (selected[0], selected[1])
    logger.debug(f"Selected parents using best chromosome pair: {parents}")
    return parents


# Crossover operator
def crossover(parent1: Chromosome, parent2: Chromosome) -> Chromosome:
    """
    Perform crossover between two parent chromosomes to produce a child chromosome.

    Args:
        parent1 (Chromosome): The first parent chromosome.
        parent2 (Chromosome): The second parent chromosome.

    Returns:
        Chromosome: The child chromosome resulting from the crossover.
    """
    crossover_point = random.randint(1, len(parent1.gene) - 2)
    child_gene = parent1.gene[:crossover_point] + parent2.gene[crossover_point:]
    child = Chromosome(gene=child_gene)
    logger.debug(f"Performed crossover at point {crossover_point}: {child}")
    return child


# Mutation operator
def mutation(chromosome: Chromosome, num_resources: int, mutation_rate: float = 0.01):
    """
    Mutate a chromosome by randomly changing some of its genes.

    Args:
        chromosome (Chromosome): The chromosome to be mutated.
        num_resources (int): The number of available resources.
        mutation_rate (float): The probability of each gene being mutated.

    Returns:
        None
    """
    for i in range(len(chromosome.gene)):
        if random.random() < mutation_rate:
            logger.debug(f"Mutating gene {i} from {chromosome.gene[i]}")
            chromosome.gene[i] = random.randint(0, num_resources - 1)
