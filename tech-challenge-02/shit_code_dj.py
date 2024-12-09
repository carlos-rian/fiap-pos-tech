from itertools import product

class Task:
    def __init__(self, name, duration, priority):
        self.name = name
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

resources = [Resource("Resource 1"), Resource("Resource 2"), Resource("Resource 3"), Resource("Resource 4")]

tasks = [
    Task("Task 1", 2, 3),
    Task("Task 2", 1, 1),
    Task("Task 3", 3, 2),
    Task("Task 4", 2, 3),
    Task("Task 5", 1, 2),
    Task("Task 6", 3, 1),
    Task("Task 7", 2, 2),
    Task("Task 8", 1, 3),
]

# Sort tasks by priority
tasks.sort(key=lambda x: -x.priority)

best_distribution = None
best_max_time = None

# Generate all possible distributions of tasks to resources
for distribution in product(tasks, repeat=len(resources)):
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

# Print out the best distribution
for i in range(len(best_distribution)):
    print(f"{resources[i].name} tasks:")
    print(f"  {best_distribution[i].name}")