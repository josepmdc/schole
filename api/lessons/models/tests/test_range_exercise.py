from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import transaction
from uuid import uuid4

from lessons.models.range_exercise import RangeExercise, RangeExerciseDataPoint, TargetType

class RangeExerciseValidationsTest(TestCase):
    def _create_test_exercise(self, target_type, y_min, y_max) -> RangeExercise:
        """creates a range exercise with sane defaults for testing"""
        return RangeExercise(
            id=uuid4(),
            title="title",
            target_type=target_type,
            target_y_min=y_min,
            target_y_max=y_max,
            description="Test exercise",
            order=1
        )

    def test_target_type_not_set(self):
        """given target_type is not set, a ValidationError is raised"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                target_type="",
                y_min=1.1,
                y_max=1.1,
            ).save()

    def test_lt_ok(self):
        """given target_type is LT, min is set and max is not, it should succeed"""
        self._create_test_exercise(
            target_type=TargetType.LT,
            y_min=2.2,
            y_max=None,
        ).save()

    def test_lt_min_is_none(self):
        """given target_type is LT, min is not set, it should fail"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                target_type=TargetType.LT,
                y_min=None,
                y_max=None,
            ).save()

    def test_lt_max_is_set(self):
        """given target_type is LT and max is set, it should fail"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                target_type=TargetType.LT,
                y_min=2.2,
                y_max=3.2,
            ).save()

    def test_gt_ok(self):
        """given target_type is GT, min is not set and max is set, it should succeed"""
        self._create_test_exercise(
            target_type=TargetType.GT,
            y_min=None,
            y_max=2.2,
        ).save()

    def test_gt_max_is_none(self):
        """given target_type is GT and max is None, a ValidationError is raised"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                target_type=TargetType.GT,
                y_min=None,
                y_max=None,
            ).save()

    def test_gt_min_is_set(self):
        """given target_type is GT and min is set, it should fail"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                target_type=TargetType.GT,
                y_min=2.2,
                y_max=3.2,
            ).save()

    def test_between_ok(self):
        """given target_type is BETWEEN, min is set and max is set, it should succeed"""
        self._create_test_exercise(
            target_type=TargetType.BETWEEN,
            y_min=2.2,
            y_max=3.2,
        ).save()

    def test_between_min_is_none(self):
        """given target_type is BETWEEN and min is None, it should fail"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                target_type=TargetType.BETWEEN,
                y_min=None,
                y_max=3.2,
            ).save()

    def test_between_max_is_none(self):
        """given target_type is BETWEEN and max is None, it should fail"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                target_type=TargetType.BETWEEN,
                y_min=2.2,
                y_max=None,
            ).save()

    def test_min_gt_max(self):
        """given min is greater than max, an error should be returned"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                target_type=TargetType.BETWEEN,
                y_min=3.2,
                y_max=2.2,
            ).save()

    def test_get_data_points(self):
        """given an exercise we can add data point to it"""
        exercise = self._create_test_exercise(TargetType.BETWEEN, 2.2, 4.3)
        data_points = [
            RangeExerciseDataPoint(x=1+i, y=2+i, size=3+i, exercise=exercise)
            for i in range(0, 5)
        ]

        with transaction.atomic():
            exercise.save()
            RangeExerciseDataPoint.objects.bulk_create(data_points)

        res = list(exercise.data_points.all())
        self.assertEqual(res, data_points)
