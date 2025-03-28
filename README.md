# Backend developer assessment
This repository contains sample code, representative of production-grade Just Russel platform code.

It's meant to assess a developer's ability to:
- Read and understand existing code.
- Perform code reviews.
- Find and fix bugs based on non-technical reports.
- Implement new features based on a user story.

## Configuring the environment

- Initialize the .env file in the project root:
```
cp .env.example .env
```
- update the `.env` file with project specific values:
```bash
APP_NAME="Test service"
APP_DESCRIPTION="My super cool service"
SERVICE_NAME=test_service
DB_NAME=test_db
DB_USER=db_test_user
DB_PASSWORD=db_test_password
```

- Make sure to have [direnv](https://direnv.net/docs/hook.html) installed.

- Configure direnv to source the `.env` file in the project root:

`~/.config/direnv/direnv.toml`:

```toml
[global]
load_dotenv = true
```

```
direnv allow .
```

## Setting up the development environment

```
make dev-setup
```

## (Re-)Initialize the database

This is executed when running the `make dev-setup` or `make setup` target, but can also be run separately:

```
make init-db
```

## Database migrations

### Check for pending migrations

```
make check-migrations
```

### Generate migrations

```
make generate-migrations
```

### Apply migrations

```
make apply-migrations
```

## Initialize the secrets

This is executed when running the `make dev-setup` or `make setup` target, but can also be run separately:

```
make secrets
```

## Running the app

Running in dev mode using default settings (listening on http://127.0.0.1:8000):
```
uv run fastapi dev src/main.py
```

Running using the configured environment (sourcing .env file):
```
uv run python -m src
```

Or using the makefile
```
make debug
```

Or running in a docker container
```
make run
```

## Common make targets

### Project development environment setup

```
make setup
```

Can be used after cloning the repository to set up the project.
This will create a virtual environment and install the dependencies.

### Check type annotations

```
make type-check
```

Runs mypy on the project src folder.

### Linting the code

```
make lint
```

Perform flakes8 linting on the project src folder (using ruff).

### Format the code

```
make format
```

### Running tests

```
make unit-tests
```
runs pytest on the project src folder.

```
make integration-tests
```
runs pytest on the project tests folder.

```
make tests
```
runs both unit and integration tests.

```
make cov
```
runs both unit and integration tests, and generates a coverage report.

### Docker images

```
make build
```
Builds the docker image from the current codebase.

```
make publish
```
Publishes the docker image to the configured registry.


## Authentication
Authentication is done via signed JWT tokens.
Multiple named signing keys are supported so that keys can be rotated without invalidating existing sessions.
The name of the key used for signing is inserted into the JWT header, so that we know which key to use when validating the token later.
