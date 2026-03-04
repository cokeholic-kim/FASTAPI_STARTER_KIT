from datetime import datetime

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class User(BaseModel):
    """User domain model."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(length=120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
