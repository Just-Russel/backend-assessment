from datetime import datetime

import pytest
import pytest_asyncio

from src.model.post import Post, Reply
from src.model.user import User
from src.persistence.post import PostRepository, ReplyRepository

from .test_base import db_pool
from .test_user import user_repository


@pytest_asyncio.fixture
async def post_repository(db_pool):
    repo = PostRepository(db_pool)
    await repo.initialize()
    await repo.clear()
    return repo


@pytest_asyncio.fixture
async def reply_repository(db_pool):
    repo = ReplyRepository(db_pool)
    await repo.initialize()
    await repo.clear()
    return repo


@pytest.fixture
def sample_user():
    return User(username="john", email="john@example.com")


@pytest_asyncio.fixture
async def sample_post(sample_user, user_repository):
    await user_repository.create(sample_user)
    return Post(
        title="Test Post",
        content="This is a test post.",
        created_at=datetime.now(),
        author_uuid=sample_user.uuid,
    )


@pytest_asyncio.fixture
async def sample_reply(sample_post, sample_user, user_repository):
    await user_repository.create(sample_user)
    return Reply(
        post_uuid=sample_post.uuid,
        reply_uuid=None,
        content="This is a test reply.",
        created_at=datetime.now(),
        author_uuid=sample_user.uuid,
    )


@pytest.mark.asyncio
async def test_create(post_repository, sample_post):
    post_id = await post_repository.create(sample_post)
    assert post_id == sample_post.uuid


@pytest.mark.asyncio
async def test_get(post_repository, sample_post):
    await post_repository.create(sample_post)
    retrieved_post = await post_repository.get(sample_post.uuid)
    assert retrieved_post.title == sample_post.title
    assert retrieved_post.content == sample_post.content


@pytest.mark.asyncio
async def test_delete(post_repository, sample_post):
    await post_repository.create(sample_post)
    await post_repository.delete(sample_post.uuid)
    retrieved_post = await post_repository.get(sample_post.uuid)
    assert retrieved_post is None


@pytest.mark.asyncio
async def test_create(reply_repository, post_repository, sample_post, sample_reply):
    await post_repository.create(sample_post)
    reply_id = await reply_repository.create(sample_reply)
    assert reply_id == sample_reply.uuid


@pytest.mark.asyncio
async def test_get_for_post(reply_repository, post_repository, sample_post, sample_reply):
    await post_repository.create(sample_post)
    await reply_repository.create(sample_reply)
    replies = await reply_repository.get_for_post(sample_post.uuid)
    assert len(replies) == 1
    assert replies[0].content == sample_reply.content


@pytest.mark.asyncio
async def test_delete_reply(reply_repository, post_repository, sample_post, sample_reply):
    await post_repository.create(sample_post)
    await reply_repository.create(sample_reply)
    await reply_repository.delete(sample_reply.uuid)
    replies = await reply_repository.get_for_post(sample_post.uuid)
    assert len(replies) == 0


@pytest.mark.asyncio
async def test_update_reply(reply_repository, post_repository, sample_post, sample_reply):
    await post_repository.create(sample_post)
    await reply_repository.create(sample_reply)
    updated_content = "Updated reply content."
    await reply_repository.update(sample_reply.uuid, updated_content)
    updated_reply = await reply_repository.get(sample_reply.uuid)
    assert updated_reply.content == updated_content
