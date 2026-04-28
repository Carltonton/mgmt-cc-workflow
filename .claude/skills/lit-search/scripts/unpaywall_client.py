"""
Unpaywall API client for open access metadata enrichment.

Unpaywall is not a search engine — it is a DOI-based lookup service that
returns open access status, best OA URL, and publisher information.

Free, 100K requests/day with email parameter.

API docs: https://unpaywall.org/products/api
"""

import logging
import time
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError as e:
    raise ImportError(
        "Required dependency not found. Install: pip install requests"
    ) from e

from .config import (
    CROSSREF_POLITE_MAILTO,
    UNPAYWALL_API_URL,
    UNPAYWALL_EMAIL,
    UNPAYWALL_RATE_LIMIT,
)

logger = logging.getLogger(__name__)


class UnpaywallClient:
    """Unpaywall API client for open access metadata enrichment.

    Standalone (not a BaseAPIClient subclass) because Unpaywall has
    no search endpoint — only DOI-based lookup.
    """

    def __init__(self, email: Optional[str] = None):
        self.email = email or UNPAYWALL_EMAIL
        self.rate_limit = UNPAYWALL_RATE_LIMIT
        self.last_call_time = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"LitSearch/2.0-Unpaywall (mailto:{self.email})",
            "Accept": "application/json",
        })

    def lookup_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """Look up a DOI and return OA metadata.

        Args:
            doi: The DOI to look up

        Returns:
            Dict with oa_status, best_oa_url, is_oa, etc. or None on failure.
        """
        if not doi:
            return None

        # Clean DOI
        clean_doi = doi.replace("https://doi.org/", "").strip()

        url = f"{UNPAYWALL_API_URL}/{clean_doi}?email={self.email}"

        try:
            self._check_rate_limit()
            response = self.session.get(url, timeout=(10, 30))
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Unpaywall lookup failed for {clean_doi}: {e}")
            return None

    def enrich_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Add OA status and best OA URL to a paper dict.

        Args:
            paper: Paper metadata dict (must have 'doi' field)

        Returns:
            Updated paper dict with open_access and oa_url fields added.
        """
        doi = paper.get("doi")
        if not doi:
            return paper

        result = self.lookup_doi(doi)
        if not result:
            return paper

        paper = dict(paper)  # Copy to avoid mutating input
        paper["open_access"] = result.get("is_oa", False)

        best_oa = result.get("best_oa_location") or {}
        oa_url = (
            best_oa.get("url_for_pdf")
            or best_oa.get("url")
            or None
        )
        if oa_url:
            paper["oa_url"] = oa_url

        oa_status = result.get("oa_status")
        if oa_status:
            paper["oa_status"] = oa_status

        return paper

    def batch_enrich(
        self,
        papers: List[Dict[str, Any]],
        max_batch: int = 50,
    ) -> List[Dict[str, Any]]:
        """Enrich a batch of papers with OA metadata.

        Args:
            papers: List of paper dicts (should have 'doi' fields)
            max_batch: Max papers to enrich (rate limit protection)

        Returns:
            List of enriched paper dicts.
        """
        papers_with_doi = [p for p in papers if p.get("doi")]
        to_enrich = papers_with_doi[:max_batch]

        enriched = 0
        for paper in to_enrich:
            enriched_paper = self.enrich_paper(paper)
            if enriched_paper.get("open_access"):
                enriched += 1
                # Update the original list entry
                idx = papers.index(paper)
                papers[idx] = enriched_paper

        logger.info(
            f"Unpaywall: enriched {enriched}/{len(to_enrich)} papers with OA info"
        )
        return papers

    def _check_rate_limit(self) -> None:
        elapsed = time.time() - self.last_call_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_call_time = time.time()

    def close(self) -> None:
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
