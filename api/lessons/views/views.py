from uuid import UUID
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.core.exceptions import ValidationError as DjangoValidationError, ObjectDoesNotExist

from lessons.serializers.lesson import EvaluateSolutionResponseSerializer, EvaluateSolutionSerializer, NextExerciseSerializer, RangeExerciseCreateSerializer, RangeExerciseResponseSerializer
from lessons.services.service import ExerciseService, RangeExerciseDataPointDto

class RangeExerciseViewSet(viewsets.ViewSet):
    @extend_schema(
        responses=RangeExerciseResponseSerializer,
        description="Get a range exercise by ID"
    )
    def retrieve(self, _, pk: UUID) -> Response:
        try:
            exercise = ExerciseService.get(pk)
            return Response(
                RangeExerciseResponseSerializer.from_dto(exercise),
                status=status.HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            return Response(
                {'error': f'Exercise with id {pk} not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        responses=RangeExerciseResponseSerializer,
        description="Get the first exercise"
    )
    @action(methods=["GET"], url_path="first", detail=False)
    def retrieve_first(self, _) -> Response:
        try:
            exercise = ExerciseService.get_first()
            return Response(
                RangeExerciseResponseSerializer.from_dto(exercise),
                status=status.HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            return Response(
                {'error': f'could not find any exercise'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        responses=NextExerciseSerializer,
        description="Get the next exercise after the current one",
    )
    @action(methods=["GET"], url_path="next", detail=True)
    def retrieve_next(self, _, pk: UUID) -> Response:
        next_id = ExerciseService.get_next(pk)

        data = {
            'id': next_id, 
        }

        return Response(
            data=data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=RangeExerciseCreateSerializer,
        responses=RangeExerciseResponseSerializer,
        description="Create a new range exercise"
    )
    def create(self, request: Request) -> Response:
        try:
            serializer = RangeExerciseCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            assert isinstance(serializer, RangeExerciseCreateSerializer)
            dto = serializer.to_dto()
            exercise = ExerciseService.create_range_exercise(dto)

            return Response(
                RangeExerciseResponseSerializer.from_dto(exercise), 
                status=status.HTTP_201_CREATED,
            )
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        request=EvaluateSolutionSerializer,
        responses=EvaluateSolutionResponseSerializer,
        description="Evaluate an exercise's solution",
    )
    @action(methods=["POST"], url_path="evaluate", detail=True)
    def evaluate(self, req: Request, pk: UUID) -> Response:
        try:
            serializer = EvaluateSolutionSerializer(data=req.data)
            serializer.is_valid(raise_exception=True)

            assert isinstance(serializer.validated_data, dict)

            points = [
                RangeExerciseDataPointDto(**point)
                for point in serializer.validated_data['solution']
            ]

            res = {
                'is_correct': ExerciseService.evaluate_solution(pk, points),
            }

            return Response(
                EvaluateSolutionResponseSerializer(res).data,
                status=status.HTTP_200_OK,
            )

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ObjectDoesNotExist:
            return Response(
                {'error': f'Exercise with id {pk} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
