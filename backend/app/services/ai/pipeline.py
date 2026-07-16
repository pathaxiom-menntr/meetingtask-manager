"""
pipeline.py — Main orchestrator: wires all layers together.

This is the ONLY file that knows about the full pipeline order.
Each layer is imported from its own module and called in sequence.

Pipeline
--------
Transcript
  |  Layer 1   preprocessing.TranscriptPreprocessor  — clean & normalise
  |  Layer 3   preprocessing.TranscriptChunker       — split into chunks
  |  Layer 5   ThreadPoolExecutor (parallel)
  |               extraction.extract_from_chunk      — Pass 1: extract
  |               processing.TaskIdentityStamper     — UUID + position stamp
  |               extraction.validate_chunk          — Pass 2: audit
  |  Merge all chunk results (preserving chronological order)
  |  Layer 6a  processing.ConflictResolver           — reassignment-only
  |  Layer 6b  processing.SemanticDeduplicator       — multi-field dedup
  |  Layer 6c  processing.run_final_consistency_check— lightweight normalise
  |  Layer 7   processing.RuleEngine                 — validate & enrich
  v
Final task list  ->  list[dict]
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

from app.core.logger import get_logger
from .config import MAX_PARALLEL_WORKERS
from .preprocessing import TranscriptPreprocessor, TranscriptChunker
from .prompts import build_system_prompt
from .extraction import extract_from_chunk, validate_chunk
from .processing import (
    ConflictResolver,
    SemanticDeduplicator,
    run_final_consistency_check,
    RuleEngine,
)

logger = get_logger(__name__)


def _process_chunk(
    chunk: str,
    system_prompt: str,
    team_members: list[str],
    today: str,
    chunk_index: int,
    total_chunks: int,
) -> list[dict]:
    """
    Full single-chunk pipeline: extract -> validate.
    Designed to be called in a thread pool for parallelisation.
    """
    raw = extract_from_chunk(
        chunk=chunk,
        system_prompt=system_prompt,
        team_members=team_members,
        today=today,
        chunk_index=chunk_index,
        total_chunks=total_chunks,
    )
    return validate_chunk(
        raw_tasks=raw,
        chunk_transcript=chunk,      # <- FULL chunk, not a truncated sample
        team_members=team_members,
        today=today,
        chunk_index=chunk_index,
        total_chunks=total_chunks,
    )


class AIService:
    """
    Public facade for the AI extraction pipeline.

    Single public method:
        AIService.generate_tasks(transcript, team_members, today) -> list[dict]

    Backward-compatible: the import path ``from app.services.ai import AIService``
    continues to work via the package's __init__.py.
    """

    @staticmethod
    def generate_tasks(
        transcript: str,
        team_members: list[str] | None = None,
        today: str | None = None,
    ) -> list[dict]:
        """
        Extract action-item tasks from a meeting transcript.

        Args
        ----
        transcript:    Full meeting transcript (any length; 1+ hour meetings supported).
        team_members:  Full names of all team members for accurate name matching.
        today:         ISO date for relative date resolution. Defaults to server date.

        Returns
        -------
        List of task dicts. Each dict contains:
            title, description, assignee, assigner, priority, due_date,
            confidence, evidence, meeting_section, tags,
            task_uuid, original_assignee, reassignment_history, chunk_id
        """
        from fastapi import HTTPException

        resolved_today = today or date.today().isoformat()
        resolved_members = team_members or []

        try:
            # Layer 1: Preprocess
            logger.info(
                "AI Pipeline START — transcript: %d chars | team: %d members",
                len(transcript), len(resolved_members),
            )
            clean = TranscriptPreprocessor.process(transcript)
            logger.info("AI Pipeline — preprocessed: %d chars", len(clean))

            # Layer 3: Chunk
            chunks = TranscriptChunker.split(clean)
            total_chunks = len(chunks)
            logger.info("AI Pipeline — %d chunk(s) queued for parallel processing", total_chunks)

            # Build the system prompt once — shared across all chunks
            system_prompt = build_system_prompt(resolved_members, resolved_today)

            # Layer 5: Parallel extract + per-chunk validate
            chunk_results: dict[int, list[dict]] = {}

            with ThreadPoolExecutor(max_workers=min(MAX_PARALLEL_WORKERS, total_chunks)) as executor:
                futures = {
                    executor.submit(
                        _process_chunk,
                        chunk,
                        system_prompt,
                        resolved_members,
                        resolved_today,
                        idx,
                        total_chunks,
                    ): idx
                    for idx, chunk in enumerate(chunks)
                }
                for future in as_completed(futures):
                    idx = futures[future]
                    try:
                        chunk_results[idx] = future.result()
                    except Exception as exc:
                        logger.error("[Chunk %d] parallel processing raised: %s", idx + 1, exc)
                        chunk_results[idx] = []

            # Merge in chunk order to preserve meeting chronology
            all_validated: list[dict] = []
            for idx in range(total_chunks):
                all_validated.extend(chunk_results.get(idx, []))

            total_extracted = sum(
                len(chunk_results.get(i, [])) for i in range(total_chunks)
            )
            logger.info(
                "AI Pipeline — Parallel phase complete: %d task(s) across %d chunk(s)",
                total_extracted, total_chunks,
            )

            # Layer 6a: Task-identity-aware conflict resolution
            after_conflict = ConflictResolver.resolve(all_validated)

            # Layer 6b: Multi-field deduplication
            deduped = SemanticDeduplicator.deduplicate(after_conflict)

            # Layer 6c: Final lightweight consistency check
            consistent = run_final_consistency_check(deduped, resolved_members, resolved_today)

            # Layer 7: Rule engine — final gate
            final = RuleEngine.process(consistent, resolved_members, resolved_today)

            logger.info(
                "AI Pipeline COMPLETE -- "
                "extracted: %d | post-conflict: %d | deduped: %d | "
                "consistent: %d | final: %d",
                total_extracted,
                len(after_conflict),
                len(deduped),
                len(consistent),
                len(final),
            )
            return final

        except HTTPException:
            raise
        except RuntimeError as e:
            logger.error("AI Pipeline — LLM exhausted retries: %s", e)
            raise HTTPException(status_code=502, detail=f"AI Processing failed: {e}")
        except Exception as e:
            logger.error("AI Pipeline — unexpected error: %s", e)
            raise HTTPException(status_code=502, detail=f"AI Processing failed: {e}")
