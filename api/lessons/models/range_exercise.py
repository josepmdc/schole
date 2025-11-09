import enum

from typing import TYPE_CHECKING, Never, cast
from django.db import models
from django.core.exceptions import ValidationError

from .lesson import Lesson

class TargetType(enum.StrEnum):
    LT      = "lt"
    GT      = "gt"
    BETWEEN = "between"

def assert_never(arg: Never) -> Never:
    raise ValidationError(f"unexpected target_type {arg}")

class RangeExercise(Lesson):
    TARGET_TYPES = [
        (TargetType.LT, "less than"),
        (TargetType.GT, "greater than"),
        (TargetType.BETWEEN, "between"),
    ]

    description     = models.TextField()
    target_y_min    = models.FloatField(null=True, blank=True)
    target_y_max    = models.FloatField(null=True, blank=True)
    target_type     = models.CharField(max_length=10, choices=TARGET_TYPES)

    # this is for helping with type annotations since Django generates it on the fly
    if TYPE_CHECKING: data_points: models.QuerySet['RangeExerciseDataPoint']

    def clean(self) -> None:
        super().clean()

        match cast(TargetType, self.target_type):
            case TargetType.LT:
                if self.target_y_min is None:
                    raise ValidationError("when target type is LT, target_y_min should be set")
                if self.target_y_max is not None:
                    raise ValidationError("when target type is LT, target_y_max should be None")
            case TargetType.GT:
                if self.target_y_min is not None:
                    raise ValidationError("when target type is GT, target_y_min should be None")
                if self.target_y_max is None:
                    raise ValidationError("when target type is GT, target_y_max should be set")
            case TargetType.BETWEEN:
                if self.target_y_max is None or self.target_y_min is None:
                    raise ValidationError("when target type is BETWEEN, both target_y_min and target_y_max should be set")
                if self.target_y_min > self.target_y_max:
                    raise ValidationError("min target can't be greater than max target")
            case _ as unexpected:
                # this line will make sure that if a new enum value is added and not
                # handled in the match, the static analyzer will report an error
                assert_never(unexpected)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class RangeExerciseDataPoint(models.Model):
    x        = models.FloatField(help_text="x coordinate")
    y        = models.FloatField(help_text="y coordinate")
    size     = models.FloatField(help_text="Size of the bubble")
    exercise = models.ForeignKey(RangeExercise, on_delete=models.CASCADE, related_name='data_points')
