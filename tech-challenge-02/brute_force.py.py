from copy import copy, deepcopy
import numpy as np
import itertools


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
        self.tasks: list[Task] = []

    def __repr__(self):
        return f"Resource(id={self.id})"


def generate_tasks(num_tasks: int) -> list[Task]:
    return [
        Task(id=task_id, duration=duration, priority=priority)
        for task_id, duration, priority in zip(
            range(num_tasks),
            np.random.randint(1, 10, num_tasks),
            np.random.randint(1, 5, num_tasks),
        )
    ]


# Generate sample resources
def generate_resources(num_resources: int):
    return [Resource(id=id) for id in range(num_resources)]


def calculate_balance(resources):
    """
    Calculate load balance for the given resources based on task durations.

    Args:
        resources (list[Resource]): List of resources with assigned tasks.

    Returns:
        float: The standard deviation of resource loads.
    """
    resource_loads = [
        sum(task.duration for task in resource.tasks) for resource in resources
    ]
    return np.std(resource_loads)


def distribute_tasks_balanced(tasks, resources):
    """
    Distributes tasks to resources ensuring load balance across resources.

    Args:
        tasks (list[Task]): List of tasks to distribute.
        resources (list[Resource]): List of available resources.

    Returns:
        tuple: Best resources allocation and its load balance score.
    """
    num_resources = len(resources)
    best_allocation = None
    best_score = float("inf")

    # Generate all possible groupings of tasks
    for combination in itertools.combinations(range(len(tasks)), num_resources - 1):
        split_indices = [0] + list(combination) + [len(tasks)]
        task_groups = [
            tasks[split_indices[i] : split_indices[i + 1]] for i in range(num_resources)
        ]

        # Assign groups to resources
        for resource, group in zip(resources, task_groups):
            resource.tasks = group

        # Calculate load balance score
        score = calculate_balance(resources)
        if score < best_score:
            best_score = score
            best_allocation = deepcopy([res.tasks for res in resources])

    return best_allocation, best_score


# Example Usage
tasks = generate_tasks(10)  # 6 tasks for demonstration
resources = generate_resources(5)  # 3 resources


NUM_TASKS = 100
NUM_RESOURCES = 5


def main():
    def randomize():
        ### generated tasks and resources
        # Generate tasks and resources
        tasks = generate_tasks(num_tasks=NUM_TASKS)
        resources = generate_resources(num_resources=NUM_RESOURCES)
        return tasks, resources

    tasks, resources = randomize()
    # randomize()

    best_allocation, best_score = distribute_tasks_balanced(tasks, resources)

    print("Best Allocation:")
    for idx, resource_tasks in enumerate(best_allocation):
        duration = sum(task.duration for task in resource_tasks)
        print(f"Resource:{idx} - Duration: {duration} -> {resource_tasks[:3]}...")

    print(f"Best Balance Score: {best_score}")
