#!/usr/bin/env python3
"""
Search Orchestrator for Portable Bibliography Hook

This module is called by the PreToolUse hook to execute literature searches
via direct API calls (CrossRef, Semantic Scholar, Tavily) instead of MCP WebSearch.

It receives search queries via stdin or command-line arguments, queries the APIs,
and formats the results for Claude to read.

Usage (from hook):
    echo '{"query": "latent class analysis", "max_results": 5}' | \\
    python .claude/skills/lit-search/scripts/search_orchestrator.py

Usage (CLI):
    python .claude/skills/lit-search/scripts/search_orchestrator.py \\
        --query "scale validation" \\
        --source crossref \\
        --max-results 5
"""

import sys
import json
import argparse
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Absolute imports - works when .claude is on PYTHONPATH
from scripts import CrossRefClient, SemanticScholarClient
from scripts.openalex_client import OpenAlexClient
from scripts.tavily_client import TavilySearchClient
from scripts.ssrn_client import search_ssrn
from scripts.exceptions import RateLimitError
from scripts.query_expander import expand_query
from scripts.config import (
    SEARCH_RESULTS_PATH,
    TEMP_DIR,
    validate_configuration,
    DEFAULT_MAX_RESULTS,
    get_abs_issns,
    get_abs_journal_names,
    MERGE_SOURCE_PRIORITY,
    QUERY_EXPANSION_ENABLED,
    DEFAULT_DOMAIN,
)
from scripts import doi_utils
from scripts.metadata_manager import MetadataManager
from scripts.shared_types import Paper
from difflib import SequenceMatcher


# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def format_papers_markdown(
    query: str,
    results: List[Dict[str, Any]],
    source: str = "API",
    mode: str = "search",
) -> str:
    """
    Format paper metadata as Markdown for Claude to read.

    Args:
        query: The original search query or reference identifier
        results: List of paper metadata from API
        source: API source name
        mode: "search" for full results, "references" for compact reference lists

    Returns:
        Formatted Markdown string
    """
    lines = []

    # Header
    if mode == "references":
        lines.append(f'# References: "{query}"')
    else:
        lines.append(f'# Search Results: "{query}"')
    lines.append("")

    # Statistics
    papers_with_doi = sum(1 for p in results if p.get("doi"))

    if mode == "references":
        validated_dois = sum(1 for p in results if p.get("doi_validated"))
        lines.append(f"Found {len(results)} references. "
                     f"{papers_with_doi} with DOI ({validated_dois} validated).")
    else:
        validated_dois = sum(1 for p in results if p.get("doi_validated"))
        supplemented_dois = sum(1 for p in results if p.get("doi_supplemented"))
        lines.append(f"Found {len(results)} papers from {source}.")
        lines.append(f"**Statistics**: {papers_with_doi}/{len(results)} papers with DOI, "
                     f"{validated_dois} validated, {supplemented_dois} supplemented")
    lines.append("")

    if not results:
        if mode == "references":
            lines.append("No references found.")
        else:
            lines.append("No results found. Please try a different query.")
        return "\n".join(lines)

    for i, paper in enumerate(results, 1):
        # Title and authors
        title = paper.get("title", "Unknown Title")
        authors = paper.get("authors", [])
        if authors:
            if len(authors) > 3:
                authors_str = ", ".join(authors[:3]) + f", et al. ({len(authors)} authors)"
            else:
                authors_str = ", ".join(authors)
        else:
            authors_str = "Unknown Authors"

        lines.append(f"## {i}. {title}")
        lines.append(f"**Authors**: {authors_str}")

        # Year and venue
        year = paper.get("year")
        venue = paper.get("journal/venue") or paper.get("venue")
        if year or venue:
            parts = []
            if year:
                parts.append(str(year))
            if venue:
                parts.append(venue)
            lines.append(f"**Published**: {' / '.join(parts)}")

        # DOI with validation indicator
        doi = paper.get("doi")
        if doi:
            validated = paper.get("doi_validated", False)
            supplemented = paper.get("doi_supplemented", False)
            if validated:
                indicator = "✓" if not supplemented else "✓ (supplemented)"
            else:
                indicator = "⚠"
            lines.append(f"**DOI**: {indicator} {doi}")
        else:
            lines.append("**DOI**: Not found")

        # Search-mode-only fields
        if mode == "search":
            citation_count = paper.get("citation_count")
            if citation_count:
                lines.append(f"**Citations**: {citation_count}")

            url = paper.get("url")
            if url:
                lines.append(f"**URL**: {url}")

            abstract = paper.get("abstract")
            if abstract:
                if len(abstract) > 500:
                    abstract = abstract[:500] + "..."
                lines.append(f"**Abstract**: {abstract}")

            source_name = paper.get("source", "unknown")
            lines.append(f"**Source**: {source_name}")

        lines.append("")  # Empty line between papers

    return "\n".join(lines)


