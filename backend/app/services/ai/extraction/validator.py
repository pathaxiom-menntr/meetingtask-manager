"""
extraction/validator.py — Pass 2: Per-chunk auditor.

Key architectural guarantees:
1. The validator ONLY sees tasks from THIS chunk and the FULL text of THIS
   chunk — never a truncated global sample.
2. A 10% safety threshold: if the validated list is too small, discard the
   validation result and return the original raw extraction.
3. If the LLM call fails for any reason, the original tasks are returned
   unchanged.
"""

from app.core.logger import get_logger
from .llm import call_llm
from ..config import VALIDATION_PASS_ENABLED, VALIDATION_SAFETY_THRESHOLD
from ..prompts.validation import build_chunk_validation_prompt

logger = get_logger(__name__)


def validate_chunk(
    raw_tasks: list[dict],
    chunk_transcript: str,
    team_members: list[str],
    today: str,
    chunk_index: int,
    total_chunks: int,
) -> list[dict]:
    """
    Per-chunk auditor (Pass 2).

    Reviews the extracted tasks conservatively — fixes errors, never
    bulk-deletes. Falls back to raw_tasks if the LLM removes too many.
    """
    if not VALIDATION_PASS_ENABLED or not raw_tasks:
        return raw_tasks

    validation_prompt = build_chunk_validation_prompt(
        team_members=team_members,
        today=today,
        extracted_tasks=raw_tasks,
        chunk_transcript=chunk_transcript,
        chunk_index=chunk_index,
        total_chunks=total_chunks,
    )

    try:
        data = call_llm(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a conservative AI auditor for meeting task extraction. "
                        "Your primary obligation is to PRESERVE tasks, not remove them. "
                        "Return only valid JSON."
                    ),
                },
                {"role": "user", "content": validation_prompt},
            ],
            temperature=0.0,
        )
        validated = data.get("tasks", [])
        if not isinstance(validated, list):
            logger.warning(
                "[Chunk %d/%d] Validator returned non-list — using raw extraction",
                chunk_index + 1, total_chunks,
            )
            return raw_tasks

        raw_n = len(raw_tasks)
        val_n = len(validated)
        removed = raw_n - val_n
        corrected = sum(
            1 for i, t in enumerate(validated)
            if i < len(raw_tasks) and t.get("title") != raw_tasks[i].get("title")
        )
        added = max(0, val_n - raw_n)

        logger.info(
            "[Chunk %d/%d] Validation — extracted: %d | validated: %d | "
            "removed: %d | corrected: ~%d | added: %d",
            chunk_index + 1, total_chunks,
            raw_n, val_n, max(0, removed), corrected, added,
        )

        # Safety threshold: if the validator removed too many tasks, discard
        # the validation and keep the originals.
        if raw_n > 0 and removed > 0:
            removal_fraction = removed / raw_n
            if removal_fraction > VALIDATION_SAFETY_THRESHOLD:
                logger.warning(
                    "[Chunk %d/%d] SAFETY THRESHOLD TRIGGERED: validator removed "
                    "%.0f%% of tasks (>%.0f%% limit). "
                    "Discarding validation — using raw extraction (%d tasks).",
                    chunk_index + 1, total_chunks,
                    removal_fraction * 100,
                    VALIDATION_SAFETY_THRESHOLD * 100,
                    raw_n,
                )
                return raw_tasks

        # Ensure all validated tasks carry the correct chunk_id
        for t in validated:
            if isinstance(t, dict):
                t["chunk_id"] = chunk_index
        return validated

    except Exception as e:
        logger.warning(
            "[Chunk %d/%d] Validation FAILED (%s) — using raw extraction",
            chunk_index + 1, total_chunks, e,
        )
        return raw_tasks
