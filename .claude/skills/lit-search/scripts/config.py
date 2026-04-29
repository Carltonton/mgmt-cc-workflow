"""
Portable Configuration module for bibliography API clients.

This module centralizes all configuration settings for the bibliography search system.
Designed to be self-contained and portable across projects.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
# Try to load .env from project root
_env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


# =============================================================================
# Portable Paths
# =============================================================================

def get_hook_dir() -> Path:
    """
    Get the .claude directory location.

    Since this module is in .claude/skills/lit-search/scripts/, parent is .claude/skills/lit-search/

    Returns:
        Path to the .claude directory
    """
    return Path(__file__).parent.parent


def get_project_dir() -> Path:
    """
    Get the project directory (parent of .claude/).

    Returns:
        Path to the project root
    """
    return get_hook_dir().parent


HOOK_DIR: Path = get_hook_dir()
PROJECT_DIR: Path = get_project_dir()
# Put temp directory inside scripts module for true portability
TEMP_DIR: Path = Path(__file__).parent / "temp"
SEARCH_RESULTS_PATH: Path = TEMP_DIR / "search_results.md"

# Optional: Auto-detect bibliography file
BIBLIOGRAPHY_PATH: Optional[Path] = None
_possible_bib_paths = [
    PROJECT_DIR / "Bibliography_base.bib",
    PROJECT_DIR / "references.bib",
    PROJECT_DIR / "bibliography.bib",
    PROJECT_DIR / "refs.bib",
]
for path in _possible_bib_paths:
    if path.exists():
        BIBLIOGRAPHY_PATH = path
        break


# =============================================================================
# API Configuration
# =============================================================================

# CrossRef API
CROSSREF_API_URL: str = "https://api.crossref.org/works"
CROSSREF_POLITE_MAILTO: str = os.environ.get(
    "CROSSREF_EMAIL",
    "bibliography-search@example.com"  # Generic placeholder - users can override
)
CROSSREF_USER_AGENT: str = f"BibliographySearch/0.2.0-portable (mailto:{CROSSREF_POLITE_MAILTO})"

# Semantic Scholar API
SEMANTIC_SCHOLAR_API_URL: str = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_API_KEY: Optional[str] = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
SEMANTIC_SCHOLAR_PAPER_URL: str = f"{SEMANTIC_SCHOLAR_API_URL}/paper"
SEMANTIC_SCHOLAR_SEARCH_URL: str = f"{SEMANTIC_SCHOLAR_API_URL}/paper/search"

# Tavily API (Google Scholar replacement)
TAVILY_API_KEY: Optional[str] = os.environ.get("TAVILY_API_KEY")

# Web of Science (Future - requires institutional access)
WOS_API_URL: str = "https://api.clarivate.com/api/wos"
WOS_API_KEY: Optional[str] = os.environ.get("WOS_API_KEY")

# OpenAlex API (250M+ works, free, with abstracts)
OPENALEX_API_URL: str = "https://api.openalex.org/works"
OPENALEX_MAILTO: str = os.environ.get(
    "OPENALEX_EMAIL",
    CROSSREF_POLITE_MAILTO,
)
OPENALEX_RATE_LIMIT: float = 0.1  # 10 req/sec in polite pool
OPENALEX_MAX_PER_PAGE: int = 200

# Unpaywall API (OA metadata by DOI)
UNPAYWALL_API_URL: str = "https://api.unpaywall.org/v2"
UNPAYWALL_EMAIL: str = os.environ.get(
    "UNPAYWALL_EMAIL",
    CROSSREF_POLITE_MAILTO,
)
UNPAYWALL_RATE_LIMIT: float = 1.0  # Conservative: 1 req/sec

# Query expansion
QUERY_EXPANSION_ENABLED: bool = os.environ.get(
    "LIT_SEARCH_EXPAND_QUERIES", "false"
).lower() == "true"
DEFAULT_DOMAIN: str = "management"


# =============================================================================
# Rate Limiting Configuration
# =============================================================================

# CrossRef: Polite rate limit (no key required)
CROSSREF_RATE_LIMIT: float = 1.0  # seconds between requests
CROSSREF_BURST_SIZE: int = 1  # max concurrent requests

# Semantic Scholar: Free tier limits
SEMANTIC_SCHOLAR_RATE_LIMIT: float = 0.05  # ~20 requests/second (free tier)
SEMANTIC_SCHOLAR_RATE_LIMIT_WITH_KEY: float = 0.01  # ~100 requests/second (with key)

# Semantic Scholar rate limit cooldown (seconds)
# Free tier: 20 req/5min — set to 300 for full window reset
S2_RATE_LIMIT_COOLDOWN: int = int(
    os.environ.get("S2_RATE_LIMIT_COOLDOWN", "300")
)
# Adjust rate limit based on API key
if SEMANTIC_SCHOLAR_API_KEY:
    SEMANTIC_SCHOLAR_RATE_LIMIT = SEMANTIC_SCHOLAR_RATE_LIMIT_WITH_KEY


# =============================================================================
# Retry Configuration
# =============================================================================

API_MAX_RETRIES: int = 3
API_RETRY_BACKOFF_MULTIPLIER: int = 2
API_RETRY_INITIAL_DELAY: float = 1.0  # seconds
API_RETRY_MAX_DELAY: float = 30.0  # seconds


# =============================================================================
# Request Timeout Configuration
# =============================================================================

API_REQUEST_TIMEOUT: int = 30  # seconds
API_CONNECT_TIMEOUT: int = 10  # seconds


# =============================================================================
# Search Defaults
# =============================================================================

DEFAULT_MAX_RESULTS: int = 50
MIN_MAX_RESULTS: int = 1
MAX_MAX_RESULTS: int = 100

# Fields to fetch from Semantic Scholar
SEMANTIC_SCHOLAR_FIELDS: str = (
    "title,authors,year,venue,citationCount,abstract,externalIds,url,publicationDate"
)


# =============================================================================
# DOI Validation Configuration
# =============================================================================

# Multi-source merge priority (OpenAlex first for richest metadata)
MERGE_SOURCE_PRIORITY: List[str] = [
    "openalex", "crossref", "semantic_scholar", "google_scholar", "ssrn"
]

# DOI supplementation settings
SUPPLEMENT_DOI: bool = os.environ.get("BIBLIOGRAPHY_SUPPLEMENT_DOI", "true").lower() == "true"
DOI_SUPPLEMENT_MAX_ATTEMPTS: int = int(os.environ.get("BIBLIOGRAPHY_DOI_SUPPLEMENT_MAX", "10"))

# Smart multi-round retrieval settings
SMART_MULTI_ROUND: bool = os.environ.get("BIBLIOGRAPHY_SMART_MULTI_ROUND", "true").lower() == "true"
MULTI_ROUND_THRESHOLD: float = float(os.environ.get("BIBLIOGRAPHY_MULTI_ROUND_THRESHOLD", "0.5"))

# Fuzzy matching thresholds
TITLE_MATCH_THRESHOLD: float = float(os.environ.get("BIBLIOGRAPHY_TITLE_MATCH_THRESHOLD", "0.9"))
TITLE_MERGE_THRESHOLD: float = float(os.environ.get("BIBLIOGRAPHY_TITLE_MERGE_THRESHOLD", "0.85"))

# DOI resolution timeout (seconds)
DOI_RESOLUTION_TIMEOUT: float = float(os.environ.get("BIBLIOGRAPHY_DOI_TIMEOUT", "5.0"))


# =============================================================================
# Metadata Configuration
# =============================================================================

REFERENCES_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent.parent / "references"
TOPICS_DIR: Path = REFERENCES_DIR
DEFAULT_TOPIC: str = "coaching-papers"
METADATA_FILENAME: str = "metadata.json"
KB_LITERATURE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent.parent / "knowledge-base" / "01-literature"


# =============================================================================
# Logging Configuration
# =============================================================================

LOG_LEVEL: str = os.environ.get("BIBLIOGRAPHY_LOG_LEVEL", "WARNING").upper()
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# =============================================================================
# Utility Functions
# =============================================================================

def get_temp_dir() -> Path:
    """
    Get or create the temporary directory for search results.

    Returns:
        Path to the temporary directory
    """
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return TEMP_DIR


def validate_max_results(max_results: int) -> int:
    """
    Validate and clamp max_results to acceptable range.

    Args:
        max_results: Requested maximum number of results

    Returns:
        Clamped value within acceptable range
    """
    return max(MIN_MAX_RESULTS, min(MAX_MAX_RESULTS, max_results))


def get_user_agent(service: str = "crossref") -> str:
    """
    Get appropriate User-Agent header for API requests.

    Args:
        service: The API service name ('crossref' or others)

    Returns:
        User-Agent string
    """
    if service.lower() == "crossref":
        return CROSSREF_USER_AGENT
    return "BibliographySearch/0.2.0-portable"


# =============================================================================
# ABS Journal Configuration
# =============================================================================

# Path to ABS journals JSON file
ABS_JOURNALS_PATH: Path = Path(__file__).parent / "abs_journals.json"

# Cache for loaded ABS journals
_ABS_JOURNALS_CACHE: Optional[Dict[str, Any]] = None


def load_abs_journals() -> Dict[str, Any]:
    """
    Load ABS journals from JSON file.

    Returns:
        Dictionary containing ABS journal data with structure:
        {
            "metadata": {...},
            "journals": {
                "4*": [...],
                "4": [...],
                "3": [...]
            }
        }

    Raises:
        FileNotFoundError: If abs_journals.json doesn't exist
        json.JSONDecodeError: If JSON file is invalid
    """
    global _ABS_JOURNALS_CACHE

    if _ABS_JOURNALS_CACHE is not None:
        return _ABS_JOURNALS_CACHE

    if not ABS_JOURNALS_PATH.exists():
        raise FileNotFoundError(
            f"ABS journals file not found at {ABS_JOURNALS_PATH}. "
            "Please create abs_journals.json with ABS journal data."
        )

    with open(ABS_JOURNALS_PATH, 'r', encoding='utf-8') as f:
        _ABS_JOURNALS_CACHE = json.load(f)

    return _ABS_JOURNALS_CACHE


def get_abs_journals(
    rating: Optional[str] = None,
    field: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get ABS journals filtered by rating and/or field.

    Args:
        rating: ABS rating filter ('4*', '4', '3', or None for all)
        field: Academic field filter (e.g., 'Management', 'Psychology')

    Returns:
        List of journal dictionaries with keys: name, issn, domain, field

    Examples:
        >>> get_abs_journals(rating='4*')  # All 4* journals
        >>> get_abs_journals(field='Psychology')  # All Psychology journals
        >>> get_abs_journals(rating='4', field='Management')  # 4-rated Management journals
    """
    data = load_abs_journals()
    journals = data.get('journals', {})

    results = []

    # Determine which ratings to include
    if rating:
        rating_key = rating.upper() if rating == '4*' else rating
        if rating_key in journals:
            rating_journals = journals[rating_key]
            results.extend(rating_journals)
    else:
        # Include all ratings
        for rating_journals in journals.values():
            results.extend(rating_journals)

    # Filter by field if specified
    if field:
        results = [j for j in results if j.get('field', '').lower() == field.lower()]

    return results


