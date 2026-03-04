from sqlalchemy.exc import IntegrityError

from app.core.exceptions import DuplicateException, NotFound
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreateRequest, UserUpdateRequest


def _is_duplicate_error(exc: IntegrityError) -> bool:
    detail = str(exc).lower()
    orig = exc.orig

    sql_state = getattr(orig, "sqlstate", None)
    if sql_state == "23505":
        return True

    origin_name = getattr(orig, "__class__", None)
    class_name = origin_name.__name__ if origin_name else ""
    if "unique" in class_name.lower():
        return True

    return "unique" in detail or "duplicate key" in detail or "unique constraint" in detail


class UserService:
    """User business logic."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, payload: UserCreateRequest) -> User:
        existing = await self.repository.get_by_email(payload.email)
        if existing is not None:
            raise DuplicateException(message="Email already exists")

        try:
            return await self.repository.create(payload.model_dump())
        except IntegrityError as exc:
            if _is_duplicate_error(exc):
                raise DuplicateException(message="Email already exists")
            raise

    async def get_user(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFound(message="User not found")
        return user

    async def list_users(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        return await self.repository.list(skip=skip, limit=limit)

    async def update_user(self, user_id: int, payload: UserUpdateRequest) -> User:
        user = await self.get_user(user_id)
        return await self.repository.update(user, payload.model_dump(exclude_unset=True))

    async def delete_user(self, user_id: int) -> None:
        user = await self.get_user(user_id)
        await self.repository.delete(user)
