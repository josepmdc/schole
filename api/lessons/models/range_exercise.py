import enum
import uuid

from typing import TYPE_CHECKING, Never, cast
from django.db import models
from django.core.exceptions import ValidationError

class ConstraintType(enum.StrEnum):
    LT      = "lt"
    GT      = "gt"
    BETWEEN = "between"

def assert_never(arg: Never) -> Never:
    raise ValidationError(f"unexpected constraint_type {arg}")

class RangeExercise(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField()
    constraint_type = models.CharField(max_length=10, choices=[
        (ConstraintType.LT, "less than"),
        (ConstraintType.GT, "greater than"),
        (ConstraintType.BETWEEN, "between"),
    ])
    upper_bound = models.FloatField(null=True, blank=True)
    lower_bound = models.FloatField(null=True, blank=True)

    # this is for helping with type annotations/autocomplete since Django generates it on the fly
    if TYPE_CHECKING: data_points: models.QuerySet['RangeExerciseDataPoint']

    def clean(self) -> None:
        super().clean()

        match cast(ConstraintType, self.constraint_type):
            case ConstraintType.LT:
                if self.upper_bound is None:
                    raise ValidationError("when target type is LT, upper_bound should be set")
                if self.lower_bound is not None:
                    raise ValidationError("when target type is LT, lower_bound should be None")
            case ConstraintType.GT:
                if self.lower_bound is None:
                    raise ValidationError("when target type is GT, lower_bound should be set")
                if self.upper_bound is not None:
                    raise ValidationError("when target type is GT, upper_bound should be None")
            case ConstraintType.BETWEEN:
                if self.lower_bound is None or self.upper_bound is None:
                    raise ValidationError("when target type is BETWEEN, both upper_bound and lower_bound should be set")
                if self.lower_bound > self.upper_bound:
                    raise ValidationError("lower bound can't be greater than upper bound")
            case _ as unexpected:
                # exhaustiveness check
                assert_never(unexpected)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class RangeExerciseDataPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    x = models.FloatField(help_text="x coordinate")
    y = models.FloatField(help_text="y coordinate")
    size = models.FloatField(help_text="Size of the bubble")
    exercise = models.ForeignKey(RangeExercise, on_delete=models.CASCADE, related_name='data_points')
