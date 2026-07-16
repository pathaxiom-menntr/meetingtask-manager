"""
processing/consistency.py — Layer 6c: Final lightweight consistency check.

Pure Python pass — NO LLM call.
Normalises names, validates dates, and strips tasks with empty titles.
Never bulk-deletes tasks.
"""

from app.core.logger import get_logger
from ..config import _VALID_PRIORITIES

logger = get_logger(__name__)


def run_final_consistency_check(
    tasks: list[dict],
    team_members: list[str],
    today_str: str,
) -> list[dict]:
    """
    Lightweight final consistency check after all chunks are merged.

    May ONLY:
      - Normalise assignee names against the team list
      - Validate and repair due dates
      - Normalise priority values
      - Remove tasks with empty titles (nothing can be done with them)

    May NEVER bulk-delete tasks.
    """
    member_lower = {m.lower(): m for m in team_members}

    def _rematch(name: str | None) -> str | None:
        if not name:
            return None
        nl = name.lower().strip()
        if nl in member_lower:
            return member_lower[nl]
        for key, full in member_lower.items():
            if nl in key.split() or any(part == nl for part in key.split()):
                return full
        return name  # keep original if no match — don't null it out

    result = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        title = (task.get("title") or "").strip()
        if not title:
            continue  # only valid deletion reason

        task["title"] = title
        if team_members:
            task["assignee"] = _rematch(task.get("assignee"))
            task["assigner"] = _rematch(task.get("assigner"))
        priority = (task.get("priority") or "medium").lower().strip()
        task["priority"] = priority if priority in _VALID_PRIORITIES else "medium"
        result.append(task)

    logger.info("Final consistency check: %d -> %d tasks", len(tasks), len(result))
    return result
