import { BubblePlot, type Point } from "~/components/graph";
import type { Route } from "./+types/home";
import { useEffect, useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  exercisesEvaluateCreateMutation,
  exercisesRetrieveOptions,
} from "~/lib/api/@tanstack/react-query.gen";
import { Loading } from "~/components/loading";

export function meta({}: Route.MetaArgs) {
  return [{ title: "Scholé" }, { name: "description", content: "Welcome to Scholé!" }];
}

export default function Home() {
  let exercise = "879ec138-7bc0-428a-9bf0-75798fb0711e";

  const { data, isLoading } = useQuery({
    ...exercisesRetrieveOptions({ path: { id: exercise } }),
  });

  const [points, setPoints] = useState<Point[]>([]);

  useEffect(() => {
    if (!data) {
      return;
    }

    const dataPoints: Point[] = data.data_points.map((point) => ({
      id: point.id,
      x: point.x,
      y: point.y,
      size: point.size,
    }));

    setPoints(dataPoints);
  }, [data]);

  const evaluate = useMutation({
    ...exercisesEvaluateCreateMutation(),
    onSuccess: (res) => alert(res.is_correct ? "Correct!" : "Try again :("),
    onError: (err) => alert(`Oops something went wrong! ${err.message}`),
  });

  const submit = () => {
    evaluate.mutate({
      path: { id: exercise },
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

  if (isLoading) {
    return <Loading />;
  }

  return (
    <div className="flex h-screen m-5">
      <div className="max-w-full lg:max-w-1/2 m-auto rounded-lg shadow flex flex-col">
        <div className="flex flex-col lg:flex-row">
          <div className="m-10 lg:w-1/3 flex flex-col">
            <div className="grow">
              <h1>Exercise 1</h1>
              <p>Move around the data point to make the range be between 200 and 500</p>
            </div>
            <div className="flex justify-center">
              <button className="p-2 m-2 rounded-lg bg-amber-100" onClick={submit}>
                Sumbit
              </button>
            </div>
          </div>
          <BubblePlot data={points} setData={setPoints} width={500} height={400} />
        </div>
      </div>
    </div>
  );
}
