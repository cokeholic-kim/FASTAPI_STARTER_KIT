import pytest
from sqlalchemy.exc import IntegrityError
from unittest.mock import AsyncMock

from app.core.exceptions import DuplicateException
from app.schemas.user import UserCreateRequest
from app.services.user import UserService


@pytest.mark.asyncio
async def test_create_user_success_with_new_email():
    payload = UserCreateRequest(email="new@example.com", name="Alice")
    repository = AsyncMock()
    repository.get_by_email.return_value = None
    repository.create.return_value = AsyncMock(
        id=1,
        email="new@example.com",
        name="Alice",
        is_active=True,
    )

    service = UserService(repository)
    user = await service.create_user(payload)

    assert user.email == "new@example.com"
    repository.get_by_email.assert_awaited_once_with("new@example.com")
    repository.create.assert_awaited_once_with(payload.model_dump())


@pytest.mark.asyncio
async def test_create_user_duplicate_email_is_rejected():
    payload = UserCreateRequest(email="dup@example.com", name="Bob")
    repository = AsyncMock()
    repository.get_by_email.return_value = True

    service = UserService(repository)

    with pytest.raises(DuplicateException) as exc_info:
        await service.create_user(payload)

    assert exc_info.value.error_code == "DUPLICATE"
    repository.create.assert_not_awaited()


class _DuplicateOrigin(Exception):
    sqlstate = "23505"


@pytest.mark.asyncio
async def test_create_user_duplicate_constraint_is_mapped_to_domain_error():
    payload = UserCreateRequest(email="concurrent@example.com", name="Concurrent")
    repository = AsyncMock()
    repository.get_by_email.return_value = None
    repository.create.side_effect = IntegrityError(
        "insert",
        "params",
        _DuplicateOrigin("duplicate key"),
    )

    service = UserService(repository)

    with pytest.raises(DuplicateException) as exc_info:
        await service.create_user(payload)

    assert exc_info.value.error_code == "DUPLICATE"
    assert "Email already exists" in exc_info.value.message
