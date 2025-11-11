import datetime
from typing import List, Optional, cast
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.db.models import Max
from exercises.models import Exercise
from exercises.models.range_exercise import (
    ExerciseDataPoint,
    ConstraintType,
    assert_never,
)


@dataclass
class CreateExerciseDataPointDto:
    x: float
    y: float
    size: float


@dataclass
class ExerciseDataPointDto:
    id: UUID
    x: float
    y: float
    size: float


@dataclass
class CreateExerciseDto:
    title: str
    description: str
    constraint_type: ConstraintType
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    is_active: bool = True

    points: List[CreateExerciseDataPointDto] = field(default_factory=list)


@dataclass
class ExerciseResponseDto:
    id: UUID
    order: int
    title: str
    description: str
    constraint_type: ConstraintType
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    data_points: List[ExerciseDataPointDto]

    @classmethod
    def from_model(cls, exercise: Exercise) -> "ExerciseResponseDto":
        return cls(
            id=exercise.id,
            order=exercise.order,
            title=exercise.title,
            description=exercise.description,
            constraint_type=ConstraintType(exercise.constraint_type),
            lower_bound=exercise.lower_bound,
            upper_bound=exercise.upper_bound,
            is_active=exercise.is_active,
            created_at=exercise.created_at,
            updated_at=exercise.updated_at,
            data_points=[
                ExerciseDataPointDto(
                    id=point.id, x=point.x, y=point.y, size=point.size
                )
                for point in exercise.data_points.all()
            ],
        )


class ExerciseService:
    @staticmethod
    def _get_next_exercise_order() -> int:
        """Get the next order value for exercises, preventing a race condition"""
        max_order = Exercise.objects.select_for_update().aggregate(  # lock DB to prevent a race condition
            max_order=Max("order")
        )[
            "max_order"
        ]
        return (max_order or 0) + 1

    @staticmethod
    def get(exercise_id: UUID) -> ExerciseResponseDto:
        try:
            exercise = Exercise.objects.prefetch_related("data_points").get(
                id=exercise_id
            )
            return ExerciseResponseDto.from_model(exercise)
        except Exercise.DoesNotExist:
            raise ObjectDoesNotExist(f"Exercise with id {exercise_id} not found")

    @staticmethod
    def get_first() -> ExerciseResponseDto:
        exercise = (
            Exercise.objects.prefetch_related("data_points")
            .order_by("order")
            .first()
        )

        if exercise is None:
            raise ObjectDoesNotExist(f"could not find any exercise")

        return ExerciseResponseDto.from_model(exercise)

    @staticmethod
    def get_next(exercise_id: UUID) -> UUID | None:
        current = Exercise.objects.get(id=exercise_id)

        if current is None:
            raise ObjectDoesNotExist(f"Exercise with id {exercise_id} not found")

        next = (
            Exercise.objects.prefetch_related("data_points")
            .filter(order__gt=current.order)
            .order_by("order")
            .values_list("id", flat=True)
            .first()
        )

        if next is None:
            return None
        return next

    @staticmethod
    def create_exercises(
        exercises_req: List[CreateExerciseDto],
    ) -> List[ExerciseResponseDto]:
        exercises: List[ExerciseResponseDto] = []

        with transaction.atomic():
            for exercise_req in exercises_req:
                # TODO: allow exercise reordering, maybe on a separate endpoint
                order = ExerciseService._get_next_exercise_order()

                exercise = Exercise(
                    id=uuid4(),
                    title=exercise_req.title,
                    constraint_type=exercise_req.constraint_type,
                    lower_bound=exercise_req.lower_bound,
                    upper_bound=exercise_req.upper_bound,
                    description=exercise_req.description,
                    is_active=exercise_req.is_active,
                    order=order,
                )

                exercise.save()

                points = [
                    ExerciseDataPoint(
                        x=point.x,
                        y=point.y,
                        size=point.size,
                        exercise=exercise,
                    )
                    for point in exercise_req.points
                ]

                ExerciseDataPoint.objects.bulk_create(points)

                exercise.refresh_from_db()

                exercises.append(ExerciseResponseDto.from_model(exercise))

        return exercises

    @staticmethod
    def evaluate_solution(
        exercise_id: UUID, solution: List[ExerciseDataPointDto]
    ) -> bool:
        if not solution:
            raise ValidationError("Solution must contain at least one data point.")

        y_values = [point.y for point in solution]
        min_y, max_y = min(y_values), max(y_values)

        exercise = Exercise.objects.get(id=exercise_id)

        lower_bound, upper_bound = exercise.lower_bound, exercise.upper_bound

        match cast(ConstraintType, exercise.constraint_type):
            case ConstraintType.LT:
                if upper_bound is None:
                    raise RuntimeError(
                        "invalid data: 'upper_bound' was unexpectedly None"
                    )
                return max_y < upper_bound

            case ConstraintType.GT:
                if lower_bound is None:
                    raise RuntimeError(
                        "invalid data: 'lower_bound' was unexpectedly None"
                    )
                return min_y > lower_bound

            case ConstraintType.BETWEEN:
                if lower_bound is None:
                    raise RuntimeError(
                        "invalid data: 'lower_bound' was unexpectedly None"
                    )
                if upper_bound is None:
                    raise RuntimeError(
                        "invalid data: 'upper_bound' was unexpectedly None"
                    )
                return min_y >= lower_bound and max_y <= upper_bound

            case _ as unexpected:
                assert_never(unexpected)  # exhaustiveness check
