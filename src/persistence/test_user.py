import pytest
import pytest_asyncio

from .test_base import db_pool
from .user import User, UserRepository


@pytest_asyncio.fixture
async def user_repository(db_pool):
    repo = UserRepository(db_pool)
    await repo.initialize()
    await repo.clear()
    return repo


@pytest.fixture
def sample_user():
    return User(username="testuser", email="testuser@example.com")


@pytest.mark.asyncio
async def test_create_user(user_repository, sample_user):
    created_user = await user_repository.create(sample_user)
    assert created_user.uuid == sample_user.uuid
    assert created_user.username == sample_user.username
    assert created_user.email == sample_user.email


@pytest.mark.asyncio
async def test_read_user(user_repository, sample_user):
    await user_repository.create(sample_user)
    retrieved_user = await user_repository.get(sample_user.uuid)
    assert retrieved_user is not None
    assert retrieved_user.uuid == sample_user.uuid
    assert retrieved_user.username == sample_user.username
    assert retrieved_user.email == sample_user.email


@pytest.mark.asyncio
async def test_update_user(user_repository, sample_user):
    await user_repository.create(sample_user)

    sample_user.username = "updateduser"
    sample_user.email = "updateduser@example.com"
    updated_user = await user_repository.update(sample_user)
    assert updated_user.username == "updateduser"
    assert updated_user.email == "updateduser@example.com"


@pytest.mark.asyncio
async def test_delete_user(user_repository, sample_user):
    await user_repository.create(sample_user)
    await user_repository.delete(sample_user.uuid)
    deleted_user = await user_repository.get(sample_user.uuid)
    assert deleted_user is None