def get_abs_issns(
    rating: Optional[str] = None,
    field: Optional[str] = None
) -> List[str]:
    """
    Get list of ISSNs for ABS journals filtered by rating and/or field.

    Args:
        rating: ABS rating filter ('4*', '4', '3', or None for all)
        field: Academic field filter

    Returns:
        List of ISSN strings

    Examples:
        >>> get_abs_issns(rating='4*')  # ['0001-4273', '0021-9010', ...]
    """
    journals = get_abs_journals(rating=rating, field=field)
    return [j['issn'] for j in journals if j.get('issn')]


def get_abs_domains(
    rating: Optional[str] = None,
    field: Optional[str] = None
) -> List[str]:
    """
    Get list of domains for ABS journals filtered by rating and/or field.

    Args:
        rating: ABS rating filter ('4*', '4', '3', or None for all)
        field: Academic field filter

    Returns:
        List of domain strings for site: filtering in web searches

    Examples:
        >>> get_abs_domains(rating='4*')  # ['journals.aom.org', 'apa.org/pubs/journals/apl', ...]
    """
    journals = get_abs_journals(rating=rating, field=field)
    return [j['domain'] for j in journals if j.get('domain')]


def get_abs_journal_names(
    rating: Optional[str] = None,
    field: Optional[str] = None
) -> List[str]:
    """
    Get list of journal names for ABS journals filtered by rating and/or field.

    Args:
        rating: ABS rating filter ('4*', '4', '3', or None for all)
        field: Academic field filter

    Returns:
        List of journal name strings

    Examples:
        >>> get_abs_journal_names(rating='4*')  # ['Academy of Management Journal', ...]
    """
    journals = get_abs_journals(rating=rating, field=field)
    return [j['name'] for j in journals]