# Backward-compatible aliases
format_results_markdown = format_papers_markdown
format_references_markdown = lambda query, results: format_papers_markdown(query, results, mode="references")


def merge_papers_by_doi(
    papers: List[Dict[str, Any]],
    priority: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    Merge papers from multiple sources by DOI.

    Priority: OpenAlex > CrossRef > Semantic Scholar > Tavily > SSRN
    For papers without DOI, merge by title similarity.

    Args:
        papers: List of paper metadata from multiple sources
        priority: Source priority order (highest to lowest)

    Returns:
        Merged list with unique papers, using highest priority source for each DOI
    """
    if priority is None:
        priority = MERGE_SOURCE_PRIORITY
    papers_by_doi = {}  # doi -> list of papers
    papers_without_doi = []

    for paper in papers:
        doi = paper.get("doi", "")
        if doi and doi_utils.validate_doi_format(doi):
            if doi not in papers_by_doi:
                papers_by_doi[doi] = []
            papers_by_doi[doi].append(paper)
        else:
            papers_without_doi.append(paper)

    # Select paper with richest metadata for each DOI
    merged_results = []
    for doi, paper_list in papers_by_doi.items():
        # Sort by: (1) non-empty field count descending, (2) source priority
        def _field_richness(p):
            return sum(1 for v in p.values()
                       if v is not None and v != "" and v != [] and v != 0)

        paper_list.sort(key=lambda p: (
            _field_richness(p),
            -priority.index(p.get("source", "google_scholar"))
            if p.get("source") in priority else -len(priority)
        ), reverse=True)

        # Start with highest priority paper
        merged = paper_list[0].copy()

        # Fill missing fields from lower priority sources
        for paper in paper_list[1:]:
            for key, value in paper.items():
                if not merged.get(key) and value:
                    merged[key] = value

        merged_results.append(merged)

    # Handle papers without DOI - merge by title similarity
    used_indices = set()
    for paper in papers_without_doi:
        title = paper.get("title", "").lower().strip()
        if not title:
            merged_results.append(paper)
            continue

        # Check if similar title already exists
        found_similar = False
        for i, existing in enumerate(merged_results):
            existing_title = existing.get("title", "").lower().strip()
            if existing_title and SequenceMatcher(None, title, existing_title).ratio() > 0.85:
                # Similar title - merge this paper into existing
                for key, value in paper.items():
                    if not existing.get(key) and value:
                        existing[key] = value
                found_similar = True
                break

        if not found_similar:
            merged_results.append(paper)

    logger.info(f"Merged {len(papers)} papers into {len(merged_results)} unique papers")
    return merged_results


def supplement_missing_dois(
    papers: List[Dict[str, Any]],
    max_attempts: int = None
) -> List[Dict[str, Any]]:
    """
    For papers without DOI, search CrossRef by title to find DOI.

    Args:
        papers: List of paper metadata
        max_attempts: Max papers to supplement (default: adaptive up to 10)

    Returns:
        Updated list with DOIs supplemented where found
    """
    papers_without_doi = [p for p in papers if not p.get("doi") and p.get("title")]

    if not papers_without_doi:
        return papers

    # Adaptive cap: supplement up to min(10, count_without_doi)
    if max_attempts is None:
        max_attempts = min(10, len(papers_without_doi))

    # Limit attempts to avoid rate limits
    to_supplement = papers_without_doi[:max_attempts]

    logger.info(f"Attempting to supplement DOI for {len(to_supplement)} papers")

    # Create result set with copies
    updated_papers = list(papers)

    for paper in to_supplement:
        title = paper.get("title", "")
        authors = paper.get("authors", [])

        if not title:
            continue

        # Build search query: title + first author (if available)
        query = title
        if authors:
            # Extract last name of first author
            first_author_last = authors[0].split()[-1]
            query = f"{title} {first_author_last}"

        try:
            # Search CrossRef
            client = CrossRefClient()
            results = client.search_by_query(query, max_results=3)
            client.close()

            # Find best match by title similarity
            for result in results:
                result_title = result.get("title", "")
                if result_title:
                    similarity = SequenceMatcher(
                        None,
                        title.lower(),
                        result_title.lower()
                    ).ratio()

                    result_doi = result.get("doi", "")

                    # High similarity + valid DOI = match
                    if similarity >= 0.9 and result_doi and doi_utils.validate_doi_format(result_doi):
                        # Found DOI - update the paper
                        for i, p in enumerate(updated_papers):
                            if p is paper:
                                updated_papers[i]["doi"] = result_doi
                                updated_papers[i]["doi_validated"] = True
                                updated_papers[i]["doi_supplemented"] = True
                                # Also copy other useful fields if missing
                                if not p.get("year") and result.get("year"):
                                    updated_papers[i]["year"] = result["year"]
                                if not p.get("journal/venue") and result.get("journal/venue"):
                                    updated_papers[i]["journal/venue"] = result["journal/venue"]
                                logger.info(f"Supplemented DOI for '{title[:50]}...': {result_doi}")
                                break
                        break

        except Exception as e:
            logger.warning(f"DOI supplementation failed for '{title[:50]}...': {e}")

    # Count supplemented
    supplemented_count = sum(1 for p in updated_papers if p.get("doi_supplemented"))
    if supplemented_count > 0:
        logger.info(f"Successfully supplemented {supplemented_count} DOIs")

    return updated_papers


def search_crossref(
    query: str,
    max_results: int = 10,
    issns: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Search CrossRef for papers.

    Args:
        query: Search query
        max_results: Maximum number of results
        issns: Optional list of ISSNs to filter by

    Returns:
        List of paper metadata
    """
    try:
        client = CrossRefClient()
        results = client.search_by_query(query, max_results=max_results, issn=issns)
        client.close()
        return results
    except Exception as e:
        logger.error(f"CrossRef search failed: {e}")
        return []


def search_semantic_scholar(
    query: str,
    max_results: int = 10,
    journal_names: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Search Semantic Scholar for papers.

    Args:
        query: Search query
        max_results: Maximum number of results
        journal_names: Optional list of journal names to filter by

    Returns:
        List of paper metadata
    """
    try:
        client = SemanticScholarClient()
        results = client.search_by_query(
            query,
            max_results=max_results,
            journal_names=journal_names,
        )
        client.close()
        return results
    except RateLimitError:
        print(
            "⚠ Semantic Scholar rate limited — returning CrossRef/Tavily results only.\n"
            "  Run enrichment later: python3 -m scripts.s2_enrich --topic coaching-papers",
            file=sys.stderr,
        )
        return []
    except Exception as e:
        logger.error(f"Semantic Scholar search failed: {e}")
        return []


def search_google_scholar(
    query: str,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """
    Search Google Scholar via Tavily with domain restriction.

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        List of search results with Google Scholar as source
    """
    try:
        client = TavilySearchClient()
        results = client.search_google_scholar(query, max_results=max_results)
        return results
    except Exception as e:
        logger.error(f"Google Scholar search failed: {e}")
        return []


def search_openalex(
    query: str,
    max_results: int = 10,
    issns: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Search OpenAlex for papers.

    Args:
        query: Search query
        max_results: Maximum number of results
        issns: Optional list of ISSNs for journal filtering

    Returns:
        List of paper metadata
    """
    try:
        client = OpenAlexClient()
        if issns:
            results = client.search_by_issn_batch(query, issns, max_results=max_results)
        else:
            results = client.search_by_query(query, max_results=max_results)
        client.close()
        return results
    except Exception as e:
        logger.error(f"OpenAlex search failed: {e}")
        return []


def search_citation_chain(
    seed_dois: List[str],
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """Citation chaining: find papers cited by seed papers.

    Uses SemanticScholarClient.get_references() for each seed DOI.
    Fails fast on S2 rate limits.
    """
    all_refs = []
    client = SemanticScholarClient()
    try:
        for doi in seed_dois:
            try:
                refs = client.get_references(f"DOI:{doi}", max_results=max_results)
                all_refs.extend(refs)
            except RateLimitError:
                logger.warning("S2 rate limited during citation chaining. Stopping.")
                break
            except Exception as e:
                logger.warning(f"Citation chain failed for {doi}: {e}")
    finally:
        client.close()

    return merge_papers_by_doi(all_refs)


def search_all_apis(
    query: str,
    max_results: int = 10,
    issns: Optional[List[str]] = None,
    journal_names: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Search all available APIs and combine results with smart multi-round retrieval.

    Args:
        query: Search query
        max_results: Maximum number of results per API
        issns: Optional list of ISSNs for CrossRef filtering
        journal_names: Optional list of journal names for Semantic Scholar filtering

    Returns:
        Combined list of paper metadata (merged by DOI, with DOI supplementation)
    """
    all_results = []

    # OpenAlex first — has abstracts + ISSN batch in one call
    openalex_results = search_openalex(query, max_results, issns=issns)
    all_results.extend(openalex_results)

    # CrossRef — good DOI coverage, ISSN batch
    crossref_results = search_crossref(query, max_results, issns=issns)
    all_results.extend(crossref_results)

    # Search Semantic Scholar with journal filter
    semantic_results = search_semantic_scholar(query, max_results, journal_names=journal_names)
    all_results.extend(semantic_results)

    # Search Google Scholar via Tavily
    tavily_results = search_google_scholar(query, max_results)
    all_results.extend(tavily_results)

    # Merge by DOI (CrossRef priority)
    merged_results = merge_papers_by_doi(all_results)

    # Smart multi-round: if results < max_results, try supplementation
    if len(merged_results) < max_results:
        logger.info(f"Only {len(merged_results)} results found, attempting DOI supplementation...")
        supplemented_results = supplement_missing_dois(merged_results)
        if len(supplemented_results) > len(merged_results):
            logger.info(f"Supplemented {len(supplemented_results) - len(merged_results)} DOIs")
        merged_results = supplemented_results

    return merged_results


def save_results(results_markdown: str) -> str:
    """
    Save search results to the temp file.

    Args:
        results_markdown: Formatted results as Markdown

    Returns:
        Path to the saved file
    """
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    with open(SEARCH_RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write(results_markdown)

    logger.info(f"Results saved to {SEARCH_RESULTS_PATH}")
    return str(SEARCH_RESULTS_PATH)


def _persist_metadata(
    args, results: List[Dict[str, Any]], search_query: str = ""
) -> None:
    """Persist search results to metadata.json (non-fatal)."""
    if not results:
        return
    try:
        from scripts.config import DEFAULT_TOPIC
        topic = args.topic or DEFAULT_TOPIC
        manager = MetadataManager(topic=topic)
        stats = manager.add_papers(results, search_query=search_query or "")
        logger.info(
            f"Metadata updated: +{stats['added']} new, "
            f"~{stats['updated']} updated, {stats['skipped']} skipped"
        )
        print(
            f"Metadata: {stats['added']} new, {stats['updated']} updated "
            f"→ references/{topic}/metadata.json",
            file=sys.stderr,
        )
    except Exception as e:
        logger.warning(f"Metadata collection failed (non-fatal): {e}")


def main():
    """Main entry point for the search orchestrator."""
    parser = argparse.ArgumentParser(
        description="Search academic literature databases via API"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Search query"
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=["crossref", "semantic-scholar", "google-scholar", "openalex", "ssrn", "all"],
        default="all",
        help="API source to query (default: all)"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help=f"Maximum results per API (default: {DEFAULT_MAX_RESULTS})"
    )
    parser.add_argument(
        "--abs-rating",
        type=str,
        choices=["3", "4", "4*", "all"],
        help="Filter by ABS journal rating (3, 4, 4*, or all for 3+)"
    )
    parser.add_argument(
        "--field",
        type=str,
        help="Filter by academic field (e.g., Management, Psychology)"
    )
    parser.add_argument(
        "--issn",
        type=str,
        help="Filter by specific ISSN (comma-separated for multiple)"
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["markdown", "json", "stdout"],
        default="file",
        help="Output format (default: save to file)"
    )
    parser.add_argument(
        "--references",
        type=str,
        help="Extract references from a markdown file (path to .md file)"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Topic directory for metadata storage under references/ (default: coaching-papers)"
    )
    parser.add_argument(
        "--expand",
        action="store_true",
        help="Expand query with synonyms and related terms",
    )
    parser.add_argument(
        "--chain",
        type=str,
        help="Citation chaining: comma-separated seed DOIs",
    )

    args = parser.parse_args()

    # Handle --references mode (markdown file path only)
    if args.references:
        from pathlib import Path
        from .convert_pdfs_to_md import extract_and_save_references

        md_path = Path(args.references)
        if not md_path.exists():
            print(f"Error: File not found: {md_path}", file=sys.stderr)
            sys.exit(1)

        if md_path.suffix != ".md":
            print(f"Error: --references requires a markdown file (.md)", file=sys.stderr)
            sys.exit(1)

        # Extract references from markdown and save to metadata.json
        results = extract_and_save_references(md_path, args.topic or DEFAULT_TOPIC)
        source_label = md_path.stem

        results_markdown = format_papers_markdown(source_label, results, mode="references")

        # Output
        output = args.output
        if output == "file":
            file_path = save_results(results_markdown)
            print(f"Results saved to: {file_path}", file=sys.stderr)
            print(results_markdown)
        elif output == "stdout":
            print(results_markdown)
        elif output == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))

        # Note: metadata is already saved by extract_and_save_references()
        print(f"\nNext step: Enrich with DOIs and abstracts:", file=sys.stderr)
        print(f"  python3 -m scripts.s2_enrich --topic {args.topic or DEFAULT_TOPIC} --source markdown_reference", file=sys.stderr)

        return 0
    query = args.query
    if not query and not args.chain:
        try:
            stdin_data = json.load(sys.stdin)
            query = stdin_data.get("query", "")
            max_results = stdin_data.get("max_results", args.max_results)
            source = stdin_data.get("source", args.source)
        except (json.JSONDecodeError, KeyError, IOError):
            parser.print_help()
            sys.exit(1)
    else:
        max_results = args.max_results
        source = args.source

    if not query and not args.chain:
        print("Error: No query provided", file=sys.stderr)
        sys.exit(1)

    # Handle --chain mode (citation chaining)
    if args.chain:
        seed_dois = [d.strip() for d in args.chain.split(",") if d.strip()]
        if not seed_dois:
            print("Error: --chain requires comma-separated DOIs", file=sys.stderr)
            sys.exit(1)
        results = search_citation_chain(seed_dois, max_results=args.max_results)
        source_name = f"Citation chain ({len(seed_dois)} seeds)"
        results_markdown = format_results_markdown(args.chain, results, source_name)
        output = args.output
        if output == "file":
            file_path = save_results(results_markdown)
            print(f"Results saved to: {file_path}", file=sys.stderr)
            print(results_markdown)
        elif output == "stdout":
            print(results_markdown)
        elif output == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
        _persist_metadata(args, results, f"chain:{args.chain}")
        return 0

    # Handle ABS journal filtering
    issns = None
    journal_names = None

    if args.issn:
        # Direct ISSN filter takes precedence
        issns = [issn.strip() for issn in args.issn.split(",")]
    elif args.abs_rating:
        # Get ABS journal data
        rating = args.abs_rating.upper() if args.abs_rating != "all" else None
        field = args.field

        try:
            issns = get_abs_issns(rating=rating, field=field)
            journal_names = get_abs_journal_names(rating=rating, field=field)

            if issns:
                logger.info(f"Filtering by ABS {args.abs_rating} journals ({len(issns)} ISSNs)")
            if field:
                logger.info(f"Field filter: {field}")
        except FileNotFoundError as e:
            logger.warning(f"ABS journals file not found: {e}. Proceeding without journal filter.")

    # Check configuration
    warnings = validate_configuration()
    if warnings and logger.isEnabledFor(logging.WARNING):
        for warning in warnings:
            logger.warning(warning)

    # Perform search
    logger.info(f"Searching for: {query} (source={source}, max_results={max_results})")

    # Handle query expansion
    if args.expand:
        queries = expand_query(query, domain=DEFAULT_DOMAIN)
        if len(queries) > 1:
            print(f"Query expansion: {len(queries)} variants", file=sys.stderr)
            for i, q in enumerate(queries):
                print(f"  [{i+1}] {q}", file=sys.stderr)
    else:
        queries = [query]

    # Execute searches for all query variants
    all_variant_results = []
    for q in queries:
        if source == "crossref":
            variant_results = search_crossref(q, max_results, issns=issns)
            source_name = "CrossRef"
        elif source == "semantic-scholar":
            variant_results = search_semantic_scholar(q, max_results, journal_names=journal_names)
            source_name = "Semantic Scholar"
        elif source == "google-scholar":
            variant_results = search_google_scholar(q, max_results)
            source_name = "Google Scholar (via Tavily)"
        elif source == "openalex":
            variant_results = search_openalex(q, max_results, issns=issns)
            source_name = "OpenAlex"
        elif source == "ssrn":
            variant_results = search_ssrn(q, max_results)
            source_name = "SSRN (via Tavily)"
        else:  # all
            variant_results = search_all_apis(q, max_results, issns=issns, journal_names=journal_names)
            source_name = "OpenAlex + CrossRef + Semantic Scholar"
        all_variant_results.extend(variant_results)

    # Merge results across query variants
    if len(queries) > 1:
        results = merge_papers_by_doi(all_variant_results)
    else:
        results = all_variant_results

    # Format results
    results_markdown = format_results_markdown(query, results, source_name)

    # Output results
    output = args.output
    if output == "file":
        # Save to temp file
        file_path = save_results(results_markdown)
        print(f"Results saved to: {file_path}", file=sys.stderr)
        print(results_markdown)  # Also print to stdout for the hook
    elif output == "stdout":
        print(results_markdown)
    elif output == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))

    # Persist metadata (non-fatal)
    _persist_metadata(args, results, query)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
