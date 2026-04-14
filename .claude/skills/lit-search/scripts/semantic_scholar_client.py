"""
Semantic Scholar API client for academic bibliography search.

This module implements the Semantic Scholar API client, which provides access to
200M+ papers with rich metadata including citation counts and abstracts.

API Documentation: https://api.semanticscholar.org/
"""

import logging
from typing import List, Dict, Any, Optional, Union
import urllib.parse

from .api_base import BaseAPIClient
from .config import (
    SEMANTIC_SCHOLAR_API_KEY,
    SEMANTIC_SCHOLAR_PAPER_URL,
    SEMANTIC_SCHOLAR_SEARCH_URL,
    SEMANTIC_SCHOLAR_FIELDS,
)
from .exceptions import NotFoundError, APIError, RateLimitError
from . import doi_utils


# Configure logging
logger = logging.getLogger(__name__)


class SemanticScholarClient(BaseAPIClient):
    """
    Client for the Semantic Scholar API.

    Semantic Scholar provides free access to 200M+ papers with rich metadata
    including citation counts, abstracts, and influential citation counts.

    An optional API key can be used for higher rate limits.

    Example:
        >>> from scripts.python.bibliography import SemanticScholarClient
        >>> client = SemanticScholarClient()
        >>> paper = client.search_by_doi("10.1287/mksc.2018.0886")
        >>> print(paper['title'])
        >>> results = client.search_by_query("machine learning", max_results=5)
        >>> for paper in results:
        ...     print(f"{paper['title']} ({paper['year']}) - Citations: {paper['citation_count']}")
    """

    # Semantic Scholar has higher rate limits
    DEFAULT_RATE_LIMIT = 0.05  # ~20 requests/second on free tier

    def __init__(self, rate_limit: Optional[float] = None, api_key: Optional[str] = None):
        """
        Initialize the Semantic Scholar client.

        Args:
            rate_limit: Minimum seconds between API calls (default: 0.05)
                       If api_key is provided, can be set to 0.01 for higher limits
            api_key: Optional Semantic Scholar API key for higher rate limits
        """
        if rate_limit is None:
            # Use configured rate limit
            if SEMANTIC_SCHOLAR_API_KEY or api_key:
                rate_limit = 0.01  # ~100 requests/second with key
            else:
                rate_limit = self.DEFAULT_RATE_LIMIT

        super().__init__(rate_limit=rate_limit)

        self.api_key = api_key or SEMANTIC_SCHOLAR_API_KEY
        if self.api_key:
            self.session.headers.update({"x-api-key": self.api_key})

        logger.info(f"Semantic Scholar client initialized (rate_limit={rate_limit}s)")

    def _make_request(self, url, params=None, headers=None):
        """
        Override to fail fast on 429 rate limits.

        Semantic Scholar free tier: 20 req/5 min.
        On 429, raises RateLimitError immediately so callers can handle it
        without blocking the session. Use s2_enrich.py for background enrichment.
        """
        try:
            return super()._make_request(url, params, headers)
        except RateLimitError:
            logger.warning("S2 rate limited. Skipping Semantic Scholar for this request.")
            raise

    def _get_user_agent(self) -> str:
        """Get the User-Agent header for Semantic Scholar API requests."""
        return "BibliographySearch/0.1.0"

    def _build_doi_url(self, doi: str) -> str:
        """
        Build the URL for a DOI lookup.

        Semantic Scholar uses the DOI in the URL path.

        Args:
            doi: The DOI to look up

        Returns:
            Full URL for the DOI lookup
        """
        # Clean DOI (remove URL prefix if present)
        clean_doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
        clean_doi = clean_doi.strip()

        # Semantic Scholar uses DOI: prefix in URL
        return f"{SEMANTIC_SCHOLAR_PAPER_URL}/DOI:{clean_doi}"

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
        encoded_query = urllib.parse.quote(query)

        # Build URL with parameters
        url = (
            f"{SEMANTIC_SCHOLAR_SEARCH_URL}"
            f"?query={encoded_query}"
            f"&limit={max_results}"
            f"&fields={SEMANTIC_SCHOLAR_FIELDS}"
        )
        return url

    def _parse_doi_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the Semantic Scholar API response for a DOI lookup.

        Args:
            response: Raw Semantic Scholar API response as a dictionary

        Returns:
            Parsed paper metadata in standard format

        Raises:
            NotFoundError: If the DOI is not found
        """
        # Semantic Scholar returns data directly
        if not response or "title" not in response:
            raise NotFoundError(
                message="DOI not found or has no metadata",
                resource_type="DOI",
            )

        return self._extract_paper_metadata(response)

    def _parse_query_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the Semantic Scholar API response for a query search.

        Args:
            response: Raw Semantic Scholar API response as a dictionary

        Returns:
            List of parsed paper metadata in standard format
        """
        # Semantic Scholar returns data in 'data' field
        items = response.get("data", [])

        results = []
        for item in items:
            try:
                metadata = self._extract_paper_metadata(item)
                results.append(metadata)
            except Exception as e:
                # Log but continue parsing other items
                logger.warning(f"Failed to parse item: {e}")

        logger.info(f"Parsed {len(results)} papers from Semantic Scholar")
        return results

    def _extract_paper_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract paper metadata from a Semantic Scholar API item.

        Args:
            item: A single item from the Semantic Scholar API response

        Returns:
            Paper metadata in standard format
        """
        # Extract title
        title = item.get("title", "")

        # Extract authors
        authors = []
        if "authors" in item:
            for author in item["authors"]:
                if "name" in author:
                    authors.append(author["name"])

        # Extract year
        year = None
        if "year" in item:
            year = item["year"]
        elif "publicationDate" in item:
            # Try to extract year from publication date
            pub_date = item["publicationDate"]
            if pub_date:
                year = int(pub_date.split("-")[0])

        # Extract venue (journal/conference)
        venue = item.get("venue", "")

        # Extract DOI
        doi = ""
        doi_validated = False
        if "externalIds" in item:
            doi = item["externalIds"].get("DOI", "")
            # Clean and validate DOI format
            if doi:
                doi = doi_utils.clean_doi(doi)
                doi_validated = doi_utils.validate_doi_format(doi)
                if not doi_validated:
                    logger.warning(f"Invalid DOI format from Semantic Scholar: {doi}")

        # Extract URL
        url = item.get("url", "")

        # Extract abstract
        abstract = item.get("abstract", "")

        # Extract citation count
        citation_count = item.get("citationCount", 0)

        # Extract influential citation count (if available)
        influential_citation_count = item.get("influentialCitationCount")

        return {
            "title": title,
            "authors": authors,
            "year": year,
            "journal/venue": venue,
            "doi": doi,
            "doi_validated": doi_validated,
            "abstract": abstract,
            "citation_count": citation_count,
            "influential_citation_count": influential_citation_count,
            "url": url,
            "source": "semantic_scholar",
        }

    def search_by_query(
        self,
        query: str,
        max_results: int = 10,
        year_from: Optional[str] = None,
        year_to: Optional[str] = None,
        venue: Optional[str] = None,
        journal_names: Optional[List[str]] = None,
        fields_of_study: Optional[List[str]] = None,
        open_access_pdf: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search for papers by query string with optional filters.

        Args:
            query: The search query (keywords, phrases, etc.)
            max_results: Maximum number of results to return (1-100)
            year_from: Filter by publication year (inclusive, e.g., "2018")
            year_to: Filter by publication year (inclusive, e.g., "2023")
            venue: Filter by venue (journal/conference name)
            journal_names: Filter by list of journal/venue names (uses first if multiple provided)
            fields_of_study: Filter by fields of study (e.g., ["Computer Science", "Medicine"])
            open_access_pdf: Only return papers with open access PDFs

        Returns:
            List of paper metadata in standard format

        Note:
            Semantic Scholar API only supports a single venue filter per request.
            When journal_names is provided with multiple journals, only the first
            journal in the list will be used for filtering.
        """
        # Build URL with filters
        encoded_query = urllib.parse.quote(query)
        url = (
            f"{SEMANTIC_SCHOLAR_SEARCH_URL}"
            f"?query={encoded_query}"
            f"&limit={max_results}"
            f"&fields={SEMANTIC_SCHOLAR_FIELDS}"
        )

        if year_from:
            url += f"&year={year_from}-"
        if year_to:
            if year_from:
                # Combine year range
                url = url.replace(f"&year={year_from}-", f"&year={year_from}-{year_to}")
            else:
                url += f"&year=-{year_to}"

        # Handle venue/journal filtering
        if journal_names:
            if isinstance(journal_names, list) and len(journal_names) > 1:
                # Multiple journals: skip venue filter for broader results
                # ABS filtering happens at screening time (SKILL.md Step 3)
                logger.info(
                    f"Multiple journals ({len(journal_names)}), "
                    f"skipping S2 venue filter for broader coverage"
                )
            else:
                venue_to_use = journal_names[0] if isinstance(journal_names, list) else journal_names
                url += f"&venue={urllib.parse.quote(venue_to_use)}"
        elif venue:
            url += f"&venue={urllib.parse.quote(venue)}"

        if fields_of_study:
            for fos in fields_of_study:
                url += f"&fieldsOfStudy={urllib.parse.quote(fos)}"
        if open_access_pdf:
            url += "&openAccessPdf"

        logger.info(f"Searching for: {query} (max_results={max_results})")
        response = self._make_request(url)
        return self._parse_query_response(response)

    def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a paper by its Semantic Scholar ID.

        Args:
            paper_id: The Semantic Scholar paper ID (e.g., "COR:123456789")

        Returns:
            Paper metadata in standard format
        """
        url = f"{SEMANTIC_SCHOLAR_PAPER_URL}/{paper_id}"
        url += f"?fields={SEMANTIC_SCHOLAR_FIELDS}"

        response = self._make_request(url)
        return self._parse_doi_response(response)

    def get_references(
        self, paper_id: str, max_results: int = 500, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all papers cited by a given paper (its references/bibliography).

        Args:
            paper_id: Semantic Scholar paper ID or DOI (format: "DOI:10.xxx/yyy")
            max_results: Maximum references to return (default 500, max 1000)
            offset: Pagination offset

        Returns:
            List of referenced paper metadata in standard format
        """
        url = f"{SEMANTIC_SCHOLAR_PAPER_URL}/{paper_id}/references"
        params = {
            "fields": "paperId,title,authors,year,venue,externalIds,url",
            "limit": min(max_results, 1000),
            "offset": offset,
        }
        response = self._make_request(url, params=params)
        return self._parse_references_response(response)

    def _parse_references_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the Semantic Scholar references endpoint response.

        S2 format: {"data": [{"citingPaperId": ..., "citedPaper": {...}}]}

        Args:
            response: Raw API response

        Returns:
            List of referenced paper metadata
        """
        items = response.get("data") or []
        results = []

        for item in items:
            cited_paper = item.get("citedPaper") or {}
            if not cited_paper or not cited_paper.get("title"):
                continue
            try:
                metadata = self._extract_paper_metadata(cited_paper)
                results.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to parse reference: {e}")

        logger.info(f"Parsed {len(results)} references from Semantic Scholar")
        return results

