"""processing — identity stamping, conflict resolution, deduplication, rule engine."""

from .identity import TaskIdentityStamper
from .conflict import ReassignmentDetector, ConflictResolver
from .deduplicator import SemanticDeduplicator
from .consistency import run_final_consistency_check
from .rule_engine import RuleEngine

__all__ = [
    "TaskIdentityStamper",
    "ReassignmentDetector",
    "ConflictResolver",
    "SemanticDeduplicator",
    "run_final_consistency_check",
    "RuleEngine",
]
