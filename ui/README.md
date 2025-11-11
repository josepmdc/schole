# Structure
The most important folder in the `app` folder. In there you can find 3 other folders:
- **components**: Contains reusable components like for example a buttom on the bubble graph.
- **lib**: Contains miscellanious libraries. Currently it contains one library, which is the client auto-generated from the OpenAPI spec. You can find config for the OpenAPI generator at `openapi-ts.config.ts`.
- **routes**: Contains the differnt pages of the app. In `app/routes.ts` you can find the defined routes that link to these pages.

# Makefile
There's a Makefile that you can use to generate the Open API client, run the app or format the code with Prettier.
