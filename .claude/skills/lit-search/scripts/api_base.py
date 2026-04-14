"""
Base API client class for bibliography search services.

This module provides an abstract base class that defines the interface
for all literature search API clients. It includes common functionality
for rate limiting, retry logic, and error handling.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
import time

try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
    )
    import requests
except ImportError as e:
    raise ImportError(
        "Required dependencies not found. Please install: "
        "pip install requests tenacity"
    ) from e

from .config import (
    API_REQUEST_TIMEOUT,
    API_CONNECT_TIMEOUT,
    API_MAX_RETRIES,
    API_RETRY_INITIAL_DELAY,
    API_RETRY_BACKOFF_MULTIPLIER,
    API_RETRY_MAX_DELAY,
)
from .exceptions import (
    APIError,
    RateLimitError,
    NotFoundError,
    TimeoutError as BibTimeoutError,
    ValidationError,
)


# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """
    Abstract base class for literature search API clients.

    This class provides common functionality for all API clients including:
    - Rate limiting
    - Retry logic with exponential backoff
    - Error handling
    - Logging

    Subclasses must implement the search_by_doi() and search_by_query() methods.
    """

    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize the API client.

        Args:
            rate_limit: Minimum seconds between API calls (for rate limiting)
        """
        self.rate_limit = rate_limit
        self.last_call_time = 0.0
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self) -> None:
        """Set up the requests session with default headers and settings."""
        self.session.headers.update({
            "User-Agent": self._get_user_agent(),
            "Accept": "application/json",
        })

    @abstractmethod
    def _get_user_agent(self) -> str:
        """
        Get the User-Agent header for API requests.

        Returns:
            User-Agent string
        """
        pass

    @abstractmethod
    def _build_doi_url(self, doi: str) -> str:
        """
        Build the URL for a DOI lookup.

        Args:
            doi: The DOI to look up

        Returns:
            Full URL for the DOI lookup
        """
        pass

    @abstractmethod
    def _build_query_url(self, query: str, max_results: int = 10) -> str:
        """
        Build the URL for a query search.

        Args:
            query: The search query
            max_results: Maximum number of results to return

        Returns:
            Full URL for the search
        """
        pass

    @abstractmethod
    def _parse_doi_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the API response for a DOI lookup.

        Args:
            response: Raw API response as a dictionary

        Returns:
            Parsed paper metadata in standard format
        """
        pass

    @abstractmethod
    def _parse_query_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the API response for a query search.

        Args:
            response: Raw API response as a dictionary

        Returns:
            List of parsed paper metadata in standard format
        """
        pass

    def _check_rate_limit(self) -> None:
        """
        Check and enforce rate limiting.

        This method ensures that the minimum time between API calls
        (as specified by rate_limit) has elapsed.
        """
        elapsed = time.time() - self.last_call_time
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        self.last_call_time = time.time()

    def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP GET request with error handling and retry logic.

        Args:
            url: The URL to request
            params: Query parameters
            headers: Additional headers (merged with session headers)

        Returns:
            Parsed JSON response

        Raises:
            APIError: If the request fails after retries
            NotFoundError: If the resource is not found
            RateLimitError: If rate limit is exceeded
            BibTimeoutError: If the request times out
        """
        merged_headers = self.session.headers.copy()
        if headers:
            merged_headers.update(headers)

        try:
            self._check_rate_limit()

            logger.debug(f"Making request to: {url}")
            response = self.session.get(
                url,
                params=params,
                headers=merged_headers,
                timeout=(API_CONNECT_TIMEOUT, API_REQUEST_TIMEOUT),
            )

            # Handle specific HTTP status codes
            if response.status_code == 404:
                raise NotFoundError(
                    message="Resource not found",
                    resource_type="API endpoint",
                    identifier=url,
                )
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    message="API rate limit exceeded",
                    retry_after=int(retry_after) if retry_after else None,
                )
            elif response.status_code >= 500:
                raise APIError(
                    message=f"Server error: {response.status_code}",
                    status_code=response.status_code,
                    response_text=response.text,
                )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout as e:
            raise BibTimeoutError(
                message=f"Request timed out: {e}",
                timeout_seconds=API_REQUEST_TIMEOUT,
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise APIError(
                message=f"Connection error: {e}",
            ) from e
        except requests.exceptions.RequestException as e:
            raise APIError(
                message=f"Request failed: {e}",
            ) from e

    @retry(
        stop=stop_after_attempt(API_MAX_RETRIES),
        wait=wait_exponential(
            multiplier=API_RETRY_BACKOFF_MULTIPLIER,
            min=API_RETRY_INITIAL_DELAY,
            max=API_RETRY_MAX_DELAY,
        ),
        retry=retry_if_exception_type((APIError, BibTimeoutError)),
        reraise=True,
    )
    def search_by_doi(self, doi: str) -> Dict[str, Any]:
        """
        Fetch a paper by its DOI.

        Args:
            doi: The DOI to look up (e.g., "10.1287/mksc.2018.0886")

        Returns:
            Paper metadata in standard format:
            {
                "title": str,
                "authors": List[str],
                "year": int,
                "journal/venue": str,
                "doi": str,
                "abstract": str (optional),
                "citation_count": int (optional),
                "url": str (optional),
            }

        Raises:
            NotFoundError: If the DOI is not found
            APIError: If the API request fails
            ValidationError: If the DOI format is invalid
        """
        if not doi or not isinstance(doi, str):
            raise ValidationError(
                message="DOI must be a non-empty string",
                field="doi",
                value=str(doi),
            )

        # Clean DOI (remove URL prefix if present)
        clean_doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
        clean_doi = clean_doi.strip()

        if not clean_doi:
            raise ValidationError(
                message="DOI cannot be empty after cleaning",
                field="doi",
                value=doi,
            )

        url = self._build_doi_url(clean_doi)
        logger.info(f"Searching for DOI: {clean_doi}")

        response = self._make_request(url)
        return self._parse_doi_response(response)

    @retry(
        stop=stop_after_attempt(API_MAX_RETRIES),
        wait=wait_exponential(
            multiplier=API_RETRY_BACKOFF_MULTIPLIER,
            min=API_RETRY_INITIAL_DELAY,
            max=API_RETRY_MAX_DELAY,
        ),
        retry=retry_if_exception_type((APIError, BibTimeoutError)),
        reraise=True,
    )
    def search_by_query(
        self, query: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for papers by query string.

        Args:
            query: The search query (keywords, phrases, etc.)
            max_results: Maximum number of results to return (1-100)

        Returns:
            List of paper metadata in standard format

        Raises:
            APIError: If the API request fails
            ValidationError: If the query is invalid
        """
        if not query or not isinstance(query, str):
            raise ValidationError(
                message="Query must be a non-empty string",
                field="query",
                value=str(query),
            )

        if max_results < 1 or max_results > 100:
            raise ValidationError(
                message="max_results must be between 1 and 100",
                field="max_results",
                value=str(max_results),
            )

        url = self._build_query_url(query, max_results)
        logger.info(f"Searching for: {query} (max_results={max_results})")

        response = self._make_request(url)
        return self._parse_query_response(response)

    def to_bibtex(self, entry: Dict[str, Any]) -> str:
        """
        Convert a paper metadata entry to BibTeX format.

        Handles entry type detection (article, book, inproceedings).

        Args:
            entry: Paper metadata in standard format

        Returns:
            BibTeX formatted string
        """
        cite_key = self._generate_cite_key(entry)

        authors = " and ".join(entry.get("authors", []))
        year = entry.get("year", "n.d.")
        title = entry.get("title", "")
        journal = entry.get("journal/venue", "")
        doi = entry.get("doi", "")
        url = entry.get("url", "")

        # Determine entry type
        paper_type = entry.get("type", "article")
        if paper_type == "book-chapter":
            bibtex_type = "inproceedings"
        elif paper_type == "book":
            bibtex_type = "book"
        else:
            bibtex_type = "article"

        bibtex = f"@{bibtex_type}{{{cite_key},\n"
        bibtex += f"  author = {{{authors}}},\n"
        bibtex += f"  title = {{{title}}},\n"
        bibtex += f"  year = {{{year}}},\n"

        if journal:
            bibtex += f"  journal = {{{journal}}},\n"

        if doi:
            bibtex += f"  doi = {{{doi}}},\n"

        if url:
            bibtex += f"  url = {{{url}}},\n"

        bibtex += "}"

        return bibtex

    def _generate_cite_key(self, entry: Dict[str, Any]) -> str:
        """
        Generate a BibTeX citation key from paper metadata.

        Args:
            entry: Paper metadata in standard format

        Returns:
            Citation key in format: firstauthor_keyword_year
        """
        authors = entry.get("authors", [])
        if authors:
            first_author = authors[0].split()[-1].lower()  # Last name of first author
        else:
            first_author = "unknown"

        # Extract keyword from title (first meaningful word)
        title = entry.get("title", "")
        if title:
            words = title.lower().split()
            # Filter out common words
            stopwords = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "with"}
            keywords = [w for w in words if w.isalpha() and w not in stopwords]
            keyword = keywords[0] if keywords else "paper"
        else:
            keyword = "paper"

        year = entry.get("year", "n.d.")

        return f"{first_author}_{keyword}_{year}"

    def close(self) -> None:
        """Close the requests session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
