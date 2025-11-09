from django.db import IntegrityError
from django.test import TestCase
from uuid import uuid4
from lessons.models.lesson import Lesson

class LessonModelTest(TestCase):
    def test_given_a_lesson_with_the_same_id_integrity_error_is_returned(self):
        """given we try to create a lesson with an ID that already exists, an error is returned"""
        lesson_id = uuid4()

        Lesson.objects.create(id=lesson_id, order=1).save()

        with self.assertRaises(IntegrityError):
            Lesson.objects.create(id=lesson_id, order=2).save()
