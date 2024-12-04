# the list of ids of the tasks assigned to the resource
from typing import Literal, TypeAlias, Union
from models import Task

ScheduleResType: TypeAlias = int
ScheduleKeysType: TypeAlias = Literal["Task", "Start", "Finish"]
ScheduleValueType: TypeAlias = Union[Task, int]
ScheduleReturnType: TypeAlias = dict[
    ScheduleResType, list[dict[ScheduleKeysType, ScheduleValueType]]
]
