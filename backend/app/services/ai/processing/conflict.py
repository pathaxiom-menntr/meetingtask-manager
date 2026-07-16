"""
processing/conflict.py — Layer 6a: Reassignment detector + Conflict resolver.

Core principle: two tasks are the SAME task ONLY when there is explicit
evidence of reassignment. Independent tasks with identical titles are NEVER merged.
"""

import re

from app.core.logger import get_logger
from .deduplicator import _tokenize, _jaccard

logger = get_logger(__name__)


class ReassignmentDetector:
    """
    Determine whether a piece of transcript evidence contains an explicit
    reassignment signal.

    A reassignment signal is one of the phrases below appearing in the evidence
    of the *later* task (higher chunk_id / transcript_offset). The presence of
    such a phrase is a necessary condition for two tasks to be considered the
    same task under a new owner.

    Design notes
    ------------
    * Matching is case-insensitive and searches the full evidence string.
    * Single-word triggers use word-boundary anchors.
    * Multi-word phrases are matched as substrings (order matters).
    * Returns False (independent task) when no phrase is found.
    """

    _SINGLE_WORD_TRIGGERS: frozenset[str] = frozenset({
        "actually",
        "instead",
        "reassign",
        "reassigned",
        "transfer",
        "transferred",
    })

    _MULTI_WORD_PHRASES: tuple[str, ...] = (
        "take over",
        "taking over",
        "took over",
        "switch owner",
        "switching owner",
        "move this to",
        "moving this to",
        "hand over",
        "handing over",
        "handed over",
        "give it to",
        "giving it to",
        "assign it to",
        "assigning it to",
        "will own it",
        "will handle it",
        "will be handling",
        "no longer",
        "someone else will",
        "change owner",
        "let's reassign",
        "let us reassign",
        "pass this to",
        "passing this to",
        "now owns",
        "will now own",
    )

    @classmethod
    def detect(cls, evidence: str) -> bool:
        """
        Return True if *evidence* contains at least one explicit reassignment
        signal. Returns False for empty evidence.
        """
        if not evidence:
            return False
        text = evidence.lower()

        for word in cls._SINGLE_WORD_TRIGGERS:
            if re.search(rf"\b{re.escape(word)}\b", text):
                return True

        for phrase in cls._MULTI_WORD_PHRASES:
            if phrase in text:
                return True

        return False


