"""
Portable Bibliography API Client Module

Direct API integration with academic literature databases (CrossRef, Semantic Scholar,
OpenAlex, Tavily, SSRN, Unpaywall) to replace MCP WebSearch for literature searches.

This is a self-contained module that can be copied to any project's .claude/ directory.

Usage:
    from scripts import CrossRefClient, SemanticScholarClient, OpenAlexClient

    client = OpenAlexClient()
    results = client.search_by_query("organizational behavior", max_results=5)
"""

__version__ = "2.0.0"

from .exceptions import (
    APIError,
    RateLimitError,
    NotFoundError,
    ConfigurationError,
)

from .shared_types import Paper
from .crossref_client import CrossRefClient
from .semantic_scholar_client import SemanticScholarClient
from .openalex_client import OpenAlexClient
from .metadata_manager import MetadataManager

__all__ = [
    "Paper",
    "CrossRefClient",
    "SemanticScholarClient",
    "OpenAlexClient",
    "MetadataManager",
    "APIError",
    "RateLimitError",
    "NotFoundError",
    "ConfigurationError",
]
