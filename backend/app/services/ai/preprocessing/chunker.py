"""
preprocessing/chunker.py — Layer 3: Transcript Chunker.

Splits arbitrarily long transcripts into overlapping chunks that fit
within the Azure OpenAI context window.
"""

from ..config import CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS


class TranscriptChunker:
    """
    Split a transcript of arbitrary length into overlapping chunks.

    Design
    ------
    * Target chunk size: CHUNK_SIZE_CHARS characters (default 32,000).
    * Overlap: CHUNK_OVERLAP_CHARS characters (default 500) so that tasks
      spanning a chunk boundary are not missed.
    * Splits are always on newline boundaries — a speaker turn is never split.
    * Short transcripts (<= chunk_size) return a single-element list.
    """

    @staticmethod
    def split(
        transcript: str,
        chunk_size: int = CHUNK_SIZE_CHARS,
        overlap: int = CHUNK_OVERLAP_CHARS,
    ) -> list[str]:
        """Return a list of transcript chunks."""
        if len(transcript) <= chunk_size:
            return [transcript]

        lines = transcript.splitlines(keepends=True)
        chunks: list[str] = []
        current = ""

        for line in lines:
            if len(current) + len(line) > chunk_size and current:
                chunks.append(current.strip())
                tail = current[-overlap:] if len(current) > overlap else current
                current = tail + line
            else:
                current += line

        if current.strip():
            chunks.append(current.strip())

        return chunks
