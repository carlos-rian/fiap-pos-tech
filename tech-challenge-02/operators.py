import random

import numpy as np
from models import Chromosome, Task, Resource


# Fitness function
def calculate_fitness(
    chromosome: Chromosome, tasks: list[Task], resources: list[Resource]
) -> float:
    # Calculate total execution time and priority score
    resource_times: dict[int, float] = {r.id: 0 for r in resources}
    priority_score = 0

    for task_idx, resource_id in enumerate(chromosome.gene):
        task = tasks[task_idx]
        resource_times[resource_id] += task.duration
        priority_score += task.priority

    makespan = max(resource_times.values())
    load_balance = np.std(list(resource_times.values()))

    # Objective: Minimize makespan and load balance, maximize priority score
    fitness = (
        (1 / makespan) + (1 / (1 + load_balance)) + (priority_score / (len(tasks) * 5))
    )
    return fitness


# Selection operator
def selection(population: list[Chromosome]) -> tuple[Chromosome, Chromosome]:
    # Using tournament selection
    tournament_size = 3
    # select random chromosomes and return the best two
    selected = random.sample(population, tournament_size)
    selected.sort(reverse=True)
    return (selected[0], selected[1])


# Crossover operator
def crossover(parent1: Chromosome, parent2: Chromosome) -> Chromosome:
    crossover_point = random.randint(1, len(parent1.gene) - 2)
    child_gene = parent1.gene[:crossover_point] + parent2.gene[crossover_point:]
    return Chromosome(gene=child_gene)


# Mutation operator
def mutation(chromosome: Chromosome, num_resources: int, mutation_rate: float = 0.01):
    for i in range(len(chromosome.gene)):
        if random.random() < mutation_rate:
            chromosome.gene[i] = random.randint(0, num_resources - 1)