def clear_abs_journals_cache() -> None:
    """
    Clear the cached ABS journals data.

    Useful if abs_journals.json is modified and needs to be reloaded.
    """
    global _ABS_JOURNALS_CACHE
    _ABS_JOURNALS_CACHE = None


# =============================================================================
# Configuration Validation
# =============================================================================

def validate_configuration() -> list[str]:
    """
    Validate the current configuration and return any warnings.

    Returns:
        List of warning messages (empty if configuration is valid)
    """
    warnings = []

    # Check if temp directory is writable
    try:
        get_temp_dir()
        test_file = TEMP_DIR / ".write_test"
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        warnings.append(f"Cannot write to temp directory: {e}")

    # Warn if Semantic Scholar API key is not set (optional but recommended)
    if not SEMANTIC_SCHOLAR_API_KEY:
        warnings.append(
            "Semantic Scholar API key not set. Rate limits will be lower. "
            "Set SEMANTIC_SCHOLAR_API_KEY environment variable for higher limits."
        )

    # Warn if Tavily API key is not set (required for Google Scholar replacement)
    if not TAVILY_API_KEY:
        warnings.append(
            "Tavily API key not set. Google Scholar requests will not work. "
            "Get a free key at https://tavily.com and set TAVILY_API_KEY environment variable."
        )

    # Warn about generic CrossRef email
    if "example.com" in CROSSREF_POLITE_MAILTO:
        warnings.append(
            "Using generic CrossRef email. Set CROSSREF_EMAIL environment variable "
            "with your email for better rate limits and polite API usage."
        )

    return warnings
