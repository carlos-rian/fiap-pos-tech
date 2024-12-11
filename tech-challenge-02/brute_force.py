from copy import deepcopy
from functools import lru_cache
import random
from time import monotonic
import numpy as np
import itertools
from models import Resource as R, Task
from generator import DEFAULT_TASKS

import pygame


# Define the Resource class
class Resource(R):
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
    count = 0

    # Generate all possible groupings of tasks
    for combination in itertools.combinations(range(len(tasks)), num_resources - 1):
        split_indices = [0] + list(combination) + [len(tasks)]
        task_groups = [
            tasks[split_indices[i] : split_indices[i + 1]] for i in range(num_resources)
        ]

        # Assign groups to resources
        for resource, group in zip(resources, task_groups):
            resource.tasks = group
            count += 1

        # Calculate load balance score
        score = calculate_balance(resources)
        if score < best_score:
            best_score = score
            best_allocation = deepcopy([res.tasks for res in resources])

        count += 1

    return best_allocation, best_score, count


@lru_cache(maxsize=None)
def create_color(text: str) -> tuple:
    random_color = (
        random.randint(00, 255),
        random.randint(00, 255),
        random.randint(00, 255),
    )

    match random_color:
        # recreate the color if it is too light
        case (r, g, b) if r + g + b > 650:
            t = f"{text}{random.randint(0, 10)}"
            color, _ = create_color(t)
        case _:
            color = random_color

    font_color = (255, 255, 255) if sum(color) < 500 else (0, 0, 0)
    return (color, font_color)


def visualize_task_distribution(resources: list[Resource]):
    pygame.init()
    # get display info
    infoObject = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, (infoObject.current_h * 0.7)

    # Define margins as a percentage of screen size
    margin_percentage = 0.05  # 5% margin on each side
    margin_x = int(SCREEN_WIDTH * margin_percentage)
    margin_y = int(SCREEN_HEIGHT * (margin_percentage - 0.02))

    # Calculate WIDTH and HEIGHT based on screen size and margins
    WIDTH = SCREEN_WIDTH - 2 * margin_x
    HEIGHT = SCREEN_HEIGHT - 2 * margin_y
    # Set screen dimensions
    # WIDTH, HEIGHT = 3300, 800
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    # Display title
    pygame.display.set_caption("Task Scheduling Visualization")
    # Get font
    FONT = pygame.font.SysFont("Arial", 16)
    BOLD_FONT = pygame.font.SysFont("Arial", 16, bold=True)
    BOLD_FONT_TITLE = pygame.font.SysFont("Arial", 22, bold=True)

    margin = 150
    BORDER_RGB = (11, 37, 87)
    SCREEN.fill((255, 255, 255))
    resource_height = (HEIGHT - 2 * margin) // (len(resources) + 1)
    time_scale = (
        (WIDTH - 2 * margin)
        / max(sum(task.duration for task in resource.tasks) for resource in resources)
        * 0.95
    )

    # Ensure time_scale is not too large
    time_scale = min(
        time_scale,
        (WIDTH - 2 * margin)
        / max(task.duration for resource in resources for task in resource.tasks),
    )

    default = (True, (0, 0, 0))

    pygame.draw.rect(
        surface=SCREEN,
        color=BORDER_RGB,
        rect=(margin, margin, WIDTH - 2 * margin, HEIGHT - 2 * margin),
        width=4,
        border_radius=6,
    )

    for idx, resource in enumerate(resources):
        resource_id = resource.id
        tasks_info = [
            {"Task": task, "Start": sum(t.duration for t in resource.tasks[:idx])}
            for idx, task in enumerate(resource.tasks)
        ]
        y = margin + (idx + 1) * resource_height
        # ADD BOLD RESOURCE LABEL HERE
        resource_label = BOLD_FONT.render(f"Resource {resource_id}", *default)
        SCREEN.blit(resource_label, (margin + 8, y - resource_height // 5))

        for task_info in tasks_info:
            task = task_info["Task"]
            start = task_info["Start"]
            duration = task.duration
            x = margin + start * time_scale
            width = duration * time_scale

            # Ensure the task width does not exceed the main rectangle

            color, font_color = create_color(task.name)

            pygame.draw.rect(
                surface=SCREEN,
                color=color,
                rect=(
                    x + 100,
                    y - resource_height // 2,
                    width - 1,
                    resource_height - 15,
                ),
                border_radius=6,
            )
            task_label = BOLD_FONT.render(task.name, True, font_color)
            SCREEN.blit(source=task_label, dest=(x + 105, y - resource_height // 2 + 5))

    pygame.display.update()

    pygame.time.delay(5000)
    pygame.quit()


# Example Usage
NUM_TASKS = 30
NUM_RESOURCES = 5

# 10: 0.116 secs
# 20: 0.748 secs
# 30: 4.711 secs
# 40: 15.791 secs
# 50: 43.976 secs
# 60: 92.361 secs
# > 70: demora muito


def main():
    def randomize():
        ### generated tasks and resources
        # Generate tasks and resources
        tasks = generate_tasks(num_tasks=NUM_TASKS)
        resources = generate_resources(num_resources=NUM_RESOURCES)
        return tasks, resources

    tasks, resources = randomize()
    tasks = DEFAULT_TASKS[:NUM_TASKS]
    # randomize()
    start = monotonic()

    best_allocation, best_score, count = distribute_tasks_balanced(tasks, resources)

    best_resource = []

    print("Best Allocation:")
    for idx, resource_tasks in enumerate(best_allocation):
        duration = sum(task.duration for task in resource_tasks)
        print(
            f"Resource:{idx} - Duration: {duration} -> {resource_tasks[:1]}...{len(resource_tasks)}"
        )
        resource = Resource(id=idx)
        resource.tasks = resource_tasks
        best_resource.append(resource)

    print(f"Total Combinations: {count}")
    print(f"Best Balance Score: {best_score}")
    print(f"Time taken: {monotonic() - start} secs")
    visualize_task_distribution(best_resource)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
