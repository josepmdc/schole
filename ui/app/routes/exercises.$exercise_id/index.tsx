import { BubblePlot, type Point } from "~/components/graph";
import { useEffect, useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Loading } from "~/components/loading";
import {
  exercisesEvaluateCreateMutation,
  exercisesNextRetrieveOptions,
  exercisesRetrieveOptions,
} from "~/lib/api/@tanstack/react-query.gen";
import { Link, useParams } from "react-router";
import Button from "~/components/button";
import LoadingButton from "~/components/loading-button";

export default function Exercise() {
  const params = useParams() as { exerciseId: string };

  const { data: exercise, isLoading: isExerciseLoading } = useQuery({
    ...exercisesRetrieveOptions({ path: { id: params.exerciseId } }),
  });

  const { data: nextExercise, isLoading: isNextLoading } = useQuery({
    ...exercisesNextRetrieveOptions({ path: { id: params.exerciseId } }),
  });

  const [points, setPoints] = useState<Point[]>([]);

  const [isSolved, setIsSolved] = useState<boolean | null>(null);

  const evaluate = useMutation({
    ...exercisesEvaluateCreateMutation(),
    onSuccess: (res) => setIsSolved(res.is_correct),
    onError: (err) => alert(`Oops something went wrong! ${err.message}`),
  });

  useEffect(() => {
    if (!exercise) {
      return;
    }

    const dataPoints: Point[] = exercise.data_points.map((point) => ({
      id: point.id,
      x: point.x,
      y: point.y,
      size: point.size,
    }));

    setPoints(dataPoints);
    setIsSolved(null);
  }, [exercise]);

  if (isExerciseLoading || isNextLoading) return <Loading />;
  if (!exercise || !nextExercise)
    return <h1>Oops something went wrong. We couldn't find the exercise data</h1>;

  const submit = () => {
    evaluate.mutate({
      path: { id: exercise.id },
      body: {
        solution: points.map((point) => ({
          id: point.id,
          x: point.x,
          y: point.y,
          size: point.size,
        })),
      },
    });
  };

  return (
    <div className="flex h-screen">
      <div className="m-auto flex flex-col min-w-4/6 min-h-2/3">
        <div className="flex flex-col lg:flex-row rounded-lg border border-black shadow m-5">
          <div className="m-10 flex flex-col">
            <div className="grow">
              <h1 className="text-2xl">{exercise.title}</h1>
              <p className="py-4 text-lg">
                Move around the data points to make the range be{" "}
                {exercise.constraint_type == "between" &&
                  `between ${exercise.lower_bound} and ${exercise.upper_bound}`}
                {exercise.constraint_type == "lt" && `less than ${exercise.upper_bound}`}
                {exercise.constraint_type == "gt" && `greater than ${exercise.lower_bound}`}
              </p>
            </div>
            <div className="flex justify-center">
              {isSolved === true && (
                <div className="flex flex-col space-y-6 w-full items-center">
                  <div className="flex flex-col justify-center items-center w-full">
                    <svg
                      className="h-16 w-16 text-green-500 mb-3"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <p className="text-3xl font-extrabold text-gray-900">Success!</p>
                  </div>
                  {nextExercise.id && (
                    <Link to={`/exercises/${nextExercise.id}`} className="w-full">
                      <Button className="bg-blue-200 font-semibold mx-0 w-full">Continue</Button>
                    </Link>
                  )}
                  {!nextExercise.id && (
                    <p className="text-lg font-bold text-gray-900">
                      You've completed all exercises!
                    </p>
                  )}
                </div>
              )}
              {!isSolved && (
                <>
                  <div className="flex flex-col space-y-6 w-full items-center">
                    {isSolved === false && (
                      <div className="flex flex-col justify-center items-center w-full">
                        <p className="text-lg font-bold text-red-400">
                          Oops, not quite there yet. Give it another try
                        </p>
                      </div>
                    )}
                    <LoadingButton
                      className="bg-amber-100 w-full"
                      isLoading={evaluate.isPending}
                      loadingText="Evaluating"
                      onClick={submit}
                    >
                      Submit
                    </LoadingButton>
                  </div>
                </>
              )}
            </div>
          </div>
          <div className="w-full">
            <BubblePlot
              data={points}
              setData={setPoints}
              targets={{ lowerBound: exercise.lower_bound, upperBound: exercise.upper_bound }}
              width={600}
              height={500}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
