from typing import TypeAlias
from enum import Enum


class SelectionType(Enum):
    """
    Represents the type of selection method used in the genetic algorithm.
    """

    TOURNAMENT = 1
    BEST_INDIVIDUALS = 2


class Task:
    """
    Represents a task with an ID, duration, and priority.

    Attributes:
        id (int): The unique identifier of the task.
        duration (int): The duration of the task.
        priority (int): The priority of the task.
    """

    def __init__(self, id: int, duration: int, priority: int):
        self.id = id
        self.duration = duration
        self.priority = priority

    def __repr__(self):
        return f"Task(id={self.id}, duration={self.duration}, priority={self.priority})"

    @property
    def name(self):
        return f"T{self.id}({self.duration}:{self.priority})"


# Define the Resource class
class Resource:
    """
    Represents a resource with an ID.

    Attributes:
        id (int): The unique identifier of the resource.
    """

    def __init__(self, id: int):
        self.id = id

    def __repr__(self):
        return f"Resource(id={self.id})"


GeneType: TypeAlias = list[int]


# Chromosome representation
class Chromosome:
    """
    Represents a chromosome in a genetic algorithm, consisting of a gene and a fitness score.

    Attributes:
        gene (GeneType): A list of task assignments to resources.
        fitness (int): The fitness score of the chromosome.
    """

    def __init__(self, gene: GeneType, fitness: int = 0):
        self.gene = gene  # Gene is a list of task assignments to resources, the values are a random integer between 0 and the number of resources - 1
        self.fitness = fitness

    def __lt__(self, other: "Chromosome"):
        return self.fitness < other.fitness


class FitnessValue:
    """
    Represents the fitness of a chromosome in a genetic algorithm.

    Attributes:
        makespan (int): The total time taken to complete all tasks.
        load_balance (float): The standard deviation of resource utilization.
        priority_score (int): The sum of task priorities.
    """

    def __init__(
        self, makespan: int, load_balance: float, priority_score: int, task_len: int
    ):
        self.makespan = makespan
        self.load_balance = load_balance
        self.priority_score = priority_score
        # Objective: Minimize makespan and load balance, maximize priority score
        self.fitness = (
            (1 / makespan)
            + (1 / (1 + load_balance))
            + (priority_score / (task_len * 5))
        )

    def __repr__(self):
        return f"Fitness(makespan={self.makespan}, load_balance={self.load_balance}, priority_score={self.priority_score}, fitness={self.fitness})"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, FitnessValue):
            return False
        return (
            self.makespan == value.makespan
            and self.load_balance == value.load_balance
            and self.priority_score == value.priority_score
        )
