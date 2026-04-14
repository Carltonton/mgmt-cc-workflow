"""
Custom exceptions for the bibliography API client module.

This module defines exception classes used throughout the bibliography
search system for error handling and reporting.
"""

from typing import Optional


class BibliographyError(Exception):
    """Base exception for all bibliography-related errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class APIError(BibliographyError):
    """
    Exception raised when an API request fails.

    This could be due to network issues, server errors, or unexpected responses.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ):
        """
        Initialize the API error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code if applicable
            response_text: Raw response text from the API
        """
        details = {}
        if status_code is not None:
            details["status_code"] = status_code
        if response_text:
            details["response"] = response_text[:200]  # Truncate long responses
        super().__init__(message, details)


class RateLimitError(APIError):
    """
    Exception raised when API rate limit is exceeded.

    This indicates that too many requests have been made in a short time period.
    """

    def __init__(self, message: str = "API rate limit exceeded", retry_after: Optional[int] = None):
        """
        Initialize the rate limit error.

        Args:
            message: Human-readable error message
            retry_after: Suggested retry delay in seconds
        """
        self.retry_after = retry_after
        # Include retry_after in the response_text for visibility
        response_text = f"Retry after: {retry_after} seconds" if retry_after else None
        # Rate limit is HTTP 429
        super().__init__(message, status_code=429, response_text=response_text)


class NotFoundError(BibliographyError):
    """
    Exception raised when a requested resource is not found.

    This could be a paper by DOI that doesn't exist, or a search with no results.
    """

    def __init__(self, message: str, resource_type: Optional[str] = None, identifier: Optional[str] = None):
        """
        Initialize the not found error.

        Args:
            message: Human-readable error message
            resource_type: Type of resource (e.g., "DOI", "paper")
            identifier: The identifier that was not found
        """
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if identifier:
            details["identifier"] = identifier
        super().__init__(message, details)


class ConfigurationError(BibliographyError):
    """
    Exception raised when there is a configuration problem.

    This could be missing API keys, invalid URLs, or other setup issues.
    """

    def __init__(self, message: str, config_key: Optional[str] = None):
        """
        Initialize the configuration error.

        Args:
            message: Human-readable error message
            config_key: The configuration key that is problematic
        """
        details = {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details)


class ValidationError(BibliographyError):
    """
    Exception raised when input validation fails.

    This could be invalid DOI format, missing required fields, etc.
    """

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[str] = None):
        """
        Initialize the validation error.

        Args:
            message: Human-readable error message
            field: The field that failed validation
            value: The invalid value
        """
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value[:100]  # Truncate long values
        super().__init__(message, details)


class TimeoutError(BibliographyError):
    """
    Exception raised when an API request times out.

    This indicates the server did not respond within the expected time.
    """

    def __init__(self, message: str = "API request timed out", timeout_seconds: Optional[int] = None):
        """
        Initialize the timeout error.

        Args:
            message: Human-readable error message
            timeout_seconds: The timeout duration in seconds
        """
        details = {}
        if timeout_seconds is not None:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(message, details)


