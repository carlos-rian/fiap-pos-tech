from itertools import product
import random
from time import monotonic


class Task:
    sequece: int = 0

    def __init__(self, duration, priority):
        Task.sequece += 1
        self.name = f"Task name {Task.sequece}"
        self.duration = duration
        self.priority = priority


class Resource:
    def __init__(self, name):
        self.name = name
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def get_total_time(self):
        return sum(task.duration for task in self.tasks)


resources = [
    Resource("Resource 1"),
    Resource("Resource 2"),
    Resource("Resource 3"),
    Resource("Resource 4"),
    Resource("Resource 4"),
]

tasks = [
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
    Task(random.randrange(1, 10), random.randrange(1, 5)),
]

# Sort tasks by priority
tasks.sort(key=lambda x: -x.priority)

best_distribution = None
best_max_time = None
MAX_TASKS = 10

start = monotonic()

# Generate all possible distributions of tasks to resources
for distribution in product(tasks[:MAX_TASKS], repeat=len(resources)):
    # Check if all tasks are different
    if len(set(distribution)) != len(resources):
        continue

    # Assign tasks to resources
    for i in range(len(resources)):
        resources[i].tasks = [distribution[i]]

    # Calculate the maximum total time for this distribution
    max_time = max(resource.get_total_time() for resource in resources)

    # If this distribution is better than the current best, update the best distribution
    if best_max_time is None or max_time < best_max_time:
        best_distribution = distribution
        best_max_time = max_time

print(f"Total time: {monotonic() - start:.6f} seconds")
