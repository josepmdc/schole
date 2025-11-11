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
      <Link to={`/exercises/${firstExercise.id}`}>
        <Button>Start the first exercise</Button>
      </Link>
    </div>
  );
}
