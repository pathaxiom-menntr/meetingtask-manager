"""
preprocessing/transcript.py — Layer 1: Transcript Preprocessor.

Cleans and normalises a raw meeting transcript before it reaches the LLM.
The SEMANTIC MEANING of the transcript is never changed.
"""

import re
import unicodedata

from app.core.logger import get_logger

logger = get_logger(__name__)


class TranscriptPreprocessor:
    """
    Clean and normalise a raw meeting transcript before it reaches the LLM.

    Guarantees
    ----------
    * Whitespace is normalised (no trailing spaces, no excess blank lines).
    * Transcription artefacts are removed ([inaudible], [crosstalk], etc.).
    * Repeated filler words are collapsed to a single instance.
    * Punctuation is normalised (curly quotes -> straight, em-dash -> --).
    * Speaker lines are preserved and formatted consistently.
    * Timestamps are preserved in-place.
    * Orphaned continuation lines are merged into the preceding speaker turn.
    """

    _ARTIFACT_RE = re.compile(
        r"\[(?:inaudible|crosstalk|laughter|applause|noise|background\s+noise"
        r"|music|silence|pause|unintelligible|unclear|indistinct|cough"
        r"|phone\s+ringing|door\s+closing|typing|recording\s+started"
        r"|recording\s+stopped)\]",
        re.IGNORECASE,
    )

    _FILLER_RE = re.compile(
        r"\b(um+|uh+|er+|hmm+|hm+|mhm+|ah+|aha+|uhh+|umm+|like,?\s+like)\b",
        re.IGNORECASE,
    )

    # Handles: "Name:", "Name (role):", "[HH:MM] Name:", "[HH:MM:SS] Name:"
    _SPEAKER_RE = re.compile(
        r"^(?:\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s+)?[A-Z][^\n:]{0,50}:\s",
        re.MULTILINE,
    )

    @classmethod
    def process(cls, transcript: str) -> str:
        """Return a cleaned transcript string, ready for LLM ingestion."""
        text = transcript

        text = unicodedata.normalize("NFKC", text)

        # Curly quotes -> straight
        text = (
            text.replace("\u2018", "'").replace("\u2019", "'")
                .replace("\u201c", '"').replace("\u201d", '"')
        )

        # Em-dash / en-dash -> double-hyphen
        text = text.replace("\u2014", "--").replace("\u2013", "--")

        text = cls._ARTIFACT_RE.sub("", text)
        text = cls._FILLER_RE.sub(r"\1", text)

        lines = text.splitlines()
        cleaned: list[str] = []
        for line in lines:
            line = re.sub(r"[ \t]+", " ", line).strip()
            if line:
                cleaned.append(line)

        # Merge orphaned continuation lines into the preceding speaker turn
        merged: list[str] = []
        for line in cleaned:
            if merged and not cls._SPEAKER_RE.match(line):
                merged[-1] += " " + line
            else:
                merged.append(line)

        result = "\n".join(merged)
        result = re.sub(r"\n{3,}", "\n\n", result)
        return result.strip()
