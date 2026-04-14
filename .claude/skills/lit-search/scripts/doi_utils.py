"""
DOI Utilities for Bibliography Module

Provides DOI validation, extraction, cleaning, and metadata verification functions.
"""

import re
import logging
from typing import Optional, Dict, Any, List
from difflib import SequenceMatcher
import requests

# Configure logging
logger = logging.getLogger(__name__)

# DOI regex pattern - matches standard DOI format: 10.xxxx/xxxxx
# Handles various DOI suffixes and special characters
DOI_PATTERN = re.compile(
    r"\b10\.\d{4,9}/[^\s\]>\"'`]+",
    re.IGNORECASE
)

# Common DOI URL prefixes to strip
DOI_PREFIXES = [
    'https://doi.org/',
    'http://doi.org/',
    'https://dx.doi.org/',
    'http://dx.doi.org/',
    'doi:',
    'DOI:',
    'doi ',
    'DOI ',
]

# Standard field names that might contain DOI in structured data
DOI_FIELD_NAMES = ['doi', 'DOI', 'identifier', 'id']


def validate_doi_format(doi: str) -> bool:
    """
    Validate that a string matches standard DOI format.

    DOI format: 10.xxxx/xxxxx where xxxx is 4+ digits and xxxxx is variable

    Args:
        doi: The DOI string to validate

    Returns:
        True if DOI matches standard format, False otherwise
    """
    if not doi or not isinstance(doi, str):
        return False

    # Clean the DOI first
    cleaned = clean_doi(doi)

    # Check if it matches the pattern
    match = DOI_PATTERN.fullmatch(cleaned)
    return match is not None


def extract_doi_from_text(text: str) -> Optional[str]:
    """
    Extract DOI from text content using regex pattern matching.

    Handles:
    - Direct DOI mentions (10.xxxx/xxxxx)
    - DOI URLs (https://doi.org/10.xxxx/xxxxx)
    - DOI in various capitalizations

    Args:
        text: Text content to search for DOI

    Returns:
        Cleaned DOI string if found, None otherwise
    """
    if not text or not isinstance(text, str):
        return None

    # Try direct pattern match first
    match = DOI_PATTERN.search(text)
    if match:
        return clean_doi(match.group(0))

    # Try looking for DOI URLs
    for prefix in DOI_PREFIXES:
        if prefix.lower() in text.lower():
            # Find the position and extract from there
            idx = text.lower().find(prefix.lower())
            substring = text[idx + len(prefix):idx + len(prefix) + 100]

            # Try to extract DOI from the substring
            doi_match = DOI_PATTERN.search(substring)
            if doi_match:
                return clean_doi(doi_match.group(0))

    return None


def extract_doi_from_url(url: str) -> Optional[str]:
    """
    Extract DOI from a URL.

    Handles:
    - doi.org URLs
    - Journal page URLs with DOI in query
    - Direct links with DOI in path

    Args:
        url: URL string to search for DOI

    Returns:
        Cleaned DOI string if found, None otherwise
    """
    if not url or not isinstance(url, str):
        return None

    # Check for doi.org URLs
    if 'doi.org/' in url.lower():
        # Extract DOI from doi.org URL
        idx = url.lower().find('doi.org/')
        substring = url[idx + 8:]  # Skip 'doi.org/'
        # Remove any query parameters or fragments
        substring = substring.split('?')[0].split('#')[0]
        return clean_doi(substring)

    # Try regex match on entire URL
    return extract_doi_from_text(url)


def clean_doi(doi: str) -> str:
    """
    Clean DOI string by removing prefixes and normalizing.

    Removes:
    - URL prefixes (https://doi.org/, http://doi.org/)
    - "doi:" prefix
    - Leading/trailing whitespace
    - Common formatting issues

    Args:
        doi: The DOI string to clean

    Returns:
        Cleaned DOI string
    """
    if not doi or not isinstance(doi, str):
        return ""

    # Remove URL prefixes
    cleaned = doi
    for prefix in DOI_PREFIXES:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):]
            break

    # Strip whitespace
    cleaned = cleaned.strip()

    # Remove trailing punctuation
    cleaned = cleaned.rstrip('.,;:)]}')

    # Normalize to lowercase (DOI is case-insensitive)
    cleaned = cleaned.lower()

    return cleaned


