from typing import TypeAlias


class Task:
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
    def __init__(self, id: int, capacity: int):
        self.id = id
        self.capacity = capacity

    def __repr__(self):
        return f"Resource(id={self.id}, capacity={self.capacity})"


GeneType: TypeAlias = list[int]


# Chromosome representation
class Chromosome:
    def __init__(self, gene: GeneType, fitness: int = 0):
        self.gene = gene  # Gene is a list of task assignments to resources, the values are a random integer between 0 and the number of resources - 1
        self.fitness = fitness

    def __lt__(self, other: "Chromosome"):
        return self.fitness < other.fitness
