from typing import Annotated

from fastapi import Depends
from fastapi.params import Security
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth import TokenClaims, decode_access_token
from src.db import get_session

TokenDep = Annotated[TokenClaims, Security(decode_access_token)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
