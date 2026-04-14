#!/usr/bin/env python3
"""
Semantic Scholar Enrichment Script

Enriches existing metadata.json entries with S2 data (abstracts, citations).
Designed to run in the background between interactive sessions, avoiding
the 300-second rate limit blocks that occur during live searches.

Uses conservative rate limiting (15s between requests) to stay within
the free tier (20 req/5min).

Usage:
    # Enrich up to 20 papers (default)
    python3 -m scripts.s2_enrich --topic coaching-papers

    # Dry run — see what would be enriched
    python3 -m scripts.s2_enrich --topic coaching-papers --dry-run

    # Custom batch size and delay
    python3 -m scripts.s2_enrich --topic coaching-papers --max 50 --delay 20

    # Run in background
    nohup python3 -m scripts.s2_enrich --topic coaching-papers &
"""

import sys
import json
import argparse
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .semantic_scholar_client import SemanticScholarClient
from .crossref_client import CrossRefClient
from .exceptions import RateLimitError, NotFoundError
from .config import DEFAULT_TOPIC, TOPICS_DIR
from .metadata_manager import MetadataManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [s2-enrich] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def find_papers_to_enrich(metadata: Dict[str, Any], source: str = None) -> List[str]:
    """Find DOIs of papers missing abstract or DOI."""
    papers = metadata.get("papers", {})
    needing_enrichment = []

    for doi, paper in papers.items():
        # Skip if source filter is set and this paper doesn't match
        if source:
            paper_source = paper.get("source", "")
            if paper_source != source:
                continue

        # Check what's missing
        has_doi = bool(paper.get("doi"))
        has_abstract = bool(paper.get("abstract"))

        if not has_doi or not has_abstract:
            # Use title hash as key if no DOI
            key = doi if has_doi else f"title:{paper.get('title', '')[:50]}"
            needing_enrichment.append(key)

    return needing_enrichment


def find_missing_dois(
    metadata: Dict[str, Any],
    crossref_client: CrossRefClient,
    source: str = None,
    crossref_delay: float = 1.1,
) -> int:
    """
    Find DOIs for papers that don't have them, using CrossRef.

    Args:
        metadata: Loaded metadata.json dict
        crossref_client: CrossRefClient instance
        source: Only process papers with this source (e.g., "markdown_reference")
        crossref_delay: Seconds between CrossRef requests

    Returns:
        Number of DOIs found
    """
    import time
    from difflib import SequenceMatcher

    papers = metadata.get("papers", {})
    found_count = 0

    for key, paper in papers.items():
        # Skip if already has DOI or source doesn't match
        if paper.get("doi"):
            continue
        if source and paper.get("source") != source:
            continue

        title = paper.get("title", "")
        if not title:
            continue

        # Build query: title + first author last name
        authors = paper.get("authors", [])
        first_author = authors[0].split(",")[0].strip() if authors else ""
        query = f"{title}"
        if first_author:
            query = f"{title} {first_author}"

        # Search CrossRef
        try:
            results = crossref_client.search_by_query(query, max_results=3)
        except Exception as e:
            logger.warning(f"CrossRef search failed for '{title[:40]}...': {e}")
            continue

        if not results:
            continue

        # Find best title match (>= 0.85 similarity)
        best_match = None
        best_similarity = 0.0

        for result in results:
            result_title = result.get("title", "")
            if result_title:
                similarity = SequenceMatcher(None, title.lower(), result_title.lower()).ratio()
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = result

        if best_match and best_similarity >= 0.85:
            # Found a match
            doi = best_match.get("doi")
            if doi:
                paper["doi"] = doi
                # Also get clean journal name from CrossRef
                if best_match.get("journal/venue") and not paper.get("journal"):
                    paper["journal"] = best_match["journal/venue"]
                found_count += 1
                logger.info(f"Found DOI: {doi} (similarity: {best_similarity:.2f})")

        # Rate limit delay
        time.sleep(crossref_delay)

    return found_count


