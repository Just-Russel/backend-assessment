from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from freezegun import freeze_time
from jose import jwt

from .auth import TokenClaims, UserRole, datetime_to_int, decode_access_token, decode_token, encode_token
from .config import Settings
from .model.errors import ServiceError


def test_encode_token() -> None:
    current_time = datetime.strptime("2021-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")
    test_settings = Settings()
    with freeze_time(current_time):
        uid = uuid4()
        claims = TokenClaims(user_id=uid, email="user@test.com", roles=[UserRole.user, UserRole.staff])
        signing_key = "test123"
        ttl = timedelta(minutes=30)
        token = encode_token(claims=claims, signing_key=signing_key, ttl=ttl, settings=test_settings)
        assert token
        expires = current_time + ttl

        decoded_claims = jwt.decode(
            token,
            key=signing_key,
            algorithms=["HS256"],
            issuer=test_settings.service_url_public,
            audience=test_settings.api_host,
        )
        assert decoded_claims["sub"] == decoded_claims["user_id"] == str(claims.user_id)
        assert decoded_claims["exp"] == datetime_to_int(expires)
        assert decoded_claims["email"] == claims.email
        assert decoded_claims["roles"] == claims.roles
        assert decoded_claims["iss"] == test_settings.service_url_public
        assert decoded_claims["aud"] == test_settings.api_host


def test_decode_token() -> None:
    current_time = datetime.strptime("2021-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")
    test_settings = Settings()
    str_uid = "d5898164-4156-4fdb-bd15-d7bf9bb5c78a"
    str_roles = ["staff", "admin"]
    email = "admin24@test.com"
    signing_key = "test123"
    with freeze_time(current_time) as mocked_time:
        claims_dict = {
            "user_id": str_uid,
            "email": "admin24@test.com",
            "roles": str_roles,
            "exp": current_time + timedelta(minutes=5),
            "sub": str_uid,
            "iss": test_settings.service_url_public,
            "aud": test_settings.api_host,
        }
        token = jwt.encode(claims_dict, signing_key, algorithm="HS256")

        claims = decode_token(token=token, signing_key=signing_key, settings=test_settings)
        assert claims
        assert claims.user_id == UUID(str_uid)
        assert claims.email == email
        assert claims.roles == [UserRole.staff, UserRole.admin]

        # Token signature expired
        mocked_time.tick(delta=timedelta(minutes=6))
        with pytest.raises(ServiceError) as e:
            decode_token(token=token, signing_key=signing_key, settings=test_settings)
        assert e.value.error_response.code == "expired_token"

        # Token signed with invalid key
        with pytest.raises(ServiceError) as e:
            decode_token(token=token, signing_key="invalid_key", settings=test_settings)
        assert e.value.error_response.code == "invalid_token"

        # Token signed using invalid algorithm
        with pytest.raises(ServiceError) as e:
            decode_token(jwt.encode(claims_dict, signing_key, algorithm="HS512"), signing_key, settings=test_settings)
        assert e.value.error_response.code == "invalid_token"

        # Token is empty
        with pytest.raises(ServiceError) as e:
            decode_token(token="", signing_key=signing_key, settings=test_settings)
        assert e.value.error_response.code == "invalid_token"

        # Token is garbage
        with pytest.raises(ServiceError) as e:
            decode_token(token="gar ba ge", signing_key=signing_key, settings=test_settings)
        assert e.value.error_response.code == "invalid_token"

        # Missing user_id claim
        with pytest.raises(ServiceError) as e:
            decode_token(
                jwt.encode({"email": "user@example.com"}, signing_key, algorithm="HS256"),
                signing_key,
                settings=test_settings,
            )
        assert e.value.error_response.code == "invalid_token_claims"

        # Invalid user_id claim
        with pytest.raises(ServiceError) as e:
            decode_token(
                jwt.encode({"user_id": "blah"}, signing_key, algorithm="HS256"), signing_key, settings=test_settings
            )
        assert e.value.error_response.code == "invalid_token_claims"

        # Invalid roles claim
        with pytest.raises(ServiceError) as e:
            decode_token(
                jwt.encode({"user_id": str_uid, "roles": ["imposter"]}, signing_key, algorithm="HS256"),
                signing_key,
                settings=test_settings,
            )
        assert e.value.error_response.code == "invalid_token_claims"


@freeze_time("2021-01-01 12:00:00")
def test_encode__decode_token() -> None:
    test_settings = Settings()
    claims = TokenClaims(user_id=uuid4(), email="user@test.com", roles=[UserRole.user, UserRole.support])
    signing_key = "test123"
    ttl = timedelta(minutes=1)
    assert (
        decode_token(
            encode_token(claims=claims, signing_key=signing_key, ttl=ttl, settings=test_settings),
            signing_key,
            settings=test_settings,
        )
        == claims
    )


def test_decode_access_token_missing_signing_key() -> None:
    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test_token")
    settings = Settings(jr_jwt_access_token_signing_key="")

    with pytest.raises(ServiceError) as e:
        decode_access_token(token=token, settings=settings)
    assert e.value.error_response.code == "missing_signing_key"
