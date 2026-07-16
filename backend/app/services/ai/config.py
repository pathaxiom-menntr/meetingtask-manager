"""
ai/config.py — Pipeline-wide constants.

All tunable values live here so they can be adjusted from settings
without touching any business logic.
"""

from app.core.config import settings

# ── Chunking ──────────────────────────────────────────────────────────────────
CHUNK_SIZE_CHARS: int = getattr(settings, "AI_CHUNK_SIZE_CHARS", 32_000)
CHUNK_OVERLAP_CHARS: int = 500

# ── LLM retry ─────────────────────────────────────────────────────────────────
MAX_RETRIES: int = getattr(settings, "AI_MAX_RETRIES", 3)

# ── Parallelism ───────────────────────────────────────────────────────────────
MAX_PARALLEL_WORKERS: int = getattr(settings, "AI_MAX_PARALLEL_WORKERS", 4)

# ── Validation pass ───────────────────────────────────────────────────────────
VALIDATION_PASS_ENABLED: bool = getattr(settings, "AI_VALIDATION_PASS", True)

# If the validator removes more than this fraction of tasks for a chunk,
# discard its output and fall back to the raw extraction.
VALIDATION_SAFETY_THRESHOLD: float = 0.10   # 10 % max removal per chunk

# ── Confidence ────────────────────────────────────────────────────────────────
# Tasks below MIN_CONFIDENCE are dropped (clear hallucinations).
# Set to 0.50 to be inclusive — missing a task is worse than a false-positive.
MIN_CONFIDENCE: float = getattr(settings, "AI_MIN_CONFIDENCE", 0.50)

# ── Vocabulary ────────────────────────────────────────────────────────────────
# Action verbs used to validate task titles (informational only — not a gate).
_ACTION_VERBS: frozenset[str] = frozenset({
    "add", "address", "analyze", "approve", "assign", "build", "check",
    "clarify", "collect", "complete", "configure", "confirm", "contact",
    "coordinate", "create", "define", "deliver", "deploy", "design",
    "document", "draft", "ensure", "evaluate", "finish", "fix", "follow",
    "hire", "identify", "implement", "install", "integrate", "investigate",
    "merge", "migrate", "monitor", "notify", "onboard", "optimize", "plan",
    "prepare", "present", "refactor", "release", "remove", "report",
    "resolve", "review", "schedule", "send", "set", "setup", "share",
    "submit", "test", "update", "upload", "write",
})

_VALID_PRIORITIES: frozenset[str] = frozenset({"low", "medium", "high", "critical"})

# Stop-words stripped before Jaccard token comparison.
_STOP_WORDS: frozenset[str] = frozenset({
    "a", "an", "and", "are", "at", "be", "been", "being", "by", "can",
    "could", "for", "in", "is", "it", "its", "may", "might", "must", "of",
    "on", "or", "shall", "should", "that", "the", "these", "this", "those",
    "to", "was", "were", "will", "with", "would",
})
