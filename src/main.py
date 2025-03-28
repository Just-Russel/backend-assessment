from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any

import uvicorn
from fastapi import Depends, FastAPI, Request, Security
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api import v1
from .auth import TokenClaims, decode_access_token
from .config import Environment, Settings
from .config import settings as get_settings
from .db import get_engine, init_db, ping_db
from .middleware import initialize_middleware
from .model.base import AboutResponse, HealthResponse, WhoAmIResponse
from .model.errors import ErrorCode, ErrorResponse, ServiceError
from .telemetry import initialize_telemetry

settings = get_settings()


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator[None]:  # noqa: ARG001
    await init_db(get_engine())
    yield


# Disable openAPI / swagger / redoc endpoints in production
docs_kwargs: dict[str, Any] = (
    {
        "docs_urls": None,
        "redoc_url": None,
        "openapi_url": None,
    }
    if settings.environment is Environment.production
    else {}
)

app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,
    description=settings.app_description,
    version=settings.version,
    lifespan=lifespan,
    **docs_kwargs,
)

initialize_middleware(app=app, settings=settings)

initialize_telemetry(app=app, settings=settings)


@app.exception_handler(StarletteHTTPException)
async def handle_starlette_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:  # noqa: ARG001
    return ServiceError(
        code=ErrorCode.unknown_error,
        message=exc.detail,
    ).to_json_response(status_code=exc.status_code)


@app.exception_handler(ServiceError)
async def handle_service_error(request: Request, exc: ServiceError) -> JSONResponse:  # noqa: ARG001
    return exc.to_json_response()


app.include_router(v1.router)


@app.get("/about", response_model=AboutResponse)
def get_about(
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> AboutResponse:
    return AboutResponse(
        name=app_settings.app_name,
        description=app_settings.app_description,
        version=app_settings.version,
    )


@app.get("/health", response_model=HealthResponse, responses={500: {"model": ErrorResponse}})
async def get_healthcheck() -> HealthResponse:
    try:
        await ping_db()
    except Exception as e:
        raise ServiceError(ErrorCode.database_connection_error, str(e)) from e
    return HealthResponse()


@app.get("/whoami", response_model=WhoAmIResponse, responses={401: {"model": ErrorResponse}})
def whoami(claims: Annotated[TokenClaims, Security(decode_access_token)]) -> WhoAmIResponse:
    return WhoAmIResponse(**claims.model_dump())


def start_server() -> None:
    uvicorn_options: dict[str, Any] = {
        "host": settings.host,
        "port": settings.port,
        "reload": settings.environment is Environment.development and settings.auto_reload,
        "log_level": settings.log_level_int,
    }
    # Note: below code assumes we always run the code from the project root
    # Qualification of the module is needed to enable the server reloading on code changes
    uvicorn.run("src.main:app", **uvicorn_options)
