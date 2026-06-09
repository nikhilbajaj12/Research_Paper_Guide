"""Custom exception classes."""


class PaperGuideException(Exception):
    """Base exception for all PaperGuide AI errors."""

    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        """Initialize exception."""
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FileProcessingError(PaperGuideException):
    """Exception for file processing errors."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, error_code="FILE_PROCESSING_ERROR")


class ComplianceError(PaperGuideException):
    """Exception for compliance analysis errors."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, error_code="COMPLIANCE_ERROR")


class NotFoundError(PaperGuideException):
    """Exception for resource not found errors."""

    def __init__(self, resource_type: str, resource_id: str):
        """Initialize exception."""
        message = f"{resource_type} with ID '{resource_id}' not found."
        super().__init__(message, error_code="NOT_FOUND")


class ValidationError(PaperGuideException):
    """Exception for validation errors."""

    def __init__(self, message: str, field: str = None):
        """Initialize exception."""
        self.field = field
        super().__init__(message, error_code="VALIDATION_ERROR")
