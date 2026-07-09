import json
from datetime import date, timedelta

from openai import AzureOpenAI

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
)


# ── Few-shot examples injected into every prompt ──────────────────────────────
# Concrete examples are the single most effective way to improve LLM extraction
# accuracy — they define the expected pattern without ambiguity.

FEW_SHOT_EXAMPLES = """
EXAMPLE INPUT:
  Team: Alice Johnson, Bob Smith, Carol White
  Today: 2025-06-10

  Transcript:
  Alice: "Bob, can you finish the API documentation by end of this week?
  And Carol, we need the login bug fixed ASAP — it's blocking QA."
  Bob: "Sure, I'll have it done by Friday."
  Carol: "On it, I'll push a fix today."

EXAMPLE OUTPUT:
{
  "tasks": [
    {
      "title": "Complete API documentation",
      "description": "Bob committed to finishing the API documentation by end of the week. Alice requested this to support other team members.",
      "assignee": "Bob Smith",
      "assigner": "Alice Johnson",
      "priority": "high",
      "due_date": "2025-06-13"
    },
    {
      "title": "Fix login bug blocking QA",
      "description": "Critical login bug must be fixed immediately as it is blocking the QA team from proceeding. Carol committed to pushing a fix the same day.",
      "assignee": "Carol White",
      "assigner": "Alice Johnson",
      "priority": "critical",
      "due_date": "2025-06-10"
    }
  ]
}

---

EXAMPLE INPUT:
  Team: John Doe, Sarah Lee
  Today: 2025-06-10

  Transcript:
  "We discussed the roadmap for Q3. There was general agreement that performance
  improvements are important. John will schedule a follow-up meeting next week.
  Sarah mentioned she'd send the updated design mockups to the client by June 20th."

EXAMPLE OUTPUT:
{
  "tasks": [
    {
      "title": "Schedule Q3 follow-up meeting",
      "description": "John committed to scheduling a follow-up meeting to continue Q3 roadmap discussions. Target is sometime next week.",
      "assignee": "John Doe",
      "assigner": null,
      "priority": "medium",
      "due_date": "2025-06-16"
    },
    {
      "title": "Send updated design mockups to client",
      "description": "Sarah will send the updated design mockups to the client. Deadline is June 20th.",
      "assignee": "Sarah Lee",
      "assigner": null,
      "priority": "high",
      "due_date": "2025-06-20"
    }
  ]
}
"""


def _build_system_prompt(team_members: list[str], today: str) -> str:
    """
    Build a context-aware system prompt that injects:
    - The actual team member names so the AI can match assignees accurately
    - Today's date so relative deadlines resolve correctly
    - Few-shot examples to anchor the expected output format and quality
    """
    if team_members:
        member_block = (
            "TEAM MEMBERS — assignee and assigner MUST be one of these exact names, or null:\n"
            + "\n".join(f"  - {name}" for name in team_members)
        )
    else:
        member_block = "TEAM MEMBERS: none provided — use null for assignee and assigner."

    return f"""You are an expert AI meeting assistant. Your only job is to extract explicit, actionable tasks from meeting transcripts.

{member_block}

TODAY'S DATE: {today}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
FEW-SHOT EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{FEW_SHOT_EXAMPLES}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT — return ONLY valid JSON:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{
  "tasks": [
    {{
      "title": "Action verb + object, max 10 words",
      "description": "Context needed to act without re-reading the transcript",
      "assignee": "Exact name from TEAM MEMBERS, or null",
      "assigner": "Exact name from TEAM MEMBERS, or null",
      "priority": "low | medium | high | critical",
      "due_date": "YYYY-MM-DD or null"
    }}
  ]
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRICT RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT TO EXTRACT
1. Only extract tasks that are explicitly stated — someone was asked or committed to doing something.
2. Skip discussions, opinions, decisions, and status updates that have no follow-up action.
3. Never invent a task. If it isn't clearly stated, skip it.
4. Merge tasks that are clearly the same action item stated multiple times.

ASSIGNEE & ASSIGNER MATCHING
5. assignee = person who will DO the task.
6. assigner = person who ASKED for the task (e.g. "Alice asked Bob" → assigner=Alice, assignee=Bob).
7. Match names using first name, last name, or both — case-insensitive.
   Example: "john", "John", "John D", "John Doe" all match "John Doe" in the team list.
8. The value you output MUST be the full name exactly as written in the TEAM MEMBERS list.
9. If a name appears in the transcript but does NOT match any team member, output null.
10. If no person is mentioned at all, output null.

PRIORITY RULES
11. "critical" → blocking other work, must be done today or ASAP ("urgent", "immediately", "ASAP", "blocking").
12. "high"     → needed within the next few days or this week ("by Friday", "this week", "soon").
13. "medium"   → important, no hard urgency signal mentioned.
14. "low"      → optional, future, or low-stakes ("whenever you get a chance", "eventually").
15. Default is "medium".

DUE DATE RULES (Today = {today})
16. Resolve every relative date expression:
    "today"           → {today}
    "tomorrow"        → the next calendar day
    "this Friday"     → the upcoming Friday
    "next week"       → the Monday of next week
    "end of week"     → the upcoming Sunday
    "end of month"    → the last day of the current month
    "in N days"       → today + N days
17. Output in ISO format: YYYY-MM-DD.
18. Use null if no deadline is mentioned.

TITLE & DESCRIPTION
19. Title must begin with an action verb (Fix, Send, Review, Schedule, Deploy, Draft, Update, Test, etc.).
20. Title ≤ 10 words, specific enough to understand without context.
21. Description must give the assignee full context to act independently — include what, why, and any constraints.

EMPTY RESULT
22. If there are no actionable tasks at all, return: {{"tasks": []}}
"""


