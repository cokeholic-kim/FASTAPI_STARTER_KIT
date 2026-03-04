"""Test fixtures."""
import asyncio
import tempfile
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.main import app
from app.models.base import Base
from app.models import User  # ensure model metadata is loaded for tests


@pytest.fixture(scope="session")
def event_loop():
    """Per-session event loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db_session():
    """Test database session fixture."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path.as_posix()}",
            echo=False,
        )

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        TestSessionLocal = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        yield TestSessionLocal

        await engine.dispose()


@pytest.fixture
async def override_get_db(test_db_session):
    """Override database dependency for app in tests."""

    async def _get_db():
        session = test_db_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client(override_get_db):
    """HTTP test client fixture."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
