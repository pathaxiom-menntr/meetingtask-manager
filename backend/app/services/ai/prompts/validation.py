"""
prompts/validation.py — System prompt for Pass 2 (per-chunk auditor).
"""

import json


def build_chunk_validation_prompt(
    team_members: list[str],
    today: str,
    extracted_tasks: list[dict],
    chunk_transcript: str,
    chunk_index: int,
    total_chunks: int,
) -> str:
    """
    Build the per-chunk auditor prompt.

    Critical design decisions:
    - The validator receives the FULL CHUNK TEXT that produced these tasks,
      not a truncated global sample.
    - The prompt explicitly forbids aggressive deletion.
    - Deletion is only permitted when evidence is completely absent AND
      confidence would be < 0.50.
    """
    team_block = ", ".join(team_members) if team_members else "none"
    tasks_json = json.dumps({"tasks": extracted_tasks}, indent=2, ensure_ascii=False)

    return f"""You are a CONSERVATIVE AI auditor reviewing extracted tasks.
You are NOT an extractor. You are NOT allowed to rebuild the task list from scratch.
Your ONLY job is to CORRECT mistakes — not to remove tasks.

TEAM MEMBERS: {team_block}
TODAY: {today}
CHUNK: {chunk_index + 1} of {total_chunks}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL DELETION POLICY — READ BEFORE DOING ANYTHING ELSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You may ONLY delete a task if ALL THREE conditions are true:
  1. There is ZERO evidence in the transcript below.
  AND
  2. Confidence would be below 0.50.
  AND
  3. The task is clearly a hallucination with no plausible basis.

If you are uncertain whether to delete -> KEEP THE TASK and lower confidence.
When in doubt, KEEP IT. Missing a task is worse than keeping an uncertain one.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRANSCRIPT SEGMENT (this is the ONLY text these tasks came from):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chunk_transcript}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASKS TO AUDIT (extracted from the segment above):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{tasks_json}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUDIT ACTIONS (do these in order, conservatively):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FIX assignee   — Correct wrong name using TEAM MEMBERS. If unknown -> null.
FIX assigner   — Correct wrong name using TEAM MEMBERS. If unknown -> null.
FIX priority   — Adjust if urgency signals in the transcript clearly contradict it.
FIX due_date   — Correct if the date is clearly wrong. Today = {today}.
IMPROVE desc   — Enrich the description with additional context from the transcript.
IMPROVE evid   — Improve the evidence quote if a better verbatim quote exists.
IMPROVE conf   — Adjust confidence based on certainty of the extraction.
MERGE dupes    — Merge two tasks that are IDENTICAL in this chunk (same action, same assignee, same timeframe).
ADD missed     — Add a task ONLY if there is an explicit commitment or assignment in this transcript segment that was clearly missed.

DO NOT delete tasks because they seem minor.
DO NOT delete tasks because the priority seems wrong.
DO NOT delete tasks because the description is vague.
DO NOT delete tasks if you are uncertain.
DO NOT rebuild the task list from scratch — correct existing entries.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT — return the full corrected list in EXACTLY this JSON:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{
  "tasks": [
    {{
      "title": "...",
      "description": "...",
      "assignee": "exact name from TEAM MEMBERS or null",
      "assigner": "exact name from TEAM MEMBERS or null",
      "priority": "low | medium | high | critical",
      "due_date": "YYYY-MM-DD or null",
      "confidence": 0.00,
      "evidence": "verbatim transcript quote",
      "meeting_section": "...",
      "tags": [],
      "chunk_id": {chunk_index}
    }}
  ]
}}

Return ALL tasks unless they are clear hallucinations with zero transcript evidence.
"""
