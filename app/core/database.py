"""Database initialization and session lifecycle."""
from typing import AsyncGenerator
import time

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.observability import get_correlation_context, sanitize_value

logger = get_logger("app.database")

# DB engine settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# DB session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info["query_start_time"] = time.perf_counter()


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    query_start_time = conn.info.pop("query_start_time", None)
    if query_start_time is None:
        return

    elapsed_ms = (time.perf_counter() - query_start_time) * 1000
    logger.debug(
        "db.query",
        **get_correlation_context(),
        statement=str(statement)[:2000],
        parameters=sanitize_value(parameters),
        duration_ms=round(elapsed_ms, 2),
        rowcount=getattr(cursor, "rowcount", None),
    )


@event.listens_for(engine.sync_engine, "handle_error")
def _handle_db_error(context):
    logger.error(
        "db.query.error",
        **get_correlation_context(),
        statement=str(context.statement)[:2000] if context.statement is not None else None,
        parameters=sanitize_value(context.parameters),
        original_exception=str(context.original_exception),
        is_disconnected=context.is_disconnect,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for request scope."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