def enrich_paper(
    client: SemanticScholarClient, doi: str, paper: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Look up a single paper on S2 and return enriched fields."""
    try:
        result = client.search_by_doi(doi)
        enriched = {}

        if result.get("abstract") and not paper.get("abstract"):
            enriched["abstract"] = result["abstract"]

        if result.get("year") and not paper.get("year"):
            enriched["year"] = result["year"]

        if result.get("journal/venue") and not paper.get("journal"):
            enriched["journal"] = result["journal/venue"]

        return enriched if enriched else None

    except NotFoundError:
        logger.info(f"Not found on S2: {doi}")
        return None
    except RateLimitError:
        raise
    except Exception as e:
        logger.warning(f"Failed to enrich {doi}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Enrich metadata.json with Semantic Scholar data"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=DEFAULT_TOPIC,
        help=f"Topic directory (default: {DEFAULT_TOPIC})",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=20,
        help="Maximum papers to enrich per run (default: 20)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=15.0,
        help="Seconds between API requests (default: 15)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be enriched without making API calls",
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Only enrich papers with this source (e.g., 'markdown_reference')",
    )
    parser.add_argument(
        "--crossref-only",
        action="store_true",
        help="Only run CrossRef DOI lookup, skip S2 enrichment",
    )

    args = parser.parse_args()

    # Load metadata
    metadata_path = TOPICS_DIR / args.topic / "metadata.json"
    if not metadata_path.exists():
        print(f"No metadata found at {metadata_path}", file=sys.stderr)
        sys.exit(1)

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    papers = metadata.get("papers", {})
    total = len(papers)

    # Phase 1: CrossRef DOI lookup (for papers without DOI)
    crossref_client = CrossRefClient()
    try:
        print("\n=== Phase 1: CrossRef DOI Lookup ===", file=sys.stderr)
        dois_found = find_missing_dois(
            metadata, crossref_client, source=args.source, crossref_delay=1.1
        )
        print(f"CrossRef: Found {dois_found} DOIs", file=sys.stderr)

        # Save intermediate state
        metadata["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"Saved intermediate state to {metadata_path}", file=sys.stderr)
    finally:
        crossref_client.close()

    # Re-find papers needing enrichment after DOI lookup
    dois_to_enrich = find_papers_to_enrich(metadata, source=args.source)
    batch = dois_to_enrich[: args.max]

    # Check if crossref-only mode
    if args.crossref_only:
        print(f"\nCrossRef-only mode: skipping S2 enrichment", file=sys.stderr)
        print(f"Found {len([p for p in papers.values() if p.get('doi')])} papers with DOIs", file=sys.stderr)
        return 0

    # Find papers needing enrichment
    dois_to_enrich = find_papers_to_enrich(metadata, source=args.source)
    batch = dois_to_enrich[: args.max]

    print(f"Papers in metadata: {total}", file=sys.stderr)
    print(f"Missing DOI/abstract/citations: {len(dois_to_enrich)}", file=sys.stderr)
    if args.source:
        print(f"Filtering by source: {args.source}", file=sys.stderr)
    print(f"Batch size: {len(batch)}", file=sys.stderr)

    if not batch:
        print("All papers already enriched!", file=sys.stderr)
        return 0

    if args.dry_run:
        print("\n--- DRY RUN ---", file=sys.stderr)
        for doi in batch:
            paper = papers[doi]
            missing = []
            if not paper.get("doi"):
                missing.append("doi")
            if not paper.get("abstract"):
                missing.append("abstract")
            title = paper.get("title", "Unknown")[:60]
            print(f"  {doi} — {title}... — missing: {', '.join(missing)}", file=sys.stderr)
        print(f"\nRun without --dry-run to enrich {len(batch)} papers.", file=sys.stderr)
        return 0

    # Enrich
    client = SemanticScholarClient()
    enriched_count = 0
    failed_count = 0

    try:
        for i, doi in enumerate(batch, 1):
            paper = papers[doi]
            title = paper.get("title", "Unknown")[:50]
            print(f"[{i}/{len(batch)}] {doi} — {title}...", file=sys.stderr)

            try:
                updates = enrich_paper(client, doi, paper)
                if updates:
                    paper.update(updates)
                    enriched_count += 1
                    fields = ", ".join(updates.keys())
                    print(f"  -> enriched: {fields}", file=sys.stderr)
                else:
                    print(f"  -> no new data", file=sys.stderr)
            except RateLimitError:
                print(f"\nRate limited after {enriched_count} enrichments. Stopping.", file=sys.stderr)
                break

            # Rate limit delay between requests
            if i < len(batch):
                time.sleep(args.delay)

    except KeyboardInterrupt:
        print(f"\nInterrupted after {enriched_count} enrichments.", file=sys.stderr)
    finally:
        client.close()

    # Save updated metadata
    metadata["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(
        f"\nDone: {enriched_count} enriched, {failed_count} failed "
        f"-> {metadata_path}",
        file=sys.stderr,
    )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)