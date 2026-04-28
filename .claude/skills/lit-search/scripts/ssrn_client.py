"""
SSRN search client via Tavily.

SSRN (Social Science Research Network) provides management and business
working papers / preprints. There is no public search API, and the website
has aggressive bot detection. This client uses Tavily's web search
restricted to the ssrn.com domain.
"""

import logging
from typing import Any, Dict, List

from .tavily_client import TavilySearchClient

logger = logging.getLogger(__name__)


def search_ssrn(
    query: str,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Search SSRN via Tavily with domain restriction.

    SSRN does not have a public search API. This uses Tavily's web search
    restricted to ssrn.com domain.

    Args:
        query: Search query
        max_results: Max results to return

    Returns:
        List of paper metadata dicts with source="ssrn"
    """
    try:
        client = TavilySearchClient()
        # Use Tavily's search method with SSRN domain restriction
        results = client.search(
            query,
            max_results=max_results,
            journal_domains=["ssrn.com"],
        )

        # Mark source as SSRN for merge priority
        for r in results:
            r["source"] = "ssrn"
            r["journal"] = r.get("journal") or "SSRN Working Paper"

        return results
    except Exception as e:
        logger.warning(f"SSRN search failed: {e}")
        return []
