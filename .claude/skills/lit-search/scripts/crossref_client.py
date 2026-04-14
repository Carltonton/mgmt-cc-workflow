"""
CrossRef API client for academic bibliography search.

This module implements the CrossRef API client, which provides access to
15,000+ journals from various publishers. CrossRef is an open API that
doesn't require authentication for basic usage.

API Documentation: https://api.crossref.org/
"""

import logging
from typing import List, Dict, Any, Optional, Union
import re

from .api_base import BaseAPIClient
from .config import (
    CROSSREF_API_URL,
    CROSSREF_USER_AGENT,
)
from .exceptions import NotFoundError
from . import doi_utils


# Configure logging
logger = logging.getLogger(__name__)


class CrossRefClient(BaseAPIClient):
    """
    Client for the CrossRef API.

    CrossRef is a free, open API that provides metadata for millions of
    academic papers from 15,000+ journals. No authentication is required,
    but polite usage (rate limiting) is recommended.

    Example:
        >>> from scripts.python.bibliography import CrossRefClient
        >>> client = CrossRefClient()
        >>> paper = client.search_by_doi("10.1287/mksc.2018.0886")
        >>> print(paper['title'])
        >>> results = client.search_by_query("organizational behavior", max_results=5)
        >>> for paper in results:
        ...     print(f"{paper['title']} ({paper['year']})")
    """

    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize the CrossRef client.

        Args:
            rate_limit: Minimum seconds between API calls (default: 1.0)
                       CrossRef recommends polite rate limiting.
        """
        super().__init__(rate_limit=rate_limit)
        logger.info("CrossRef client initialized")

    def _get_user_agent(self) -> str:
        """Get the User-Agent header for CrossRef API requests."""
        return CROSSREF_USER_AGENT

    def _build_doi_url(self, doi: str) -> str:
        """
        Build the URL for a DOI lookup.

        Args:
            doi: The DOI to look up

        Returns:
            Full URL for the DOI lookup
        """
        return f"{CROSSREF_API_URL}/{doi}"

    def _build_query_url(self, query: str, max_results: int = 10) -> str:
        """
        Build the URL for a query search.

        Args:
            query: The search query
            max_results: Maximum number of results to return

        Returns:
            Full URL for the search with query parameters
        """
        # URL encode the query
        encoded_query = query.replace(" ", "+").lower()

        # Build URL with parameters
        url = f"{CROSSREF_API_URL}?query={encoded_query}&rows={max_results}"
        return url

    def _parse_doi_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the CrossRef API response for a DOI lookup.

        Args:
            response: Raw CrossRef API response as a dictionary

        Returns:
            Parsed paper metadata in standard format

        Raises:
            NotFoundError: If the DOI is not found in the response
        """
        # CrossRef returns the actual data in 'message' field
        message = response.get("message", {})

        # Check if this is a valid response
        if not message or "title" not in message:
            raise NotFoundError(
                message="DOI not found or has no metadata",
                resource_type="DOI",
            )

        return self._extract_paper_metadata(message)

    def _parse_query_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the CrossRef API response for a query search.

        Args:
            response: Raw CrossRef API response as a dictionary

        Returns:
            List of parsed paper metadata in standard format
        """
        message = response.get("message", {})
        items = message.get("items", [])

        results = []
        for item in items:
            try:
                metadata = self._extract_paper_metadata(item)
                results.append(metadata)
            except Exception as e:
                # Log but continue parsing other items
                logger.warning(f"Failed to parse item: {e}")

        logger.info(f"Parsed {len(results)} papers from CrossRef")
        return results

    def _extract_paper_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract paper metadata from a CrossRef API item.

        Args:
            item: A single item from the CrossRef API response

        Returns:
            Paper metadata in standard format
        """
        # Extract title
        title = ""
        if "title" in item and item["title"]:
            title = item["title"][0] if isinstance(item["title"], list) else item["title"]

        # Extract authors
        authors = []
        if "author" in item:
            for author in item["author"]:
                if "given" in author and "family" in author:
                    authors.append(f"{author['given']} {author['family']}")
                elif "family" in author:
                    authors.append(author["family"])

        # Extract year
        year = None
        if "published" in item and item["published"]:
            # 'published' is a list of date parts
            try:
                date_parts = item["published"][0]["date-parts"][0]
                year = date_parts[0] if date_parts else None
            except (IndexError, KeyError, TypeError):
                pass

        if year is None and "issued" in item and item["issued"]:
            try:
                date_parts = item["issued"][0]["date-parts"][0]
                year = date_parts[0] if date_parts else None
            except (IndexError, KeyError, TypeError):
                pass

        # Extract journal/venue
        journal = ""
        if "container-title" in item and item["container-title"]:
            journal = item["container-title"][0] if isinstance(item["container-title"], list) else item["container-title"]
        elif "publisher" in item:
            journal = item["publisher"]

        # Extract DOI
        doi = item.get("DOI", "")
        # Clean and validate DOI format
        doi_validated = False
        if doi:
            doi = doi_utils.clean_doi(doi)
            doi_validated = doi_utils.validate_doi_format(doi)
            if not doi_validated:
                logger.warning(f"Invalid DOI format from CrossRef: {doi}")

        # Extract URL
        url = item.get("URL", "")

        # Extract type (article, journal, etc.)
        paper_type = item.get("type", "")

        # Abstract is not typically available in CrossRef basic API
        abstract = ""

        # Citation count is not available in CrossRef free API
        citation_count = None

        return {
            "title": title,
            "authors": authors,
            "year": year,
            "journal/venue": journal,
            "doi": doi,
            "doi_validated": doi_validated,
            "abstract": abstract,
            "citation_count": citation_count,
            "url": url,
            "type": paper_type,
            "source": "crossref",
        }

    def search_by_query(
        self,
        query: str,
        max_results: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        field: Optional[str] = None,
        issn: Optional[Union[str, List[str]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for papers by query string with optional filters.

        Args:
            query: The search query (keywords, phrases, etc.)
            max_results: Maximum number of results to return (1-100)
            year_from: Filter by publication year (inclusive)
            year_to: Filter by publication year (inclusive)
            field: Filter by field of study (e.g., "Medicine", "Engineering")
            issn: Filter by journal ISSN (single ISSN or list of ISSNs)

        Returns:
            List of paper metadata in standard format
        """
        # Build URL with filters
        encoded_query = query.replace(" ", "+").lower()
        url = f"{CROSSREF_API_URL}?query={encoded_query}&rows={max_results}"

        if year_from:
            url += f"&from-pub-date={year_from}"
        if year_to:
            url += f"&until-pub-date={year_to}"
        if field:
            url += f"&filter=type:{field}"

        # Add ISSN filter
        if issn:
            if isinstance(issn, str):
                # Single ISSN
                url += f"&filter=issn:{issn}"
                logger.info(f"Searching for: {query} (max_results={max_results}, issn={issn})")
                response = self._make_request(url)
                return self._parse_query_response(response)
            elif isinstance(issn, list) and len(issn) > 1:
                # Multiple ISSNs: batch search across all journals
                return self._search_by_issn_batch(query, issn, max_results,
                                                   year_from, year_to)
            elif isinstance(issn, list) and issn:
                # Single-item list
                url += f"&filter=issn:{issn[0]}"

        logger.info(f"Searching for: {query} (max_results={max_results})")
        response = self._make_request(url)
        return self._parse_query_response(response)

    def _search_by_issn_batch(
        self,
        query: str,
        issn_list: List[str],
        max_results: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        rows_per_issn: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search CrossRef across multiple ISSNs with batching.

        Queries each ISSN separately and merges results by DOI to cover
        all target journals instead of only the first ISSN.

        Args:
            query: Search query string
            issn_list: List of ISSNs to search
            max_results: Maximum total results to return
            year_from: Optional year filter start
            year_to: Optional year filter end
            rows_per_issn: Results to fetch per ISSN (default 5)

        Returns:
            Deduplicated list of paper metadata
        """
        all_results = []
        seen_dois = set()

        for issn in issn_list:
            encoded_query = query.replace(" ", "+").lower()
            batch_url = (
                f"{CROSSREF_API_URL}?query={encoded_query}"
                f"&rows={rows_per_issn}&filter=issn:{issn}"
            )
            if year_from:
                batch_url += f"&from-pub-date={year_from}"
            if year_to:
                batch_url += f"&until-pub-date={year_to}"

            try:
                response = self._make_request(batch_url)
                batch = self._parse_query_response(response)
                for paper in batch:
                    doi = paper.get("doi", "")
                    if doi and doi not in seen_dois:
                        seen_dois.add(doi)
                        all_results.append(paper)
                    elif not doi:
                        all_results.append(paper)
            except Exception as e:
                logger.warning(f"CrossRef ISSN batch failed for {issn}: {e}")

            if len(all_results) >= max_results:
                break

        logger.info(
            f"ISSN batch: {len(all_results)} results from "
            f"{min(len(issn_list), len(all_results) // max(rows_per_issn, 1) + 1)}/{len(issn_list)} ISSNs"
        )
        return all_results[:max_results]

