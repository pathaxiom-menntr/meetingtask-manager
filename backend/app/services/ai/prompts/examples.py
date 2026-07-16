"""
prompts/examples.py — Few-shot examples embedded in the extraction prompt.

Keeping examples in a separate file means they can be edited without
touching any control flow.
"""

FEW_SHOT_EXAMPLES = """
===================================================
EXAMPLE 1 — Direct assignment with due date
===================================================
INPUT:
  Team: Alice Johnson, Bob Smith, Carol White
  Today: 2025-06-10
  Alice: "Bob, can you finish the API docs by end of this week?"
  Bob: "Sure, I'll have it done by Friday."

OUTPUT:
{
  "tasks": [
    {
      "title": "Complete API documentation",
      "description": "Bob committed to finishing the API documentation by Friday (end of the week). Alice requested this during the sprint review to unblock downstream teams.",
      "assignee": "Bob Smith",
      "assigner": "Alice Johnson",
      "priority": "high",
      "due_date": "2025-06-13",
      "confidence": 0.98,
      "evidence": "Alice: 'Bob, can you finish the API docs by end of this week?' Bob: 'Sure, I'll have it done by Friday.'",
      "meeting_section": "Sprint review",
      "tags": ["documentation", "api"]
    }
  ]
}

===================================================
EXAMPLE 2 — Critical blocking issue
===================================================
INPUT:
  Team: Alice Johnson, Carol White
  Today: 2025-06-10
  Alice: "Carol, the login bug is blocking QA — fix it ASAP."
  Carol: "On it, I'll push a fix today."

OUTPUT:
{
  "tasks": [
    {
      "title": "Fix login bug blocking QA",
      "description": "Critical login bug must be fixed immediately — it is blocking the entire QA team from proceeding. Carol committed to pushing a fix the same day.",
      "assignee": "Carol White",
      "assigner": "Alice Johnson",
      "priority": "critical",
      "due_date": "2025-06-10",
      "confidence": 0.99,
      "evidence": "Alice: 'Carol, the login bug is blocking QA — fix it ASAP.' Carol: 'On it, I'll push a fix today.'",
      "meeting_section": "Bug triage",
      "tags": ["bug", "qa", "blocking"]
    }
  ]
}

===================================================
EXAMPLE 3 — Pronoun resolution ("it", "that", "this")
===================================================
INPUT:
  Team: John Doe, Sarah Lee
  Today: 2025-06-10
  Sarah: "The dashboard redesign is critical for the Q3 launch."
  John: "Agreed. I'll take care of it by next Monday."

OUTPUT:
{
  "tasks": [
    {
      "title": "Implement dashboard redesign",
      "description": "John committed to completing the dashboard redesign by next Monday. 'It' refers to the dashboard redesign mentioned immediately before. This is tied to the Q3 launch timeline.",
      "assignee": "John Doe",
      "assigner": null,
      "priority": "high",
      "due_date": "2025-06-16",
      "confidence": 0.92,
      "evidence": "Sarah: 'The dashboard redesign is critical for the Q3 launch.' John: 'Agreed. I'll take care of it by next Monday.'",
      "meeting_section": "Design review",
      "tags": ["dashboard", "redesign", "q3"]
    }
  ]
}

===================================================
EXAMPLE 4 — Assignment conflict (LATEST assignment wins)
===================================================
INPUT:
  Team: John Doe, Sarah Lee
  Today: 2025-06-10
  John: "I'll handle the production deployment."
  [Later in the meeting]
  Sarah: "Actually, I'll take the deployment — John is overloaded this week."

OUTPUT:
{
  "tasks": [
    {
      "title": "Deploy application to production",
      "description": "Sarah took over the production deployment from John because John is overloaded. The latest explicit assignment (Sarah) supersedes John's earlier commitment.",
      "assignee": "Sarah Lee",
      "assigner": null,
      "priority": "medium",
      "due_date": null,
      "confidence": 0.95,
      "evidence": "John: 'I'll handle the production deployment.' Sarah: 'Actually, I'll take the deployment — John is overloaded this week.'",
      "meeting_section": "Release planning",
      "tags": ["deployment", "production", "release"]
    }
  ]
}

===================================================
EXAMPLE 5 — Duplicate merge (same task mentioned twice)
===================================================
INPUT:
  Team: Alice Johnson
  Today: 2025-06-10
  Alice: "I need to update the dashboard metrics before the board meeting."
  [Later]
  Alice: "Right, the dashboard metrics update — I'll get that done by Thursday."

OUTPUT:
{
  "tasks": [
    {
      "title": "Update dashboard metrics for board meeting",
      "description": "Alice committed to updating the dashboard metrics before the board meeting. The task was mentioned twice — merged into one entry with the most specific deadline (Thursday).",
      "assignee": "Alice Johnson",
      "assigner": null,
      "priority": "high",
      "due_date": "2025-06-12",
      "confidence": 0.97,
      "evidence": "Alice: 'I need to update the dashboard metrics before the board meeting.' [Later] Alice: 'the dashboard metrics update — I'll get that done by Thursday.'",
      "meeting_section": "Status updates",
      "tags": ["dashboard", "metrics", "board-meeting"]
    }
  ]
}

===================================================
EXAMPLE 6 — Self-commitment without explicit assigner
===================================================
INPUT:
  Team: John Doe, Sarah Lee
  Today: 2025-06-10
  John: "I'll send the updated contract to the client by June 20th."

OUTPUT:
{
  "tasks": [
    {
      "title": "Send updated contract to client",
      "description": "John committed to sending the updated contract to the client by June 20th. Self-assigned — no explicit assigner in the transcript.",
      "assignee": "John Doe",
      "assigner": null,
      "priority": "high",
      "due_date": "2025-06-20",
      "confidence": 0.99,
      "evidence": "John: 'I'll send the updated contract to the client by June 20th.'",
      "meeting_section": "Client updates",
      "tags": ["contract", "client"]
    }
  ]
}

===================================================
EXAMPLE 7 — NEGATIVE EXAMPLES: What NOT to extract
===================================================
INPUT:
  Team: Alice Johnson, Bob Smith
  Today: 2025-06-10
  Alice: "I think we should really consider improving performance."
  Bob: "Yeah, performance improvements are definitely important."
  Alice: "We've decided to adopt the new microservices architecture."
  Bob: "The Q3 metrics are looking pretty good overall."
  Alice: "There's a risk that the vendor won't deliver on time."

OUTPUT: {"tasks": []}

REASON: None of these sentences are explicit commitments or assignments.
- "I think we should consider" -> opinion, not a commitment
- "performance is important" -> vague discussion, no owner or action
- "We've decided to adopt" -> group decision, no individual action owner
- "Q3 metrics looking good" -> status update, no action needed
- "There's a risk" -> risk identification without an owner or action
"""
