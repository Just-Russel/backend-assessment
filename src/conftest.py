import pytest

from .config import Settings
from .config import settings as config_settings


@pytest.fixture
def settings() -> Settings:
    return config_settings().model_copy()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
