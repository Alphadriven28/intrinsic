"""
Custom exceptions for FMP API integration.
Provides structured error types so the API layer can return differentiated responses.
"""


class FMPError(Exception):
    """Base exception for all FMP-related errors."""

    def __init__(self, message, status_code=500, error_code="server_error"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class FMPAuthError(FMPError):
    """Raised when the API key is invalid or missing."""

    def __init__(self, message="API authentication failed. Check your FMP API key."):
        super().__init__(message, status_code=401, error_code="auth_failed")


class FMPRateLimitError(FMPError):
    """Raised when the API quota is exceeded or plan is insufficient."""

    def __init__(self, message="API quota exceeded. Please try again later."):
        super().__init__(message, status_code=429, error_code="rate_limited")


class FMPNotFoundError(FMPError):
    """Raised when the ticker is not found after fallback search."""

    def __init__(self, message="Ticker not listed in US markets."):
        super().__init__(message, status_code=404, error_code="not_found")


class FMPServiceError(FMPError):
    """Raised on network/timeout/unexpected server errors."""

    def __init__(self, message="Temporary server issue. Please try again."):
        super().__init__(message, status_code=502, error_code="server_error")
