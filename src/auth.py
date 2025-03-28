from calendar import timegm
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from pydantic import BaseModel

from .config import Settings
from .config import settings as get_settings
from .model.errors import ErrorCode, ServiceError

ALGORITHM = "HS256"

jr_service_security = HTTPBearer(auto_error=False)


class UserRole(StrEnum):
    user = "user"  # Customer / end-user
    staff = "staff"  # Just Russel staff
    support = "support"  # Customer Hero
    admin = "admin"  # Tech staff / devs


class TokenClaims(BaseModel):
    """
    The standard claims in a jwt token.
    """

    user_id: UUID
    email: str = ""
    firebase_uid: str = ""
    roles: list[UserRole] = []


def datetime_to_int(dt: datetime) -> int:
    return timegm(dt.utctimetuple())


def encode_token(
    claims: TokenClaims,
    signing_key: str,
    ttl: timedelta,
    settings: Settings,
) -> str:
    """
    Create and return an access token with the provided claims and time-to-live.
    """

    claims_dict = claims.model_dump(mode="json")

    # Add standard claims
    expire = datetime.now(UTC) + ttl
    claims_dict["exp"] = expire
    claims_dict["sub"] = claims_dict["user_id"]
    claims_dict["iss"] = settings.service_url_public
    claims_dict["aud"] = settings.api_host

    token: str = jwt.encode(claims_dict, signing_key, algorithm=ALGORITHM)
    return token


def decode_token(
    token: str,
    signing_key: str,
    settings: Settings,
) -> TokenClaims:
    """
    decode the given token, using the provided signing key
    """
    try:
        payload = jwt.decode(
            token, signing_key, algorithms=[ALGORITHM], audience=settings.api_host, issuer=settings.service_url_public
        )
    except ExpiredSignatureError as e:
        raise ServiceError(
            status_code=status.HTTP_403_FORBIDDEN,
            code=ErrorCode.expired_token,
            message="Token has expired",
        ) from e
    except JWTClaimsError as e:
        raise ServiceError(
            status_code=status.HTTP_403_FORBIDDEN,
            code=ErrorCode.invalid_token_claims,
            message="Token has invalid/missing claims",
        ) from e
    except JWTError as e:
        raise ServiceError(
            status_code=status.HTTP_403_FORBIDDEN,
            code=ErrorCode.invalid_token,
            message="Invalid token",
        ) from e
    try:
        return TokenClaims(**payload)
    except Exception as e:
        raise ServiceError(
            status_code=status.HTTP_403_FORBIDDEN,
            code=ErrorCode.invalid_token_claims,
            message="Token has invalid/missing claims",
        ) from e


def decode_access_token(
    token: Annotated[HTTPAuthorizationCredentials | None, Depends(jr_service_security)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenClaims:
    if not token:
        raise ServiceError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.missing_token,
            message="No token provided",
        )
    signing_key = settings.jr_jwt_access_token_signing_key
    if not signing_key:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCode.missing_signing_key,
            message="No signing key found in service configuration",
        )
    return decode_token(token.credentials, signing_key, settings=settings)
