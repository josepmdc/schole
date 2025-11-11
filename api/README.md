# Setup
```bash
python -m venv venv
source venv/bin/activate[.fish|.csh]
pip install -r requirements.txt
make migrate
```

# Structure
Most of the relevant code is in the "exercises" folder. It follows a simplified version of [DDD](https://en.wikipedia.org/wiki/Domain-driven_design), inspired by the [Django API Domains](https://phalt.github.io/django-api-domains/) style guide.

It contains 3 layers, each layer being a different folder:
- **Model**: Defines the Django model, which is stored in the DB. It contains a little bit of domain logic to make sure the data inserted is valid. It contains unit tests to validate this logic.
- **Service**: Implements the business logic. It's the glue between the API endpoints and the data layer. Accepts DTOs (Data Transfer Objects) as input, which decouples the logic and allows it to be reused by other parts of the system. It contains unit tests to validate the business logic.
- **Views**: Defines the HTTP REST endpoints. Calls the service layer to perform the requested operations. The serializers are defined in a separate serializers folder.

# Makefile
There's a Makefile that allows you to make and run the migrations, generate the Open API spec, run tests, etc.

# Open API spec
- https://josepmdc.pythonanywhere.com/api/schema/swagger-ui/
- https://github.com/josepmdc/schole/blob/master/api/spec.yml
