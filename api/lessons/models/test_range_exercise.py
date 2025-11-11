from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import transaction
from uuid import uuid4

from lessons.models.range_exercise import RangeExercise, RangeExerciseDataPoint, ConstraintType

class RangeExerciseValidationsTest(TestCase):
    def _create_test_exercise(self, constraint_type, lower_bound, upper_bound, id=uuid4()) -> RangeExercise:
        """creates a range exercise with sane defaults for testing"""
        return RangeExercise(
            id=id,
            title="title",
            constraint_type=constraint_type,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            description="Test exercise",
            order=1
        )

    def test_given_a_exercise_with_the_same_id_integrity_error_is_returned(self):
        """given we try to create a exercise with an ID that already exists, an error is returned"""
        exercise_id = uuid4()

        self._create_test_exercise(
            id=exercise_id,
            constraint_type=ConstraintType.LT,
            lower_bound=None,
            upper_bound=2.2,
        ).save()

        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                id=exercise_id,
                constraint_type=ConstraintType.LT,
                lower_bound=None,
                upper_bound=2.2,
            ).save()

    def test_constraint_type_not_set(self):
        """given constraint_type is not set, a ValidationError is raised"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                constraint_type="",
                lower_bound=1.1,
                upper_bound=1.1,
            ).save()

    def test_lt_ok(self):
        """given constraint_type is LT, lower bound is set and upper bound is not, it should succeed"""
        self._create_test_exercise(
            constraint_type=ConstraintType.LT,
            lower_bound=None,
            upper_bound=2.2,
        ).save()

    def test_lt_uper_is_none(self):
        """given constraint_type is LT, upper bound is not set, it should fail"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                constraint_type=ConstraintType.LT,
                lower_bound=None,
                upper_bound=None,
            ).save()

    def test_lt_lower_is_set(self):
        """given constraint_type is LT and lower bound is set, it should fail"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                constraint_type=ConstraintType.LT,
                lower_bound=2.2,
                upper_bound=3.2,
            ).save()

    def test_gt_ok(self):
        """given constraint_type is GT, upper bound is not set and lower bound is set, it should succeed"""
        self._create_test_exercise(
            constraint_type=ConstraintType.GT,
            lower_bound=2.2,
            upper_bound=None,
        ).save()

    def test_gt_lower_is_none(self):
        """given constraint_type is GT and lower bound is None, a ValidationError is raised"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                constraint_type=ConstraintType.GT,
                upper_bound=None,
                lower_bound=None,
            ).save()

    def test_gt_upper_is_set(self):
        """given constraint_type is GT and lower bound is set, it should fail"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                constraint_type=ConstraintType.GT,
                lower_bound=2.2,
                upper_bound=3.2,
            ).save()

    def test_between_ok(self):
        """given constraint_type is BETWEEN, lower bound is set and upper bound is set, it should succeed"""
        self._create_test_exercise(
            constraint_type=ConstraintType.BETWEEN,
            lower_bound=2.2,
            upper_bound=3.2,
        ).save()

    def test_between_upper_is_none(self):
        """given constraint_type is BETWEEN and upper bound is None, it should fail"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                constraint_type=ConstraintType.BETWEEN,
                lower_bound=2.2,
                upper_bound=None,
            ).save()

    def test_between_lower_is_none(self):
        """given constraint_type is BETWEEN and lower is None, it should fail"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                constraint_type=ConstraintType.BETWEEN,
                lower_bound=None,
                upper_bound=3.2,
            ).save()

    def test_lower_gt_upper(self):
        """given lower bound is greater than upper bound, an error should be returned"""
        with self.assertRaises(ValidationError):
            self._create_test_exercise(
                constraint_type=ConstraintType.BETWEEN,
                lower_bound=3.2,
                upper_bound=2.2,
            ).save()

    def test_get_data_points(self):
        """given an exercise we can add data point to it"""
        exercise = self._create_test_exercise(ConstraintType.BETWEEN, 2.2, 4.3)
        data_points = [
            RangeExerciseDataPoint(x=1+i, y=2+i, size=3+i, exercise=exercise)
            for i in range(0, 5)
        ]

        with transaction.atomic():
            exercise.save()
            RangeExerciseDataPoint.objects.bulk_create(data_points)

        res = list(exercise.data_points.all())
        self.assertEqual(res, data_points)
