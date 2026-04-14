"""
Portable Bibliography API Client Module

Direct API integration with academic literature databases (CrossRef, Semantic Scholar, Tavily)
to replace MCP WebSearch for literature searches.

This is a self-contained module that can be copied to any project's .claude/ directory.

Usage:
    from scripts import CrossRefClient, SemanticScholarClient

    client = CrossRefClient()
    results = client.search_by_query("organizational behavior", max_results=5)
"""

__version__ = "0.2.0-portable"

from .exceptions import (
    APIError,
    RateLimitError,
    NotFoundError,
    ConfigurationError,
)

from .crossref_client import CrossRefClient
from .semantic_scholar_client import SemanticScholarClient
from .metadata_manager import MetadataManager

__all__ = [
    "CrossRefClient",
    "SemanticScholarClient",
    "MetadataManager",
    "APIError",
    "RateLimitError",
    "NotFoundError",
    "ConfigurationError",
]