class ConflictResolver:
    """
    Resolve true reassignment events without collapsing independent tasks.

    Core principle
    --------------
    Two tasks are the SAME task ONLY when ALL of the following hold:

      1. Normalised-title Jaccard similarity >= TITLE_THRESHOLD (0.90).
      2. The tasks have DIFFERENT assignees (otherwise nothing to resolve).
      3. At least ONE of:
           a. The later task's evidence contains an explicit reassignment phrase
              (detected by ReassignmentDetector).
           b. The two tasks share the same evidence block
              (evidence Jaccard >= EVIDENCE_IDENTITY_THRESHOLD, 0.85).

    If condition 3 is NOT met the tasks are treated as independent assignments
    even when the titles are identical. They are kept as separate tasks.

    Resolution actions (when a true reassignment IS confirmed)
    ----------------------------------------------------------
    * Update ``assignee`` on the surviving (later) task.
    * Append a reassignment event to ``reassignment_history``.
    * Append evidence from the earlier task (never replace).
    * Boost confidence by 0.02 on the surviving task.
    * NEVER delete tasks without a confirmed reassignment.

    5% safety gate
    --------------
    If conflict resolution would remove more than MAX_REDUCTION_FRACTION (5%)
    of the input tasks (on batches >= 20), abort and restore the original list.
    """

    TITLE_THRESHOLD: float = 0.90
    EVIDENCE_IDENTITY_THRESHOLD: float = 0.85
    MAX_REDUCTION_FRACTION: float = 0.05

    @classmethod
    def resolve(cls, tasks: list[dict]) -> list[dict]:
        """
        Process *tasks* and return the resolved list.
        Independent tasks are NEVER removed even when they share a title.
        """
        if len(tasks) <= 1:
            return tasks

        original_count = len(tasks)
        absorbed: list[bool] = [False] * original_count
        conflicts_resolved = 0
        independent_logged = 0

        def _title_tokens(t: dict) -> frozenset:
            cached = t.get("_title_tokens")
            if cached:
                return frozenset(cached)
            return _tokenize(t.get("title") or "")

        token_sets = [_title_tokens(t) for t in tasks]

        for i in range(original_count):
            if absorbed[i]:
                continue

            task_a = tasks[i]
            chunk_a = task_a.get("chunk_id") or 0
            offset_a = task_a.get("transcript_offset") or 0
            assignee_a = (task_a.get("assignee") or "").lower().strip()
            evidence_a_tokens = _tokenize(task_a.get("evidence") or "")

            for j in range(i + 1, original_count):
                if absorbed[j]:
                    continue

                task_b = tasks[j]

                # Condition 1: title similarity
                title_sim = _jaccard(token_sets[i], token_sets[j])
                if title_sim < cls.TITLE_THRESHOLD:
                    continue

                # Condition 2: different assignees
                assignee_b = (task_b.get("assignee") or "").lower().strip()
                if assignee_a == assignee_b:
                    # Same title + same assignee -> duplicate; handled by
                    # SemanticDeduplicator downstream, not here.
                    continue

                # Condition 3: explicit reassignment evidence
                chunk_b = task_b.get("chunk_id") or 0
                offset_b = task_b.get("transcript_offset") or 0

                if chunk_b > chunk_a or (chunk_b == chunk_a and offset_b > offset_a):
                    later_task, earlier_task, later_idx, earlier_idx = task_b, task_a, j, i
                else:
                    later_task, earlier_task, later_idx, earlier_idx = task_a, task_b, i, j

                later_evidence = later_task.get("evidence") or ""
                evidence_b_tokens = _tokenize(later_task.get("evidence") or "")
                evidence_sim = _jaccard(evidence_a_tokens, evidence_b_tokens)

                has_reassignment_phrase = ReassignmentDetector.detect(later_evidence)
                has_shared_evidence = evidence_sim >= cls.EVIDENCE_IDENTITY_THRESHOLD

                if not has_reassignment_phrase and not has_shared_evidence:
                    # Independent tasks — keep both
                    logger.info(
                        "[ConflictResolver] Independent task detected — no merge performed | "
                        "title=%r | UUID-A=%s assignee=%s | UUID-B=%s assignee=%s | "
                        "title_sim=%.2f | evidence_sim=%.2f | reason=no_reassignment_phrase",
                        task_a.get("title"),
                        task_a.get("task_uuid", "?"),
                        task_a.get("assignee"),
                        task_b.get("task_uuid", "?"),
                        task_b.get("assignee"),
                        title_sim,
                        evidence_sim,
                    )
                    independent_logged += 1
                    continue

                # Confirmed reassignment: apply it
                earlier_assignee_display = earlier_task.get("assignee") or "unknown"
                later_assignee_display = later_task.get("assignee") or "unknown"
                reason = (
                    "Explicit reassignment phrase detected in evidence"
                    if has_reassignment_phrase
                    else "Identical evidence block — same transcript event"
                )

                later_task.setdefault("reassignment_history", []).append({
                    "from_assignee": earlier_assignee_display,
                    "to_assignee": later_assignee_display,
                    "reason": reason,
                    "evidence": later_evidence,
                    "source_task_uuid": earlier_task.get("task_uuid", ""),
                })

                earlier_ev = (earlier_task.get("evidence") or "").strip()
                existing_ev = (later_task.get("evidence") or "").strip()
                if earlier_ev and earlier_ev != existing_ev:
                    later_task["evidence"] = (
                        existing_ev + " | [Prior assignment] " + earlier_ev
                    ).strip(" | ")

                base_conf = float(later_task.get("confidence") or 0.80)
                later_task["confidence"] = round(min(1.0, base_conf + 0.02), 2)

                absorbed[earlier_idx] = True
                conflicts_resolved += 1

                logger.info(
                    "[ConflictResolver] Reassignment confirmed | "
                    "Task ID: %s | Title: %r | "
                    "Original assignee: %s -> Current assignee: %s | "
                    "Reason: %s | Evidence: %r",
                    later_task.get("task_uuid", "?"),
                    later_task.get("title"),
                    earlier_assignee_display,
                    later_assignee_display,
                    reason,
                    later_evidence[:200],
                )

        result = [t for idx, t in enumerate(tasks) if not absorbed[idx]]

        # 5% safety gate (only fires when batch is large enough)
        MIN_GATE_SIZE = 20
        removed = original_count - len(result)
        reduction_fraction = removed / original_count if original_count else 0.0

        if original_count >= MIN_GATE_SIZE and reduction_fraction > cls.MAX_REDUCTION_FRACTION:
            logger.warning(
                "[ConflictResolver] SAFETY GATE TRIGGERED -- "
                "conflict resolution would remove %.1f%% of tasks (limit: %.0f%%). "
                "Aborting. Restoring all %d original tasks.",
                reduction_fraction * 100,
                cls.MAX_REDUCTION_FRACTION * 100,
                original_count,
            )
            for t in tasks:
                t["reassignment_history"] = []
            return tasks

        logger.info(
            "[ConflictResolver] Complete -- input: %d | reassignments resolved: %d | "
            "independent tasks kept: %d | output: %d",
            original_count,
            conflicts_resolved,
            independent_logged,
            len(result),
        )
        return result
