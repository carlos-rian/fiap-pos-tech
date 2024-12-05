from typing import TypeAlias


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
    Represents a resource with an ID and capacity.

    Attributes:
        id (int): The unique identifier of the resource.
        capacity (int): The capacity of the resource.
    """

    def __init__(self, id: int, capacity: int):
        self.id = id
        self.capacity = capacity

    def __repr__(self):
        return f"Resource(id={self.id}, capacity={self.capacity})"


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
