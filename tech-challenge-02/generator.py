import random
from models import Task, Resource


def generate_tasks(num_tasks: int) -> list[Task]:
    """
    Generate a list of tasks with random durations and priorities.

    Args:
        num_tasks (int): The number of tasks to generate.

    Returns:
        list[Task]: A list of generated Task objects.
    """
    tasks = []
    for task_id in range(num_tasks):
        # Task duration between 1 and 10 units
        duration = random.randint(1, 10)
        # Priority between 1 (lowest) and 5 (highest)
        priority = random.randint(1, 5)
        tasks.append(Task(id=task_id, duration=duration, priority=priority))
    return tasks


# Generate sample resources
def generate_resources(num_resources: int):
    """
    Generate a list of resources

    Args:
        num_resources (int): The number of resources to generate.

    Returns:
        list[Resource]: A list of generated Resource objects.
    """
    return [Resource(id=id) for id in range(num_resources)]


DEFAULT_RESOURCES = [
    Resource(id=0),
    Resource(id=1),
    Resource(id=2),
    Resource(id=3),
    Resource(id=4),
]
"""List[Resource]: A default list of resources."""


DEFAULT_TASKS = [
    Task(id=0, duration=1, priority=1),
    Task(id=1, duration=2, priority=2),
    Task(id=2, duration=3, priority=3),
    Task(id=3, duration=4, priority=4),
    Task(id=4, duration=5, priority=5),
    Task(id=5, duration=6, priority=1),
    Task(id=6, duration=7, priority=2),
    Task(id=7, duration=1, priority=3),
    Task(id=8, duration=9, priority=4),
    Task(id=9, duration=10, priority=5),
    Task(id=10, duration=1, priority=1),
    Task(id=11, duration=2, priority=2),
    Task(id=12, duration=3, priority=3),
    Task(id=13, duration=4, priority=4),
    Task(id=14, duration=5, priority=5),
    Task(id=15, duration=6, priority=1),
    Task(id=16, duration=7, priority=2),
    Task(id=17, duration=1, priority=3),
    Task(id=18, duration=9, priority=4),
    Task(id=19, duration=10, priority=5),
    Task(id=20, duration=1, priority=1),
    Task(id=21, duration=2, priority=2),
    Task(id=22, duration=3, priority=3),
    Task(id=23, duration=4, priority=4),
    Task(id=24, duration=5, priority=5),
    Task(id=25, duration=6, priority=1),
    Task(id=26, duration=7, priority=2),
    Task(id=27, duration=1, priority=3),
    Task(id=28, duration=9, priority=4),
    Task(id=29, duration=10, priority=5),
    Task(id=30, duration=1, priority=1),
    Task(id=31, duration=2, priority=2),
    Task(id=32, duration=3, priority=3),
    Task(id=33, duration=4, priority=4),
    Task(id=34, duration=5, priority=5),
    Task(id=35, duration=6, priority=1),
    Task(id=36, duration=7, priority=2),
    Task(id=37, duration=8, priority=3),
    Task(id=38, duration=9, priority=4),
    Task(id=39, duration=10, priority=5),
    Task(id=40, duration=1, priority=1),
    Task(id=41, duration=2, priority=2),
    Task(id=42, duration=3, priority=3),
    Task(id=43, duration=4, priority=4),
    Task(id=44, duration=5, priority=5),
    Task(id=45, duration=6, priority=1),
    Task(id=46, duration=7, priority=2),
    Task(id=47, duration=4, priority=3),
    Task(id=48, duration=8, priority=4),
    Task(id=49, duration=10, priority=5),
    Task(id=50, duration=1, priority=1),
    Task(id=51, duration=2, priority=2),
    Task(id=52, duration=3, priority=3),
    Task(id=53, duration=4, priority=4),
    Task(id=54, duration=4, priority=5),
    Task(id=55, duration=6, priority=1),
    Task(id=56, duration=7, priority=2),
    Task(id=57, duration=8, priority=3),
    Task(id=58, duration=8, priority=4),
    Task(id=59, duration=10, priority=5),
    Task(id=60, duration=1, priority=1),
    Task(id=61, duration=2, priority=2),
    Task(id=62, duration=3, priority=3),
    Task(id=63, duration=4, priority=4),
    Task(id=64, duration=5, priority=5),
    Task(id=65, duration=6, priority=1),
    Task(id=66, duration=7, priority=2),
    Task(id=67, duration=8, priority=3),
    Task(id=68, duration=8, priority=4),
    Task(id=69, duration=10, priority=5),
    Task(id=70, duration=1, priority=1),
    Task(id=71, duration=2, priority=2),
    Task(id=72, duration=3, priority=3),
    Task(id=73, duration=4, priority=4),
    Task(id=74, duration=5, priority=5),
    Task(id=75, duration=6, priority=1),
    Task(id=76, duration=7, priority=2),
    Task(id=77, duration=3, priority=3),
    Task(id=78, duration=9, priority=4),
    Task(id=79, duration=10, priority=5),
    Task(id=80, duration=1, priority=1),
    Task(id=81, duration=2, priority=2),
    Task(id=82, duration=3, priority=3),
    Task(id=83, duration=4, priority=4),
    Task(id=84, duration=5, priority=5),
    Task(id=85, duration=6, priority=1),
    Task(id=86, duration=7, priority=2),
    Task(id=87, duration=3, priority=3),
    Task(id=88, duration=9, priority=4),
    Task(id=89, duration=2, priority=5),
    Task(id=90, duration=1, priority=1),
    Task(id=91, duration=2, priority=2),
    Task(id=92, duration=3, priority=3),
    Task(id=93, duration=4, priority=4),
    Task(id=94, duration=5, priority=5),
    Task(id=95, duration=6, priority=1),
    Task(id=96, duration=7, priority=2),
    Task(id=97, duration=3, priority=3),
    Task(id=98, duration=9, priority=4),
    Task(id=99, duration=2, priority=5),
    Task(id=100, duration=2, priority=5),
    Task(id=101, duration=1, priority=4),
    Task(id=102, duration=2, priority=2),
    Task(id=103, duration=2, priority=5),
    Task(id=106, duration=4, priority=3),
    Task(id=107, duration=1, priority=1),
    Task(id=108, duration=2, priority=4),
    Task(id=109, duration=1, priority=3),
]
"""List[Task]: A default list of tasks with varying durations and priorities."""
