"""
Canonical paper representation across all search sources.

Provides a single standardized dataclass that all API clients return,
eliminating field-name ambiguity (e.g., "journal/venue" vs "journal" vs "venue").
"""

import re
import string
from dataclasses import dataclass, field, asdict
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional


@dataclass
class Paper:
    """Canonical paper representation across all sources."""

    title: str
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    journal: str = ""
    doi: Optional[str] = None
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    source: str = "unknown"
    citation_count: Optional[int] = None
    url: Optional[str] = None
    doi_validated: bool = False
    open_access: bool = False
    added_date: Optional[str] = None

    # Internal fields preserved from raw API responses
    _raw_fields: Dict[str, Any] = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a plain dict suitable for JSON serialization."""
        d = asdict(self)
        d.pop("_raw_fields", None)
        # Drop keys with None / empty-list / empty-str values for cleaner JSON
        return {k: v for k, v in d.items()
                if v is not None and v != "" and v != [] and v is not False}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Paper":
        """Build a Paper from a raw dict (tolerant of field-name variants)."""
        # Normalize journal field — accept "journal/venue" or "venue"
        journal = (
            data.get("journal")
            or data.get("journal/venue")
            or data.get("venue")
            or ""
        )

        # Extract known fields, collect extras
        known = {f.name for f in cls.__dataclass_fields__.values()}
        extras = {k: v for k, v in data.items()
                  if k not in known and k != "_raw_fields"}

        return cls(
            title=(data.get("title") or "").strip(),
            authors=data.get("authors") or [],
            year=data.get("year"),
            journal=journal,
            doi=data.get("doi"),
            abstract=(data.get("abstract") or data.get("content") or "").strip() or None,
            keywords=data.get("keywords") or [],
            source=data.get("source", "unknown"),
            citation_count=data.get("citation_count"),
            url=data.get("url"),
            doi_validated=data.get("doi_validated", False),
            open_access=data.get("open_access", False),
            added_date=data.get("added_date"),
            _raw_fields=extras,
        )

    # ------------------------------------------------------------------
    # Matching helpers
    # ------------------------------------------------------------------

    def field_richness(self) -> int:
        """Count non-empty fields — used for merge priority."""
        count = 0
        for v in asdict(self).values():
            if v is not None and v != "" and v != [] and v is not False and v != 0:
                count += 1
        return count

    def normalize_title(self) -> str:
        """Lowercase, strip punctuation, collapse whitespace."""
        t = self.title.lower()
        t = t.translate(str.maketrans("", "", string.punctuation))
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def matches(self, other: "Paper", threshold: float = 0.85) -> bool:
        """Check if this paper matches another by DOI (exact) or title (fuzzy)."""
        # DOI match — case-insensitive
        if self.doi and other.doi:
            if self.doi.lower().strip() == other.doi.lower().strip():
                return True

        # Title fuzzy match
        t1 = self.normalize_title()
        t2 = other.normalize_title()
        if t1 and t2:
            return SequenceMatcher(None, t1, t2).ratio() >= threshold

        return False
