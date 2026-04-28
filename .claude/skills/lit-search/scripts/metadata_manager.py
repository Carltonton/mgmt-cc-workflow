"""
Metadata Manager for Bibliography Search System

Persists structured paper metadata (title, authors, year, DOI, abstract, etc.)
to docs/{topic}/metadata.json. Deduplicates by DOI (primary) or
normalized title hash (fallback). Supports append-or-update semantics.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from .config import (
    TOPICS_DIR,
    DEFAULT_TOPIC,
    METADATA_FILENAME,
)

logger = logging.getLogger(__name__)


class MetadataManager:
    """Manages persistent paper metadata stored as JSON."""

    def __init__(self, topic: str = DEFAULT_TOPIC):
        self.topic = topic
        self.metadata_path = TOPICS_DIR / topic / METADATA_FILENAME

    def load(self) -> Dict[str, Any]:
        """Load existing metadata.json or return an empty template."""
        if not self.metadata_path.exists():
            return self._empty_template()

        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Ensure expected structure
            if "_meta" not in data or "papers" not in data:
                logger.warning(
                    f"metadata.json at {self.metadata_path} has unexpected structure; starting fresh"
                )
                return self._empty_template()
            return data
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Could not load metadata.json: {e}; starting fresh")
            return self._empty_template()

    def save(self, data: Dict[str, Any]) -> None:
        """Save metadata.json, updating _meta timestamps."""
        now = datetime.now(timezone.utc).isoformat()
        data["_meta"]["last_updated"] = now
        data["_meta"]["total_entries"] = len(data["papers"])
        if not data["_meta"].get("created_date"):
            data["_meta"]["created_date"] = now

        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Metadata saved to {self.metadata_path} ({data['_meta']['total_entries']} entries)")

    def add_papers(
        self, papers: List[Dict[str, Any]], search_query: str = ""
    ) -> Dict[str, int]:
        """Add papers from API results to the metadata store.

        Normalizes each paper, deduplicates by DOI or title, and merges
        into the existing metadata file.

        Args:
            papers: Raw API result dicts (from search_orchestrator)
            search_query: The query that produced these results

        Returns:
            Stats dict: {"added": N, "updated": M, "skipped": K}
        """
        if not papers:
            return {"added": 0, "updated": 0, "skipped": 0}

        data = self.load()
        stats = {"added": 0, "updated": 0, "skipped": 0}
        now = datetime.now(timezone.utc).isoformat()

        for paper in papers:
            canonical = self._normalize_paper(paper, search_query)
            if not canonical.get("title"):
                stats["skipped"] += 1
                continue

            key = self._get_dedup_key(canonical)

            if key in data["papers"]:
                # Update existing entry
                entry = data["papers"][key]
                # Fill missing fields from new data
                fillable_fields = [
                    "abstract", "authors", "journal", "year", "keywords",
                ]
                for field in fillable_fields:
                    if not entry.get(field) and canonical.get(field):
                        entry[field] = canonical[field]
                stats["updated"] += 1
            else:
                canonical["added_date"] = now
                data["papers"][key] = canonical
                stats["added"] += 1

        self.save(data)
        return stats

    def _normalize_paper(
        self, paper: Dict[str, Any], search_query: str = ""
    ) -> Dict[str, Any]:
        """Map raw API result fields to canonical metadata schema.

        Handles field name differences across CrossRef, Semantic Scholar,
        OpenAlex, Tavily, and other sources.
        """
        now = datetime.now(timezone.utc).isoformat()
        doi = paper.get("doi") or None
        if doi:
            doi = doi.strip().lower()

        # Accept "journal/venue", "venue", or "journal"
        journal = (
            paper.get("journal")
            or paper.get("journal/venue")
            or paper.get("venue")
            or None
        )

        return {
            "title": (paper.get("title") or "").strip(),
            "authors": paper.get("authors") or [],
            "year": paper.get("year"),
            "journal": journal,
            "doi": doi,
            "abstract": (paper.get("abstract") or paper.get("content") or "").strip() or None,
            "keywords": paper.get("keywords") or [],
            "source": paper.get("source", "unknown"),
            "added_date": now,
        }

    def _get_dedup_key(self, paper: Dict[str, Any]) -> str:
        """Return deduplication key: DOI if present, else title hash."""
        doi = paper.get("doi")
        if doi:
            return doi.lower().strip()

        title = paper.get("title", "").lower().strip()
        if title:
            title_hash = hashlib.md5(title.encode("utf-8")).hexdigest()[:12]
            return f"title_{title_hash}"

        # Fallback: random-ish key (very unlikely to match)
        return f"unknown_{hashlib.md5(str(paper).encode()).hexdigest()[:12]}"

    def _empty_template(self) -> Dict[str, Any]:
        """Return an empty metadata template."""
        return {
            "_meta": {
                "topic": self.topic,
                "last_updated": "",
                "total_entries": 0,
                "created_date": "",
            },
            "papers": {},
        }

    def get_all_papers(self) -> List[Dict[str, Any]]:
        """Return all papers as a flat list (with their dedup keys)."""
        data = self.load()
        result = []
        for key, paper in data["papers"].items():
            entry = dict(paper)
            entry["_key"] = key
            result.append(entry)
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Return collection statistics."""
        data = self.load()
        papers = data["papers"]
        years = [p.get("year") for p in papers.values() if p.get("year")]

        return {
            "topic": self.topic,
            "total_entries": len(papers),
            "with_doi": sum(1 for p in papers.values() if p.get("doi")),
            "with_abstract": sum(1 for p in papers.values() if p.get("abstract")),
            "year_range": f"{min(years)}-{max(years)}" if years else "N/A",
            "last_updated": data["_meta"].get("last_updated", ""),
        }