def _sanitize_tasks(tasks: list[dict], team_members: list[str]) -> list[dict]:
    """
    Post-process AI output to catch and correct common mistakes:
    - Remove tasks missing a title
    - Normalize priority values
    - Clear assignee/assigner values that don't match any team member
    - Truncate overlong titles
    """
    valid_priorities = {"low", "medium", "high", "critical"}
    member_lower = {m.lower(): m for m in team_members}

    def match_member(name: str | None) -> str | None:
        if not name:
            return None
        nl = name.lower().strip()
        # Exact match
        if nl in member_lower:
            return member_lower[nl]
        # Partial match: check if any team member's lower name contains nl or vice versa
        for key, full in member_lower.items():
            if nl in key or key in nl:
                return full
        return None

    sanitized = []
    for task in tasks:
        if not isinstance(task, dict):
            continue

        title = (task.get("title") or "").strip()
        if not title:
            continue  # skip untitled tasks

        # Truncate excessively long titles
        if len(title) > 100:
            title = title[:97] + "..."

        priority = (task.get("priority") or "medium").lower().strip()
        if priority not in valid_priorities:
            priority = "medium"

        assignee = match_member(task.get("assignee")) if team_members else task.get("assignee")
        assigner = match_member(task.get("assigner")) if team_members else task.get("assigner")

        sanitized.append({
            "title": title,
            "description": task.get("description"),
            "assignee": assignee,
            "assigner": assigner,
            "priority": priority,
            "due_date": task.get("due_date"),
        })

    return sanitized


class AIService:

    @staticmethod
    def generate_tasks(
        transcript: str,
        team_members: list[str] | None = None,
        today: str | None = None,
    ) -> list[dict]:
        """
        Extract action-item tasks from a meeting transcript.

        Args:
            transcript:    The full meeting transcript text.
            team_members:  Full names of all users in the team. Used both in
                           the prompt (for accurate AI matching) and in the
                           post-processing sanitizer.
            today:         ISO date string for today. Defaults to server date.
        """
        resolved_today = today or date.today().isoformat()
        resolved_members = team_members or []

        system_prompt = _build_system_prompt(resolved_members, resolved_today)

        try:
            response = client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Today is {resolved_today}.\n"
                            f"Team members: {', '.join(resolved_members) if resolved_members else 'none provided'}.\n\n"
                            f"Meeting transcript:\n\n{transcript}"
                        ),
                    },
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if content is None:
                return []

            data = json.loads(content)
            raw_tasks = data.get("tasks", [])

            # Post-process: sanitize names, priority values, and titles
            return _sanitize_tasks(raw_tasks, resolved_members)

        except Exception as e:
            logger.error("AI Service error: %s", str(e))
            from fastapi import HTTPException
            raise HTTPException(status_code=502, detail=f"AI Processing failed: {str(e)}")