def verify_doi_metadata(
    doi: str,
    title: str,
    authors: List[str],
    timeout: float = 5.0
) -> Dict[str, Any]:
    """
    Verify DOI by fetching metadata from CrossRef and comparing with provided data.

    Args:
        doi: The DOI to verify
        title: Expected paper title
        authors: Expected author list
        timeout: HTTP request timeout in seconds

    Returns:
        Dictionary with verification results:
        {
            "verified": bool,
            "confidence": float (0.0-1.0),
            "match_details": str,
            "fetched_title": str,
            "fetched_authors": List[str]
        }
    """
    if not validate_doi_format(doi):
        return {
            "verified": False,
            "confidence": 0.0,
            "match_details": "Invalid DOI format",
            "fetched_title": "",
            "fetched_authors": []
        }

    cleaned_doi = clean_doi(doi)

    try:
        # Fetch metadata from CrossRef
        url = f"https://api.crossref.org/works/{cleaned_doi}"
        response = requests.get(url, timeout=timeout)

        if response.status_code != 200:
            return {
                "verified": False,
                "confidence": 0.0,
                "match_details": f"DOI not found (HTTP {response.status_code})",
                "fetched_title": "",
                "fetched_authors": []
            }

        data = response.json()
        item = data.get("message", {})

        # Extract title
        fetched_title = ""
        if "title" in item and item["title"]:
            fetched_title = item["title"][0]

        # Extract authors
        fetched_authors = []
        if "author" in item:
            for author in item["author"]:
                if "given" in author and "family" in author:
                    fetched_authors.append(f"{author['given']} {author['family']}")
                elif "family" in author:
                    fetched_authors.append(author["family"])

        # Compare titles using sequence matching
        title_similarity = 0.0
        if fetched_title and title:
            title_similarity = SequenceMatcher(
                None,
                fetched_title.lower(),
                title.lower()
            ).ratio()

        # Compare authors (partial matching)
        author_match = False
        if fetched_authors and authors:
            # Check if at least one author matches (last name)
            for fetched_author in fetched_authors[:3]:  # Check first 3
                fetched_last = fetched_author.split()[-1].lower()
                for expected_author in authors[:3]:  # Check first 3
                    expected_last = expected_author.split()[-1].lower()
                    if fetched_last == expected_last or fetched_last in expected_author.lower():
                        author_match = True
                        break
                if author_match:
                    break

        # Determine verification status
        verified = title_similarity >= 0.85 and author_match

        return {
            "verified": verified,
            "confidence": title_similarity,
            "match_details": (
                f"Title similarity: {title_similarity:.2f}, "
                f"Author match: {author_match}"
            ),
            "fetched_title": fetched_title,
            "fetched_authors": fetched_authors
        }

    except requests.Timeout:
        return {
            "verified": False,
            "confidence": 0.0,
            "match_details": "DOI verification timed out",
            "fetched_title": "",
            "fetched_authors": []
        }
    except Exception as e:
        logger.error(f"DOI verification error: {e}")
        return {
            "verified": False,
            "confidence": 0.0,
            "match_details": f"Verification error: {str(e)}",
            "fetched_title": "",
            "fetched_authors": []
        }


def verify_doi_resolution(doi: str, timeout: float = 5.0) -> bool:
    """
    Verify that a DOI resolves by checking if doi.org returns a valid redirect.

    Args:
        doi: The DOI to check
        timeout: HTTP request timeout in seconds

    Returns:
        True if DOI resolves successfully, False otherwise
    """
    if not validate_doi_format(doi):
        return False

    cleaned_doi = clean_doi(doi)
    url = f"https://doi.org/{cleaned_doi}"

    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        # Consider any 2xx or 3xx response as valid
        return 200 <= response.status_code < 400
    except requests.Timeout:
        logger.warning(f"DOI resolution timeout: {doi}")
        return False
    except Exception as e:
        logger.error(f"DOI resolution error: {e}")
        return False


def compare_titles(title1: str, title2: str) -> float:
    """
    Compare two titles using sequence matching.

    Args:
        title1: First title
        title2: Second title

    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not title1 or not title2:
        return 0.0

    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio()


def extract_doi_from_dict(data: Dict[str, Any]) -> Optional[str]:
    """
    Extract DOI from a dictionary (e.g., API response).

    Checks common field names and values.

    Args:
        data: Dictionary that might contain DOI

    Returns:
        Cleaned DOI string if found, None otherwise
    """
    if not isinstance(data, dict):
        return None

    # Check direct DOI fields first
    for field in DOI_FIELD_NAMES:
        if field in data:
            doi = data[field]
            if isinstance(doi, str) and validate_doi_format(doi):
                return clean_doi(doi)

    # Check nested externalIds (Semantic Scholar format)
    if "externalIds" in data and isinstance(data["externalIds"], dict):
        doi = data["externalIds"].get("DOI", "")
        if doi and validate_doi_format(doi):
            return clean_doi(doi)

    # Check URL field
    if "url" in data:
        doi = extract_doi_from_url(data["url"])
        if doi:
            return doi

    # Search all string values for DOI pattern
    for value in data.values():
        if isinstance(value, str):
            doi = extract_doi_from_text(value)
            if doi:
                return doi

    return None
