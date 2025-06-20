from typing import Annotated
from uuid import UUID

import aiosqlite
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from src.config import Settings
from src.config import settings as get_settings
from src.model.author import Author
from src.model.errors import ErrorCode, ServiceError
from src.persistence.author import AuthorRepository

router = APIRouter()


@router.get("/author/{author_uuid}", response_model=Author)
async def get_author(
    author_uuid: UUID,
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> Author:
    async with aiosqlite.connect(app_settings.db_uri) as conn:
        author = await AuthorRepository().get(author_uuid, conn)

    if not author:
        raise ServiceError(
            code=ErrorCode.not_found,
            message=f"Author with UUID {author_uuid} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return author


@router.get("/author", response_model=list[Author])
async def get_authors(
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> list[Author]:
    async with aiosqlite.connect(app_settings.db_uri) as conn:
        authors = await AuthorRepository().get_all(conn)
    return authors


@router.post("/author")
async def create_author(
    author: Author,
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> JSONResponse:
    async with aiosqlite.connect(app_settings.db_uri) as conn:
        await AuthorRepository().create(author, conn)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Author created successfully."},
    )
