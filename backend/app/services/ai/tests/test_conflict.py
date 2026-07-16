"""
tests/test_conflict.py — Unit tests for ReassignmentDetector and ConflictResolver.

Run with: pytest app/services/ai/tests/test_conflict.py -v
"""

import pytest
from ..processing.conflict import ReassignmentDetector, ConflictResolver


# ─── ReassignmentDetector ─────────────────────────────────────────────────────

class TestReassignmentDetector:

    def test_single_word_trigger_actually(self):
        assert ReassignmentDetector.detect("Actually Sarah will handle this.") is True

    def test_single_word_trigger_instead(self):
        assert ReassignmentDetector.detect("John will do it instead.") is True

    def test_multi_word_take_over(self):
        assert ReassignmentDetector.detect("Bob will take over the task.") is True

    def test_multi_word_hand_over(self):
        assert ReassignmentDetector.detect("Please hand over the deployment to Alice.") is True

    def test_independent_task_no_trigger(self):
        assert ReassignmentDetector.detect("Manager: John update the board today.") is False

    def test_empty_evidence(self):
        assert ReassignmentDetector.detect("") is False

    def test_word_boundary_respected(self):
        # "practically" contains "actually" but should NOT match
        assert ReassignmentDetector.detect("This is practically done.") is False


# ─── ConflictResolver ─────────────────────────────────────────────────────────

def _make_task(title, assignee, evidence, chunk_id=0, offset=0, uuid_str=None):
    return {
        "title": title,
        "assignee": assignee,
        "assigner": None,
        "due_date": None,
        "evidence": evidence,
        "chunk_id": chunk_id,
        "task_uuid": uuid_str or f"uuid-{assignee}",
        "original_assignee": assignee,
        "reassignment_history": [],
        "transcript_offset": offset,
        "line_number": 1,
        "_title_tokens": sorted(title.lower().split()),
    }


class TestConflictResolver:

    def test_independent_tasks_all_kept(self):
        """Same title, different assignees, no reassignment phrase -> keep all."""
        tasks = [
            _make_task("Update project board", "Bob",    "Bob: update the project board.", offset=0),
            _make_task("Update project board", "Jason",  "Jason: update the board tomorrow.", offset=50),
            _make_task("Update project board", "Robert", "Robert: update the board.", chunk_id=1, offset=10),
        ]
        result = ConflictResolver.resolve(tasks)
        assert len(result) == 3, f"Expected 3, got {len(result)}"

    def test_genuine_reassignment_resolved(self):
        """Evidence contains 'actually' -> merge to 1 task, assignee = Sarah."""
        tasks = [
            _make_task("Prepare release notes", "John",
                       "John: I will prepare the release notes.", chunk_id=0, offset=0),
            _make_task("Prepare release notes", "Sarah",
                       "Manager: Actually Sarah will own the release notes instead of John.",
                       chunk_id=1, offset=0),
        ]
        result = ConflictResolver.resolve(tasks)
        assert len(result) == 1, f"Expected 1, got {len(result)}"
        assert result[0]["assignee"] == "Sarah"
        hist = result[0]["reassignment_history"]
        assert len(hist) == 1
        assert hist[0]["from_assignee"] == "John"

    def test_distinct_tasks_no_merge(self):
        """20 completely different tasks should never be merged."""
        tasks = [
            _make_task(f"Task {i}", f"Person{i}", f"Unique evidence {i}", uuid_str=f"u{i}")
            for i in range(20)
        ]
        result = ConflictResolver.resolve(tasks)
        assert len(result) == 20

    def test_safety_gate_fires_on_large_batch(self):
        """If conflict resolution would remove >5% of a 25-task batch, restore all."""
        # All tasks say "actually" in evidence -> ConflictResolver tries to merge all
        # -> >5% removal of 25 tasks -> gate fires -> 25 restored
        tasks = [
            _make_task("Fix bug", f"Dev{i}",
                       f"Actually Dev{i} will fix the bug.",
                       uuid_str=f"u{i}")
            for i in range(25)
        ]
        result = ConflictResolver.resolve(tasks)
        # Gate fires: all 25 returned
        assert len(result) == 25
