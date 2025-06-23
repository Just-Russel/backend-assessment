from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings


def initialize_middleware(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
