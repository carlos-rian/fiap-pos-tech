from functools import lru_cache
import random
import pygame
from consts import ScheduleReturnType

SCREEN = None
WIDTH = None
HEIGHT = None
FONT = None
BOLD_FONT = None
BOLD_FONT_TITLE = None


def start_pygame():
    global SCREEN, WIDTH, HEIGHT, FONT, BOLD_FONT, BOLD_FONT_TITLE
    # Initialize Pygame
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


def stop_pygame():
    # Quit Pygame
    pygame.quit()


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


# Function to draw the schedule using Pygame
def draw_schedule(
    schedule: ScheduleReturnType,
    generation: int,
    best_fitness: float,
    total_duration: int,
    last_10_fitness: list[float],
    gen_without_improvement: int = 0,
):
    margin = 150
    BORDER_RGB = (11, 37, 87)
    SCREEN.fill((255, 255, 255))
    resource_height = (HEIGHT - 2 * margin) // (len(schedule) + 1)
    max_time = max(
        [task_info["Finish"] for tasks in schedule.values() for task_info in tasks]
    )
    time_scale = (WIDTH - 2 * margin) / (max_time + 1)

    default = (True, (0, 0, 0))

    # Draw a border around the schedule
    pygame.draw.rect(
        surface=SCREEN,
        color=BORDER_RGB,
        rect=(margin, margin, WIDTH - 2 * margin + 100, HEIGHT - 2 * margin),
        width=4,
        border_radius=6,
    )

    for idx, (resource_id, tasks_info) in enumerate(schedule.items()):
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

    # Display generation and fitness
    # rectangle for generation and fitness
    pygame.draw.rect(
        surface=SCREEN,
        color=BORDER_RGB,
        rect=(margin, 16, 500, 100),
        width=4,
        border_radius=6,
    )

    gen_text = BOLD_FONT_TITLE.render(f"Generation: {generation + 1}", *default)
    fitness_text = BOLD_FONT_TITLE.render(f"Best Fitness: {best_fitness:.4f}", *default)

    total_tasks = sum([len(tasks) for tasks in schedule.values()])
    total_text = BOLD_FONT_TITLE.render(f"Task Total: {total_tasks}", *default)

    pygame.draw.rect(
        surface=SCREEN,
        color=BORDER_RGB,
        rect=(margin + 600, 16, 500, 100),
        width=4,
        border_radius=6,
    )
    gen2_text = BOLD_FONT_TITLE.render(
        f"Generation without improvement: {gen_without_improvement}", *default
    )
    total_duration_text = BOLD_FONT_TITLE.render(
        f"Total duration: {total_duration} secs", *default
    )
    mean_time_text = BOLD_FONT_TITLE.render(
        f"Mean time by tasks: {total_duration / total_tasks:.2f} secs", *default
    )

    TEXT_MARGIN = 20
    SCREEN.blit(gen_text, (margin + TEXT_MARGIN, 20))
    SCREEN.blit(fitness_text, (margin + TEXT_MARGIN, 50))
    SCREEN.blit(gen2_text, (margin + TEXT_MARGIN, 80))

    SCREEN.blit(total_text, (margin + 600 + TEXT_MARGIN, 20))
    SCREEN.blit(total_duration_text, (margin + 600 + TEXT_MARGIN, 50))
    SCREEN.blit(mean_time_text, (margin + 600 + TEXT_MARGIN, 80))

    tasks_by_duration_count = {}
    for resource_id, tasks_info in schedule.items():
        for task_info in tasks_info:
            task = task_info["Task"]
            if task.duration not in tasks_by_duration_count:
                tasks_by_duration_count[task.duration] = 0
            tasks_by_duration_count[task.duration] += 1

    tasks_by_duration_count = dict(sorted(tasks_by_duration_count.items()))

    # Define starting positions and calculate dynamic spacing for horizontal layout
    num_durations = len(tasks_by_duration_count)
    rectangle_width = ((WIDTH - 2 * margin) // num_durations) - 15
    rectangle_height = 30

    # Total width occupied by all rectangles
    total_rect_width = num_durations * rectangle_width

    # Calculate available space for spacing
    available_space = WIDTH - 2 * margin - total_rect_width

    # Calculate spacing between rectangles
    if num_durations > 1:
        spacing_x = available_space / (num_durations + 1)
    else:
        spacing_x = available_space / 2  # Center the single rectangle

    # Enforce minimum spacing if necessary
    min_spacing_x = 20  # Minimum spacing in pixels
    spacing_x = max(spacing_x, min_spacing_x)

    # Starting x position
    rectangle_start_x = margin + spacing_x

    # y position remains the same (placed near the bottom)
    rectangle_y = HEIGHT - 120

    for idx, (duration, count) in enumerate(tasks_by_duration_count.items()):
        # Define rectangle position for horizontal layout
        rectangle_x = rectangle_start_x + idx * (rectangle_width + spacing_x)  # * 0.90

        text = f"Duration {duration} secs: {count}"
        # Draw the rectangle
        color, font_color = create_color(text)
        # Render the duration count text in bold
        duration_text = BOLD_FONT_TITLE.render(text, True, font_color)

        text_width, _ = duration_text.get_size()

        pygame.draw.rect(
            surface=SCREEN,
            color=color,
            rect=(rectangle_x, rectangle_y, rectangle_width, rectangle_height),
            # width=4,
            border_radius=6,
        )

        # Calculate centered text position below the rectangle
        text_x = rectangle_x + (rectangle_width - text_width) / 2
        text_y = rectangle_y

        # Blit the duration text onto the screen
        SCREEN.blit(duration_text, (text_x, text_y))

    draw_last_10_fitness(last_10_fitness)

    pygame.display.update()


def draw_time(time: int):
    BORDER_RGB = (11, 37, 87)
    pygame.draw.rect(
        surface=SCREEN,
        color=BORDER_RGB,
        rect=(WIDTH - 320, 18, 250, 35),
        border_radius=6,
        width=4,
    )
    time_text = BOLD_FONT_TITLE.render(f"Time: {time:.3f} secs", True, (0, 0, 0))
    SCREEN.blit(time_text, (WIDTH - 290, 20))
    pygame.display.update()


def draw_last_10_fitness(last_10_fitness: list[float]):
    margin = 150
    len_fitness = len(last_10_fitness)
    rectangle_width = ((WIDTH - 2 * margin) // len_fitness) - 15
    rectangle_height = 30

    # Total width occupied by all rectangles
    total_rect_width = len_fitness * rectangle_width

    # Calculate available space for spacing
    available_space = WIDTH - 2 * margin - total_rect_width

    # Calculate spacing between rectangles
    if len_fitness > 1:
        spacing_x = available_space / (len_fitness + 1)
    else:
        spacing_x = available_space / 2  # Center the single rectangle

    # Enforce minimum spacing if necessary
    min_spacing_x = 20  # Minimum spacing in pixels
    spacing_x = max(spacing_x, min_spacing_x)

    # Starting x position
    rectangle_start_x = margin + spacing_x
    for idx, fitness in enumerate(sorted(last_10_fitness, reverse=True)):
        rectangle_x = rectangle_start_x
        rectangle_y = HEIGHT - 70
        rectangle_start_x += rectangle_width + spacing_x
        text = f"Fitness top {idx + 1}: {fitness:.4f}"
        color, font_color = create_color(text)
        pygame.draw.rect(
            surface=SCREEN,
            color=color,
            rect=(rectangle_x, rectangle_y, rectangle_width, rectangle_height),
            border_radius=6,
        )
        fitness_text = BOLD_FONT_TITLE.render(text, True, font_color)
        text_width, _ = fitness_text.get_size()

        text_x = rectangle_x + (rectangle_width - text_width) / 2
        text_y = rectangle_y

        SCREEN.blit(fitness_text, (text_x, text_y))
