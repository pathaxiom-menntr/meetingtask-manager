"""
processing/identity.py — Task Identity Stamper.

Stamps every extracted task with a stable UUID and ownership snapshot
immediately after extraction, before any other pipeline layer sees it.
"""

import uuid

from .deduplicator import _tokenize


class TaskIdentityStamper:
    """
    Stamp every extracted task with a stable, multi-attribute identity
    immediately after extraction.

    Fields added to the task dict
    ------------------------------
    task_uuid            — uuid4 string; immutable for the task's lifetime.
    original_assignee    — snapshot of assignee at extraction time; never changes.
    reassignment_history — list of reassignment event dicts; starts empty.
    transcript_offset    — estimated char offset of the evidence inside the chunk.
    line_number          — estimated line number of the evidence inside the chunk.
    chunk_index          — alias for chunk_id for clarity.
    _title_tokens        — sorted list of stop-word-stripped title tokens (cached).

    This stamper is called once, inside extract_from_chunk, before any other
    pipeline layer sees the task. The identity is then immutable.
    """

    @staticmethod
    def stamp(task: dict, chunk_index: int, chunk_text: str) -> None:
        """Mutate *task* in-place, adding identity fields."""
        # Unique ID
        task["task_uuid"] = str(uuid.uuid4())

        # Ownership snapshot
        task["original_assignee"] = task.get("assignee")
        task["reassignment_history"] = []

        # Transcript position
        evidence = (task.get("evidence") or "").strip()
        if evidence and chunk_text:
            probe = evidence[:20] if len(evidence) >= 20 else evidence
            offset = chunk_text.find(probe)
            if offset == -1:
                offset = 0
            task["transcript_offset"] = offset
            task["line_number"] = chunk_text[:offset].count("\n") + 1
        else:
            task["transcript_offset"] = 0
            task["line_number"] = 0

        task["chunk_index"] = chunk_index  # alias for chunk_id

        # Cached title tokens (sorted list — JSON-serialisable)
        title_tokens = _tokenize(task.get("title") or "")
        task["_title_tokens"] = sorted(title_tokens)
