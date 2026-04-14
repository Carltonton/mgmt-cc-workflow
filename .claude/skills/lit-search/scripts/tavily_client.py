"""
Tavily API Client - Google Scholar Replacement

This module provides a simple wrapper for the Tavily Search API,
used as a replacement when users explicitly request "Google Scholar".

Tavily provides web search with academic content coverage and has
a formal API (unlike Google Scholar which requires scraping).
"""

import logging
import os
from typing import List, Dict, Any, Optional, Union

from . import doi_utils

# Configure logging
logger = logging.getLogger(__name__)


class TavilySearchClient:
    """
    Tavily API client as Google Scholar replacement.

    This client wraps the official Tavily Python SDK to provide
    academic literature search functionality when users explicitly
    request Google Scholar.

    Usage:
        client = TavilySearchClient()
        results = client.search("board fault lines corporate governance", max_results=10)
    """

    # Google Scholar trigger keywords
    GOOGLE_SCHOLAR_KEYWORDS = ["google scholar", "scholar.google"]

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Tavily client.

        Args:
            api_key: Tavily API key. If not provided, reads from TAVILY_API_KEY env var.

        Raises:
            ValueError: If no API key is available.
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "TAVILY_API_KEY required. Get one at https://tavily.com "
                "and set as environment variable."
            )

        # Lazy import - only import TavilyClient if this class is used
        try:
            from tavily import TavilyClient as OfficialTavilyClient
            self.client = OfficialTavilyClient(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "tavily-python package not installed. "
                "Install with: pip install tavily-python"
            )

    def clean_query(self, query: str) -> str:
        """
        Remove Google Scholar references from the query.

        Args:
            query: The original search query

        Returns:
            Cleaned query without Google Scholar references
        """
        clean = query
        for keyword in self.GOOGLE_SCHOLAR_KEYWORDS:
            clean = clean.replace(keyword, "")
        # Clean up extra whitespace
        clean = " ".join(clean.split())
        return clean

    def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced",
        journal_domains: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for academic content using Tavily API.

        Args:
            query: Search query (may include "Google Scholar" which will be cleaned)
            max_results: Maximum number of results to return (1-100)
            search_depth: "basic" or "advanced" (advanced for better academic results)
            journal_domains: List of journal domains to filter (e.g., ['journals.aom.org', 'apa.org'])

        Returns:
            List of search results in standard format:
            [
                {
                    "title": "Paper Title",
                    "url": "https://...",
                    "content": "Abstract/content snippet",
                    "score": 0.95,
                    "source": "tavily"
                },
                ...
            ]
        """
        # Clean the query
        clean_query = self.clean_query(query)

        if not clean_query:
            logger.warning("Query is empty after cleaning Google Scholar references")
            return []

        # Clamp max_results
        max_results = max(1, min(100, max_results))

        # Build API kwargs
        api_kwargs = {
            "query": clean_query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": False,
            "include_raw_content": False,
            "include_images": False,
        }

        # Use native include_domains instead of site: operator hack
        if journal_domains:
            api_kwargs["include_domains"] = journal_domains[:20]

        try:
            logger.info(f"Searching Tavily for: {clean_query}"
                        + (f" (domains: {journal_domains[:5]})" if journal_domains else ""))

            response = self.client.search(**api_kwargs)

            # Convert to standard format
            results = []
            for item in response.get("results", []):
                # Extract DOI from URL and content
                url = item.get("url", "")
                content = item.get("content", "")
                title = item.get("title", "")

                # Try to extract DOI from URL first
                doi = doi_utils.extract_doi_from_url(url)
                doi_validated = False

                # If not found in URL, try content
                if not doi and content:
                    doi = doi_utils.extract_doi_from_text(content)

                # If still not found, try title (some titles contain DOI)
                if not doi and title:
                    doi = doi_utils.extract_doi_from_text(title)

                # Validate DOI format if found
                if doi:
                    doi = doi_utils.clean_doi(doi)
                    doi_validated = doi_utils.validate_doi_format(doi)
                    if doi_validated:
                        logger.info(f"Extracted DOI from Tavily result: {doi}")
                    else:
                        logger.warning(f"Invalid DOI format extracted: {doi}")
                        doi = ""  # Clear invalid DOI

                results.append({
                    "title": title,
                    "url": url,
                    "content": content,
                    "doi": doi,
                    "doi_validated": doi_validated,
                    "score": item.get("score", 0),
                    "source": "tavily"
                })

            logger.info(f"Tavily returned {len(results)} results with {sum(1 for r in results if r.get('doi'))} DOIs")
            return results

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []

    def is_google_scholar_request(self, query: str) -> bool:
        """
        Check if the query explicitly requests Google Scholar.

        Args:
            query: The search query

        Returns:
            True if Google Scholar is mentioned, False otherwise
        """
        query_lower = query.lower()
        return any(keyword.lower() in query_lower for keyword in self.GOOGLE_SCHOLAR_KEYWORDS)

    # Academic publisher domains for include_domains filtering
    ACADEMIC_DOMAINS = [
        # Major publishers
        "journals.sagepub.com",
        "journals.aom.org",          # Academy of Management
        "pubsonline.informs.org",    # INFORMS (Management Science, Org Science)
        "onlinelibrary.wiley.com",   # Wiley
        "link.springer.com",        # Springer
        "www.sciencedirect.com",    # Elsevier
        "www.tandfonline.com",      # Taylor & Francis
        "www.emerald.com",          # Emerald
        "psycnet.apa.org",          # APA (JAP, Psych Bulletin)
        "academic.oup.com",         # Oxford UP
        "www.cambridge.org",        # Cambridge UP
        "pubmed.ncbi.nlm.nih.gov",  # PubMed
        "scholar.google.com",       # Google Scholar (citation pages)
        "doi.org",                  # DOI resolver
        "researchgate.net",         # ResearchGate
        # Preprint / open repositories
        "arxiv.org",
        "ssrn.com",
        "osf.io",
    ]

    # Non-academic domains to exclude
    EXCLUDE_DOMAINS = [
        "twitter.com", "x.com",
        "facebook.com", "instagram.com", "linkedin.com",
        "youtube.com", "tiktok.com", "reddit.com",
        "amazon.com", "ebay.com", "walmart.com",
        "wikipedia.org",
        "pinterest.com", "quora.com",
        "medium.com", "substack.com",
        "yelp.com", "tripadvisor.com",
    ]

    def search_google_scholar(
        self,
        query: str,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for academic papers via Tavily, targeting publisher sites.

        Instead of restricting to scholar.google.com (which only returns
        author profile pages, not paper search results), this method uses
        include_domains with academic publisher domains to surface actual
        paper pages. Also excludes common non-academic sites.

        Args:
            query: Search query (Google Scholar keywords will be cleaned)
            max_results: Maximum number of results (1-20)

        Returns:
            List of search results in standard format (same as search()).

        Note:
            Results come from publisher sites, not Google Scholar directly.
            Use --source semantic-scholar as fallback for more metadata.
        """
        clean_query = self.clean_query(query)

        if not clean_query:
            logger.warning("Query is empty after cleaning Google Scholar references")
            return []

        max_results = max(1, min(50, max_results))

        try:
            logger.info(f"Searching academic papers (via Tavily) for: {clean_query}")

            response = self.client.search(
                query=clean_query,
                max_results=max_results,
                search_depth="advanced",
                include_domains=self.ACADEMIC_DOMAINS,
                exclude_domains=self.EXCLUDE_DOMAINS,
                include_answer=False,
                include_raw_content=False,
                include_images=False,
            )

            results = []
            for item in response.get("results", []):
                url = item.get("url", "")
                content = item.get("content", "")
                title = item.get("title", "")

                doi = doi_utils.extract_doi_from_url(url)
                doi_validated = False

                if not doi and content:
                    doi = doi_utils.extract_doi_from_text(content)
                if not doi and title:
                    doi = doi_utils.extract_doi_from_text(title)

                if doi:
                    doi = doi_utils.clean_doi(doi)
                    doi_validated = doi_utils.validate_doi_format(doi)
                    if not doi_validated:
                        doi = ""

                results.append({
                    "title": title,
                    "url": url,
                    "content": content,
                    "doi": doi,
                    "doi_validated": doi_validated,
                    "score": item.get("score", 0),
                    "source": "google_scholar",
                })

            logger.info(
                f"Academic search returned {len(results)} results "
                f"({sum(1 for r in results if r.get('doi'))} with DOI)"
            )
            return results

        except Exception as e:
            logger.error(f"Academic search failed: {e}")
            return []


def is_google_scholar_request(query: str) -> bool:
    """
    Convenience function to check if a query requests Google Scholar.

    Args:
        query: The search query

    Returns:
        True if Google Scholar is mentioned, False otherwise
    """
    client = TavilySearchClient.__new__(TavilySearchClient)
    return client.is_google_scholar_request(query)
