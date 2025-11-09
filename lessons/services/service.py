from typing import List, Optional, cast

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from lessons.models import RangeExercise
from lessons.models.lesson import Lesson
from lessons.models.range_exercise import RangeExerciseDataPoint, TargetType, assert_never

@dataclass
class RangeExerciseDataPointData:
    """Defines the expected payload structure for a single RangePoint."""
    x: float
    y: float
    size: float

@dataclass
class RangeExerciseData:
    """
    Defines the expected payload structure for creating a RangeExercise
    """
    title: str
    order: int
    description: str
    target_type: TargetType
    target_y_min: Optional[float] = None
    target_y_max: Optional[float] = None
    is_active: bool = True
    
    points: List[RangeExerciseDataPoint] = field(default_factory=list)

def _get_next_lesson_order() -> int:
    max_order = (Lesson.objects
                     # important! we need to lock DB to prevent a race condition
                     .select_for_update()
                     .aggregate(max_order=Max('order'))['max_order'])

    return (max_order or 0) + 1

def create_range_exercise(data: RangeExerciseData) -> RangeExercise:
    if not data.points:
        # Raise Django's ValidationError directly
        raise ValidationError("RangeExercise must contain at least one data point.", code='missing_points')

    with transaction.atomic():
        # TODO: for now all lessons will be appended. It would be good to allow reordering lessons on a separate endpoint
        order = _get_next_lesson_order()

        exercise = RangeExercise(
            id=uuid4(),
            title="title",
            target_type=data.target_type,
            target_y_min=data.target_y_min,
            target_y_max=data.target_y_max,
            description=data.description,
            order=order,
        )

        exercise.save()

        points = [
            RangeExerciseDataPoint(
                x=point.x,
                y=point.y,
                size=point.size,
                exercise=exercise,
            )
            for point in data.points
        ]

        RangeExerciseDataPoint.objects.bulk_create(points)

    return exercise

def evaluate_solution(exercise_id: UUID, solution: List[RangeExerciseDataPointData]):
    y_values = [point.y for point in solution]
    min_y, max_y = min(y_values), max(y_values)

    exercise = RangeExercise.objects.get(id=exercise_id)

    match cast(TargetType, exercise.target_type):
        case TargetType.LT:
            if (target_y_min := exercise.target_y_min) is None:
                raise RuntimeError("DB rule violation: 'target_y_min' was unexpectedly None. Check DB insert logic.")
            return min_y > target_y_min
        case TargetType.GT:
            if (target_y_max := exercise.target_y_max) is None:
                raise RuntimeError("DB rule violation: 'target_y_max' was unexpectedly None. Check DB insert logic.")
            return max_y > target_y_max
        case TargetType.BETWEEN:
            if (target_y_max := exercise.target_y_max) is None:
                raise RuntimeError("DB rule violation: 'target_y_max' was unexpectedly None. Check DB insert logic.")
            if (target_y_min := exercise.target_y_min) is None:
                raise RuntimeError("DB rule violation: 'target_y_min' was unexpectedly None. Check DB insert logic.")
            return min_y <= target_y_min and max_y > target_y_max
        case _ as unexpected:
            # this line will make sure that if a new enum value is added and not
            # handled in the match, the static analyzer will report an error
            assert_never(unexpected)
