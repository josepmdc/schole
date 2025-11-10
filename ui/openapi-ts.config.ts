import { defaultPlugins } from "@hey-api/openapi-ts";

export default {
  input: "../api/spec.yml",
  output: "app/lib/api",
  plugins: [...defaultPlugins, "@hey-api/client-fetch", "@tanstack/react-query"],
};
