"""
OpenAlex API client for academic literature search.

OpenAlex is a free, open catalog of the global research system with 250M+ works.
Key advantages over CrossRef: provides abstracts, supports ISSN batch filtering
in a single API call, and has concept-based search.

API docs: https://docs.openalex.org/
"""

import logging
from typing import Any, Dict, List, Optional

from .api_base import BaseAPIClient
from .config import (
    CROSSREF_POLITE_MAILTO,
    OPENALEX_API_URL,
    OPENALEX_MAILTO,
    OPENALEX_MAX_PER_PAGE,
    OPENALEX_RATE_LIMIT,
)
from .exceptions import APIError, NotFoundError

logger = logging.getLogger(__name__)


class OpenAlexClient(BaseAPIClient):
    """Client for the OpenAlex API (250M+ works, free, with abstracts)."""

    def __init__(
        self,
        rate_limit: float = OPENALEX_RATE_LIMIT,
        mailto: Optional[str] = None,
    ):
        self.mailto = mailto or OPENALEX_MAILTO
        super().__init__(rate_limit=rate_limit)

    # ------------------------------------------------------------------
    # BaseAPIClient abstract methods
    # ------------------------------------------------------------------

    def _get_user_agent(self) -> str:
        return f"LitSearch/2.0-OpenAlex (mailto:{self.mailto})"

    def _build_doi_url(self, doi: str) -> str:
        return f"{OPENALEX_API_URL}/doi:{doi}"

    def _build_query_url(self, query: str, max_results: int = 10) -> str:
        per_page = min(max_results, OPENALEX_MAX_PER_PAGE)
        url = f"{OPENALEX_API_URL}?search={query}&per_page={per_page}"
        if self.mailto:
            url += f"&mailto={self.mailto}"
        return url

    def _parse_doi_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        return self._extract_paper_metadata(response)

    def _parse_query_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = response.get("results", [])
        if not results:
            return []
        return [self._extract_paper_metadata(w) for w in results]

    # ------------------------------------------------------------------
    # OpenAlex-specific methods
    # ------------------------------------------------------------------

    def search_by_issn_batch(
        self,
        query: str,
        issn_list: List[str],
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search across multiple ISSNs in a single API call.

        OpenAlex supports pipe-separated ISSNs:
            filter=primary_location.source.issn:ISSN1|ISSN2|ISSN3

        This is significantly faster than CrossRef's per-ISSN approach.
        """
        if not issn_list:
            return self.search_by_query(query, max_results=max_results)

        per_page = min(max_results, OPENALEX_MAX_PER_PAGE)

        # Build pipe-separated ISSN filter
        # OpenAlex ISSN format: "XXXX-XXXX"
        formatted_issns = []
        for issn in issn_list:
            issn_clean = issn.strip().replace("-", "")
            if len(issn_clean) == 8:
                formatted_issns.append(f"{issn_clean[:4]}-{issn_clean[4:]}")

        if not formatted_issns:
            return []

        # Batch ISSNs in groups of 50 to avoid URL length issues
        all_results = []
        batch_size = 50

        for i in range(0, len(formatted_issns), batch_size):
            batch = formatted_issns[i:i + batch_size]
            issn_filter = "|".join(batch)

            url = (
                f"{OPENALEX_API_URL}?"
                f"search={query}&"
                f"filter=primary_location.source.issn:{issn_filter}&"
                f"per_page={per_page}"
            )
            if self.mailto:
                url += f"&mailto={self.mailto}"

            try:
                self._check_rate_limit()
                response = self.session.get(
                    url,
                    timeout=(10, 30),
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                all_results.extend(
                    [self._extract_paper_metadata(w) for w in results]
                )
            except Exception as e:
                logger.warning(f"OpenAlex ISSN batch search failed: {e}")
                continue

        return all_results[:max_results]

    def search_by_concepts(
        self,
        query: str,
        concept_ids: List[str],
        max_results: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search by OpenAlex concept IDs for concept-based retrieval.

        Args:
            query: Search keywords
            concept_ids: OpenAlex concept IDs (e.g., ["C121332964"])
            max_results: Max results to return
        """
        per_page = min(max_results, OPENALEX_MAX_PER_PAGE)
        concept_filter = "|".join(concept_ids)

        url = (
            f"{OPENALEX_API_URL}?"
            f"search={query}&"
            f"filter=concepts.id:{concept_filter}&"
            f"per_page={per_page}"
        )
        if self.mailto:
            url += f"&mailto={self.mailto}"

        try:
            self._check_rate_limit()
            response = self.session.get(url, timeout=(10, 30))
            response.raise_for_status()
            data = response.json()
            return [self._extract_paper_metadata(w) for w in data.get("results", [])]
        except Exception as e:
            logger.warning(f"OpenAlex concept search failed: {e}")
            return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_paper_metadata(self, work: Dict[str, Any]) -> Dict[str, Any]:
        """Extract standard-format metadata from an OpenAlex work object."""
        # Title
        title = work.get("title", "") or work.get("display_name", "") or ""

        # Authors — from authorships array
        authors = []
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            name = author.get("display_name", "")
            if name:
                authors.append(name)

        # Year
        year = work.get("publication_year")

        # Journal — from primary_location
        journal = ""
        primary_loc = work.get("primary_location") or {}
        source = primary_loc.get("source") or {}
        journal = source.get("display_name", "") or ""

        # DOI
        doi = work.get("doi", "")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")

        # Abstract — reconstructed from inverted index
        abstract_index = work.get("abstract_inverted_index")
        abstract = self._reconstruct_abstract(abstract_index) if abstract_index else None

        # Citation count
        citation_count = work.get("cited_by_count")

        # Open access
        oa_status = work.get("open_access", {})
        is_oa = oa_status.get("is_oa", False) if isinstance(oa_status, dict) else False
        best_oa_url = (
            oa_status.get("oa_url") if isinstance(oa_status, dict) else None
        )

        # URL
        url = best_oa_url or work.get("id", "")

        return {
            "title": title.strip(),
            "authors": authors,
            "year": year,
            "journal": journal,
            "doi": doi or None,
            "abstract": abstract,
            "keywords": [],
            "source": "openalex",
            "citation_count": citation_count,
            "url": url,
            "doi_validated": bool(doi),
            "open_access": is_oa,
        }

    @staticmethod
    def _reconstruct_abstract(
        inverted_index: Dict[str, List[int]],
    ) -> str:
        """Reconstruct abstract from OpenAlex inverted index format.

        OpenAlex stores abstracts as {word: [position1, position2, ...]}.
        We sort by position and join to recover the original text.
        """
        if not inverted_index:
            return ""

        # Build position → word mapping
        position_word = {}
        for word, positions in inverted_index.items():
            for pos in positions:
                position_word[pos] = word

        # Sort by position and join
        sorted_words = [
            position_word[k]
            for k in sorted(position_word.keys())
        ]
        return " ".join(sorted_words)
