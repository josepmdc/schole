import type { Route } from "./+types/home";
import { useQuery } from "@tanstack/react-query";
import { exercisesFirstRetrieveOptions } from "~/lib/api/@tanstack/react-query.gen";
import { Loading } from "~/components/loading";
import { Link } from "react-router";
import Button from "~/components/button";

export function meta({}: Route.MetaArgs) {
  return [{ title: "Scholé" }, { name: "description", content: "Welcome to Scholé!" }];
}

export default function Home() {
  const { data: firstExercise, isLoading } = useQuery({
    ...exercisesFirstRetrieveOptions(),
  });

  if (isLoading || !firstExercise) {
    return <Loading />;
  }

  return (
    <div>
      <div className="flex h-screen">
        <div className="m-auto flex flex-col lg:max-w-1/3">
          <div className="flex flex-col rounded-lg border border-black shadow-xl m-5 items-center justify-center p-5 lg:p-20 min-w-4/6 min-h-4/6">
            <h1 className="text-2xl font-extrabold p-3">Welcome to Range Explorer!</h1>
            <p className="text-justify text-lg p-3">
              Discover the power of graphs and learn how to understand range in data visualization.
              In this interactive web app, you’ll explore how data points behave on a graph. Your
              task is simple: move the points to match the target range. You’ll get real-time
              feedback and guidance as you experiment.
            </p>
            <h2 className="text-lg font-extrabold p-3">What is the "Range”?</h2>
            <p className="text-justify text-lg p-3">
              The range is the set of possible output values in a graph—basically, the spread of the
              data along the y-axis. By adjusting the points, you’ll see exactly how changes affect
              the range. Ready to dive in?
            </p>
            <Link to={`/exercises/${firstExercise.id}`}>
              <Button className="bg-blue-200">Start with the first exercise</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
