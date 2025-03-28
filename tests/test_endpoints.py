from datetime import timedelta
from unittest import mock
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from src.auth import TokenClaims, UserRole, encode_token
from src.config import Settings


@pytest.mark.anyio
async def test_about(test_client: AsyncClient) -> None:
    """
    Test the about-endpoint.
    """
    response = await test_client.get("/about")
    assert response.status_code == 200
    assert response.json() == {"description": "Test description", "name": "API template", "version": "1.2.3"}


@pytest.mark.anyio
async def test_health(test_client: AsyncClient) -> None:
    """
    Test the health-endpoint (success).
    """
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


@pytest.mark.anyio
async def test_health_db_error(test_client: AsyncClient) -> None:
    """
    Test the health-endpoint (failure).
    """
    with mock.patch("src.main.ping_db", side_effect=RuntimeError("Database connection error: test")):
        response = await test_client.get("/health")
    assert response.status_code == 500
    assert response.json() == {"code": "database_connection_error", "message": "Database connection error: test"}


@pytest.mark.anyio
async def test_whoami(test_client: AsyncClient, test_settings: Settings) -> None:
    """
    Test the whoami-endpoint: missing token header
    """
    test_settings.jr_jwt_access_token_signing_key = "some_random_signing_key"

    response = await test_client.get("/whoami")
    assert response.status_code == 401
    assert response.json() == {"code": "missing_token", "message": "No token provided"}

    # Generate a valid token
    user_id = uuid4()
    email = "tester@test.com"
    roles = [UserRole.user]
    firebase_uid = "some_firebase_uid"
    token = encode_token(
        claims=TokenClaims(user_id=user_id, email=email, roles=roles, firebase_uid=firebase_uid),
        signing_key=test_settings.jr_jwt_access_token_signing_key,
        ttl=timedelta(minutes=10),
        settings=test_settings,
    )
    response = await test_client.get("/whoami", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {"email": email, "roles": ["user"], "user_id": str(user_id), "firebase_uid": firebase_uid}


@pytest.mark.anyio
async def test_invalid(test_client: AsyncClient) -> None:
    """
    Test if an invalid endpoint returns a 404 error, with the expected error message.
    """

    response = await test_client.get("/invalid")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"code": "unknown_error", "message": "Not Found"}
