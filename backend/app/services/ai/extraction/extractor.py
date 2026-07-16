"""
extraction/extractor.py — Pass 1: Extract tasks from a single transcript chunk.

Each returned task is stamped with chunk_id and a stable UUID immediately
after extraction so the identity is immutable before any other layer sees it.
"""

from app.core.logger import get_logger
from .llm import call_llm
from ..processing.identity import TaskIdentityStamper

logger = get_logger(__name__)


def extract_from_chunk(
    chunk: str,
    system_prompt: str,
    team_members: list[str],
    today: str,
    chunk_index: int,
    total_chunks: int,
) -> list[dict]:
    """
    Pass 1 — extract tasks from a single transcript chunk.

    Each returned task is stamped with ``chunk_id`` so that the
    per-chunk validator and the deduplicator can track provenance.
    """
    chunk_header = (
        f"[Transcript segment {chunk_index + 1} of {total_chunks}]\n\n"
        f"Today: {today}\n"
        f"Team members: {', '.join(team_members) if team_members else 'none provided'}\n\n"
        f"Meeting transcript:\n\n{chunk}"
    )

    try:
        data = call_llm(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk_header},
            ]
        )
        tasks = data.get("tasks", [])
        tasks = tasks if isinstance(tasks, list) else []

        # Stamp every task with its source chunk AND a stable identity
        # immediately after extraction so the identity is immutable.
        for t in tasks:
            if isinstance(t, dict):
                t["chunk_id"] = chunk_index
                TaskIdentityStamper.stamp(t, chunk_index, chunk)

        logger.info(
            "[Chunk %d/%d] Extraction -> %d task(s)",
            chunk_index + 1, total_chunks, len(tasks),
        )
        return tasks

    except Exception as e:
        logger.error("[Chunk %d/%d] Extraction FAILED: %s", chunk_index + 1, total_chunks, e)
        return []
