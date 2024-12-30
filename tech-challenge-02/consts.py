# the list of ids of the tasks assigned to the resource
from typing import Literal, TypeAlias, Union
from models import Task

ScheduleResType: TypeAlias = int
"""Type alias for the resource ID."""

ScheduleKeysType: TypeAlias = Literal["Task", "Start", "Finish"]
"""Type alias for the keys used in the schedule dictionary."""

ScheduleValueType: TypeAlias = Union[Task, int]
"""Type alias for the values used in the schedule dictionary."""

ScheduleReturnType: TypeAlias = dict[
    ScheduleResType, list[dict[ScheduleKeysType, ScheduleValueType]]
]
"""Type alias for the return type of a schedule, which is a dictionary 
mapping resource IDs to a list of dictionaries with keys 'Task', 'Start', and 'Finish'."""
