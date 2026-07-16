"""
processing/rule_engine.py — Layer 7: Rule Engine.

Validates, normalises, and enriches every extracted task before it
leaves the pipeline. The final gate before tasks reach the API caller.
"""

import re
import uuid
from datetime import date

from app.core.logger import get_logger
from ..config import MIN_CONFIDENCE, _ACTION_VERBS, _VALID_PRIORITIES
from ..preprocessing.date_resolver import DateResolver

logger = get_logger(__name__)


class RuleEngine:
    """
    Validate, normalise, and enrich every extracted task before it leaves
    the pipeline.

    Policy
    ------
    * Tasks are NEVER rejected based on confidence alone (user requirement).
    * Tasks below 0.80 confidence are logged as warnings but still included.
    * Tasks below MIN_CONFIDENCE (default 0.50) are dropped — they represent
      clear hallucinations with no transcript basis.
    * Tasks without a title are always dropped (nothing can be done with them).
    * Assignee / assigner names are re-matched against the team list.
    * Priority values are normalised to the four valid levels.
    * Due dates are re-validated; any relative expression the LLM missed is
      resolved by DateResolver.
    * Tags are cleaned and deduplicated.
    * Identity fields (task_uuid, original_assignee, reassignment_history)
      are preserved and passed through to the final output.
    """

    @staticmethod
    def _match_member(name: str | None, member_lower: dict[str, str]) -> str | None:
        """Fuzzy-match a name token against the team member lookup dict."""
        if not name:
            return None
        nl = name.lower().strip()
        if nl in member_lower:
            return member_lower[nl]
        for key, full in member_lower.items():
            key_parts = key.split()
            if nl in key_parts or any(part in nl for part in key_parts):
                return full
        return None

    @staticmethod
    def _validate_date(value: str | None, today_str: str) -> str | None:
        """Return a valid ISO date string, or None."""
        if not value:
            return None
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            try:
                date.fromisoformat(value)
                return value
            except ValueError:
                pass
        try:
            today = date.fromisoformat(today_str)
        except ValueError:
            today = date.today()
        return DateResolver.resolve(value, today)

    @classmethod
    def process(
        cls,
        tasks: list[dict],
        team_members: list[str],
        today_str: str,
    ) -> list[dict]:
        """
        Apply all validation rules and return the final task list.

        Args:
            tasks:          Raw task dicts from the pipeline.
            team_members:   Full names of all team members.
            today_str:      Today's date as ISO string.
        """
        member_lower = {m.lower(): m for m in team_members}
        result: list[dict] = []

        for task in tasks:
            if not isinstance(task, dict):
                continue

            # Confidence gate
            try:
                confidence = float(task.get("confidence") or 0.80)
            except (TypeError, ValueError):
                confidence = 0.80
            confidence = round(max(0.0, min(1.0, confidence)), 2)

            if confidence < MIN_CONFIDENCE:
                logger.warning(
                    "RuleEngine: dropped task (confidence=%.2f < %.2f) — title=%r",
                    confidence, MIN_CONFIDENCE, task.get("title"),
                )
                continue

            if 0.50 <= confidence < 0.80:
                logger.warning(
                    "RuleEngine: low-confidence task included — confidence=%.2f title=%r",
                    confidence, task.get("title"),
                )

            # Title
            title = (task.get("title") or "").strip()
            if not title:
                logger.warning("RuleEngine: dropped task — missing title")
                continue
            if len(title) > 100:
                title = title[:97] + "..."

            first_word = title.split()[0].lower().rstrip(".,;:")
            if first_word not in _ACTION_VERBS:
                logger.debug(
                    "RuleEngine: title '%s' does not begin with a known action verb (first_word=%r)",
                    title, first_word,
                )

            description = (task.get("description") or "").strip() or None

            assignee = (
                cls._match_member(task.get("assignee"), member_lower)
                if team_members else task.get("assignee")
            )
            assigner = (
                cls._match_member(task.get("assigner"), member_lower)
                if team_members else task.get("assigner")
            )

            priority = (task.get("priority") or "medium").lower().strip()
            if priority not in _VALID_PRIORITIES:
                priority = "medium"

            due_date = cls._validate_date(task.get("due_date"), today_str)
            evidence = (task.get("evidence") or "").strip() or None
            meeting_section = (task.get("meeting_section") or "").strip() or None

            raw_tags = task.get("tags") or []
            if isinstance(raw_tags, list):
                tags = sorted({str(t).lower().strip() for t in raw_tags if t})
            else:
                tags = []

            result.append({
                "title": title,
                "description": description,
                "assignee": assignee,
                "assigner": assigner,
                "priority": priority,
                "due_date": due_date,
                "confidence": confidence,
                "evidence": evidence,
                "meeting_section": meeting_section,
                "tags": tags,
                # Identity fields — preserved from TaskIdentityStamper
                "task_uuid": task.get("task_uuid") or str(uuid.uuid4()),
                "original_assignee": task.get("original_assignee"),
                "reassignment_history": task.get("reassignment_history") or [],
                "chunk_id": task.get("chunk_id"),
            })

        return result
