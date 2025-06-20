from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import api
from .config import settings as get_settings
from .db import init_db
from .middleware import initialize_middleware
from .model.errors import ErrorCode, ServiceError

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # noqa
    await init_db(get_settings().db_uri)
    yield


app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,
    description=settings.app_description,
    version=settings.version,
    lifespan=lifespan,
)

initialize_middleware(app=app, settings=settings)


@app.exception_handler(StarletteHTTPException)
async def handle_starlette_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    return ServiceError(
        code=ErrorCode.unknown_error,
        message=exc.detail,
    ).to_json_response(status_code=exc.status_code)


@app.exception_handler(ServiceError)
async def handle_service_error(_: Request, exc: ServiceError) -> JSONResponse:
    return exc.to_json_response()


app.include_router(api.router)


def start_server() -> None:
    uvicorn_options: dict[str, Any] = {"host": settings.host, "port": settings.port, "reload": True}
    uvicorn.run("src.main:app", **uvicorn_options)
