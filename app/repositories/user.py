from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Async repository for user persistence."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, payload: dict) -> User:
        user = User(**payload)
        self._db.add(user)
        await self._db.flush()
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        list_stmt = select(User).order_by(User.id).offset(skip).limit(limit)
        count_stmt = select(func.count(User.id))

        rows = await self._db.execute(list_stmt)
        users = list(rows.scalars().all())

        total = await self._db.scalar(count_stmt)
        return users, (total or 0)

    async def update(self, user: User, payload: dict) -> User:
        for key, value in payload.items():
            if value is not None:
                setattr(user, key, value)

        self._db.add(user)
        await self._db.flush()
        return user

    async def delete(self, user: User) -> None:
        await self._db.delete(user)
        await self._db.flush()
