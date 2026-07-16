"""
processing/deduplicator.py — Layer 6b: Multi-field composite deduplicator.

Defines _tokenize and _jaccard as module-level helpers — imported by
identity.py and conflict.py as well.
"""

import re

from app.core.logger import get_logger
from ..config import _STOP_WORDS

logger = get_logger(__name__)


# ── Text utilities (shared across processing sub-modules) ─────────────────────

def _tokenize(text: str) -> frozenset[str]:
    """Lowercase, remove stop-words, return a frozen token set."""
    tokens = re.findall(r"\b[a-z]+\b", text.lower())
    return frozenset(t for t in tokens if t not in _STOP_WORDS)


def _jaccard(a: frozenset, b: frozenset) -> float:
    """Jaccard similarity between two token sets. Returns 0.0 for empty sets."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ── Composite similarity score ────────────────────────────────────────────────

def _composite_similarity(a: dict, b: dict) -> float:
    """
    Multi-field composite similarity score between two tasks.

    Scoring breakdown (weights sum to 1.0):
      title     0.40  — Jaccard token overlap on normalised titles
      assignee  0.25  — exact match on assignee name
      due_date  0.15  — exact match on due date
      evidence  0.20  — Jaccard token overlap on evidence snippets

    Two tasks in DIFFERENT chunks receive a 0.10 penalty to avoid
    over-merging legitimate repeated agenda items across chunks.

    Returns a value in [0.0, 1.0].
    """
    title_sim = _jaccard(
        _tokenize(a.get("title") or ""),
        _tokenize(b.get("title") or ""),
    )

    assignee_a = (a.get("assignee") or "").lower().strip()
    assignee_b = (b.get("assignee") or "").lower().strip()
    assignee_sim = 1.0 if (assignee_a and assignee_a == assignee_b) else 0.0

    date_a = a.get("due_date") or ""
    date_b = b.get("due_date") or ""
    date_sim = 1.0 if (date_a and date_a == date_b) else 0.0

    evidence_sim = _jaccard(
        _tokenize(a.get("evidence") or ""),
        _tokenize(b.get("evidence") or ""),
    )

    score = (
        0.40 * title_sim
        + 0.25 * assignee_sim
        + 0.15 * date_sim
        + 0.20 * evidence_sim
    )

    # Cross-chunk penalty — same title can legitimately appear in different
    # meeting sections (e.g. mentioned at start, followed up at end).
    chunk_a = a.get("chunk_id")
    chunk_b = b.get("chunk_id")
    if chunk_a is not None and chunk_b is not None and chunk_a != chunk_b:
        score -= 0.10

    return max(0.0, score)


# ── SemanticDeduplicator ──────────────────────────────────────────────────────

class SemanticDeduplicator:
    """
    Remove genuinely duplicate tasks using a multi-field composite score.

    Design principles:
    * Title alone is NOT sufficient to declare a duplicate.
    * The composite score weights title (40%), assignee (25%),
      due_date (15%), and evidence (20%).
    * Tasks from different chunks incur a 0.10 cross-chunk penalty to avoid
      over-merging legitimate repeated agenda items.
    * The threshold is deliberately HIGH (0.82) to err on the side of keeping
      tasks rather than merging them.
    """

    # High threshold compared to the old Jaccard-only 0.65 threshold —
    # prevents over-aggressive merging.
    SIMILARITY_THRESHOLD: float = 0.82

    @classmethod
    def deduplicate(cls, tasks: list[dict]) -> list[dict]:
        """Return a deduplicated task list. Input order is preserved."""
        if len(tasks) <= 1:
            return tasks

        absorbed = [False] * len(tasks)
        result: list[dict] = []

        for i in range(len(tasks)):
            if absorbed[i]:
                continue
            canonical = dict(tasks[i])

            for j in range(i + 1, len(tasks)):
                if absorbed[j]:
                    continue

                score = _composite_similarity(tasks[i], tasks[j])
                if score < cls.SIMILARITY_THRESHOLD:
                    continue

                # Confirmed duplicate — merge conservatively
                other = tasks[j]
                absorbed[j] = True

                base_conf = float(canonical.get("confidence") or 0.0)
                other_conf = float(other.get("confidence") or 0.0)

                if other_conf > base_conf:
                    saved_evidence = canonical.get("evidence") or ""
                    canonical = dict(other)
                    other_evidence = saved_evidence
                else:
                    other_evidence = other.get("evidence") or ""

                # Concatenate unique evidence snippets
                existing_ev = (canonical.get("evidence") or "").strip()
                if other_evidence.strip() and other_evidence.strip() != existing_ev:
                    canonical["evidence"] = (
                        existing_ev + " | " + other_evidence.strip()
                    ).strip(" | ")

                # Union tags
                canonical["tags"] = sorted(
                    set(canonical.get("tags") or []) | set(other.get("tags") or [])
                )

                logger.debug(
                    "Deduplicator: merged '%s' <- '%s' (composite_score=%.2f)",
                    canonical.get("title"), other.get("title"), score,
                )

            result.append(canonical)

        merged_count = sum(absorbed)
        logger.info(
            "Deduplication: %d -> %d tasks (%d merged)",
            len(tasks), len(result), merged_count,
        )
        return result
