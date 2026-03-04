"""Example batch job that shares correlation_id with app logs."""
import asyncio
from typing import Iterable, List

from app.core.logging import get_logger
from app.utils.observability import batch_context

logger = get_logger("batch.job")


async def _process_user(user_id: int) -> str:
    """Simulate one unit of batch work."""
    logger.debug("batch.user.process", user_id=user_id)
    await asyncio.sleep(0.01)
    return f"user:{user_id}:done"


async def run_user_sync_batch(
    user_ids: Iterable[int],
    *,
    correlation_id: str | None = None,
) -> List[str]:
    """Run a batch task with `batch_context` so DB/logging correlation is unified."""
    user_ids_list = list(user_ids)
    with batch_context(
        "user-sync", correlation_id=correlation_id, job_type="sync"
    ) as _:
        logger.info("batch.started", total=len(user_ids_list))
        processed = []
        for user_id in user_ids_list:
            logger.info("batch.processed", user_id=user_id)
            processed.append(await _process_user(user_id))
        logger.info("batch.finished", processed_count=len(processed))
        return processed


async def main() -> None:
    await run_user_sync_batch([1, 2, 3], correlation_id="BATCH-0001")


if __name__ == "__main__":
    asyncio.run(main())
