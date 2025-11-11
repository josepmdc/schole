from uuid import uuid4
from django.core.exceptions import ValidationError
from django.test import TestCase

from exercises.models.range_exercise import ConstraintType
from exercises.services.service import ExerciseService, CreateExerciseDto, CreateExerciseDataPointDto, ExerciseDataPointDto


class TestExerciseService(TestCase):
    def test_create_exercise(self):
        dto = CreateExerciseDto(
            title="Range Test",
            description="Between 10 and 20",
            constraint_type=ConstraintType.BETWEEN,
            lower_bound=10,
            upper_bound=20,
            points=[
                CreateExerciseDataPointDto(x=1, y=15, size=1),
                CreateExerciseDataPointDto(x=2, y=18, size=1),
            ],
        )

        result = ExerciseService.create_exercises([dto])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, dto.title)
        self.assertEqual(len(result[0].data_points), 2)

        retrieved = ExerciseService.get(result[0].id)
        self.assertEqual(retrieved.id, result[0].id)

    def test_get_exercise(self):
        dto = CreateExerciseDto(
            title="Get Test",
            description="Test get",
            constraint_type=ConstraintType.GT,
            lower_bound=5,
            points=[CreateExerciseDataPointDto(x=1, y=6, size=1)],
        )
        created = ExerciseService.create_exercises([dto])[0]
        retrieved = ExerciseService.get(created.id)
        self.assertEqual(retrieved.id, created.id)

    def test_get_first_and_next(self):
        ex1 = ExerciseService.create_exercises([
            CreateExerciseDto(
                title="First",
                description="first",
                constraint_type=ConstraintType.GT,
                lower_bound=5,
            )
        ])[0]

        ex2 = ExerciseService.create_exercises([
            CreateExerciseDto(
                title="Second",
                description="second",
                constraint_type=ConstraintType.GT,
                lower_bound=5,
            )
        ])[0]

        first = ExerciseService.get_first()
        self.assertEqual(first.id, ex1.id)

        next_id = ExerciseService.get_next(ex1.id)
        self.assertEqual(next_id, ex2.id)
        self.assertIsNone(ExerciseService.get_next(ex2.id))

    def test_evaluate_solution_lt(self):
        ex = ExerciseService.create_exercises([
            CreateExerciseDto(
                title="Eval Test",
                description="less than 20",
                constraint_type=ConstraintType.LT,
                upper_bound=20,
            )
        ])[0]

        valid_solution = [
            ExerciseDataPointDto(id=uuid4(), x=1, y=12, size=1),
            ExerciseDataPointDto(id=uuid4(), x=2, y=13, size=2),
        ]
        self.assertTrue(ExerciseService.evaluate_solution(ex.id, valid_solution))

        invalid_solution = [
            ExerciseDataPointDto(id=uuid4(), x=1, y=21, size=1),
            ExerciseDataPointDto(id=uuid4(), x=2, y=13, size=2),
        ]
        self.assertFalse(ExerciseService.evaluate_solution(ex.id, invalid_solution))

    def test_evaluate_solution_gt(self):
        ex = ExerciseService.create_exercises([
            CreateExerciseDto(
                title="Eval Test",
                description="greater than 20",
                constraint_type=ConstraintType.GT,
                lower_bound=20,
            )
        ])[0]

        valid_solution = [
            ExerciseDataPointDto(id=uuid4(), x=1, y=21, size=1),
            ExerciseDataPointDto(id=uuid4(), x=2, y=31, size=2),
        ]
        self.assertTrue(ExerciseService.evaluate_solution(ex.id, valid_solution))

        invalid_solution = [
            ExerciseDataPointDto(id=uuid4(), x=1, y=22, size=1),
            ExerciseDataPointDto(id=uuid4(), x=2, y=13, size=2),
        ]
        self.assertFalse(ExerciseService.evaluate_solution(ex.id, invalid_solution))

    def test_evaluate_solution_between(self):
        ex = ExerciseService.create_exercises([
            CreateExerciseDto(
                title="Eval Test",
                description="between 10 and 20",
                constraint_type=ConstraintType.BETWEEN,
                lower_bound=10,
                upper_bound=20,
            )
        ])[0]

        valid_solution = [
            ExerciseDataPointDto(id=uuid4(), x=1, y=12, size=1),
            ExerciseDataPointDto(id=uuid4(), x=2, y=13, size=2),
        ]
        self.assertTrue(ExerciseService.evaluate_solution(ex.id, valid_solution))

        invalid_solution = [
            ExerciseDataPointDto(id=uuid4(), x=1, y=21, size=1),
            ExerciseDataPointDto(id=uuid4(), x=2, y=13, size=2),
        ]
        self.assertFalse(ExerciseService.evaluate_solution(ex.id, invalid_solution))

    def test_evaluate_solution_empty(self):
        ex = ExerciseService.create_exercises([
            CreateExerciseDto(
                title="Empty Test",
                description="empty",
                constraint_type=ConstraintType.GT,
                lower_bound=5,
            )
        ])[0]

        with self.assertRaises(ValidationError):
            ExerciseService.evaluate_solution(ex.id, [])
