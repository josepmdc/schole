import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("exercises/:exerciseId", "./routes/exercises.$exercise_id/index.tsx"),
] satisfies RouteConfig;
