from typing import List, cast
from rest_framework import serializers
from exercises.models.range_exercise import ConstraintType
from exercises.services.service import (
    CreateExerciseDto,
    CreateExerciseDataPointDto,
    ExerciseDataPointDto,
    ExerciseResponseDto,
)


class ExerciseDataPointSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    x = serializers.FloatField()
    y = serializers.FloatField()
    size = serializers.FloatField()

    @classmethod
    def from_dto(cls, dto: ExerciseDataPointDto) -> dict:
        return {
            "id": dto.id,
            "x": dto.x,
            "y": dto.y,
            "size": dto.size,
        }


class ExerciseDataPointCreateSerializer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()
    size = serializers.FloatField(min_value=0)


class ExerciseCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    constraint_type = serializers.ChoiceField(
        choices=[ct.value for ct in ConstraintType]
    )
    lower_bound = serializers.FloatField(required=False, allow_null=True)
    upper_bound = serializers.FloatField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)
    points = ExerciseDataPointCreateSerializer(many=True)

class ExerciseCreateManySerializer(serializers.Serializer):
    exercises = ExerciseCreateSerializer(many=True)

    def to_dto(self) -> List[CreateExerciseDto]:
        assert isinstance(self.validated_data, dict)

        data = self.validated_data.copy()

        exercises = []
        for exercise in data["exercises"]:
            exercise["constraint_type"] = ConstraintType(exercise["constraint_type"])
            points = exercise.pop("points")
            exercises.append(CreateExerciseDto(
                **exercise,
                points=[CreateExerciseDataPointDto(**point) for point in points]
            ))

        return exercises


class ExerciseResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    order = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    constraint_type = serializers.CharField()
    constraint_type_display = serializers.CharField()
    lower_bound = serializers.FloatField(allow_null=True)
    upper_bound = serializers.FloatField(allow_null=True)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    data_points = ExerciseDataPointSerializer(many=True)

    @classmethod
    def from_dto(cls, dto: ExerciseResponseDto) -> dict:
        """Convert DTO to serialized data"""
        return {
            "id": dto.id,
            "order": dto.order,
            "title": dto.title,
            "description": dto.description,
            "constraint_type": dto.constraint_type,
            "lower_bound": dto.lower_bound,
            "upper_bound": dto.upper_bound,
            "is_active": dto.is_active,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
            "data_points": [
                ExerciseDataPointSerializer.from_dto(dp) for dp in dto.data_points
            ],
        }


class ExerciseManyResponseSerializer(serializers.Serializer):
    exercises = ExerciseResponseSerializer(many=True)


class EvaluateSolutionSerializer(serializers.Serializer):
    solution = ExerciseDataPointSerializer(many=True)


class EvaluateSolutionResponseSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField()


class NextExerciseSerializer(serializers.Serializer):
    id = serializers.UUIDField(allow_null=True)
