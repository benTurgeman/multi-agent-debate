"""Custom exceptions for the debate system."""


class DebateError(Exception):
    """Base exception for debate-related errors."""

    pass


class DebateNotFoundError(DebateError):
    """Raised when a debate is not found."""

    pass


class DebateExecutionError(DebateError):
    """Raised when debate execution fails."""

    pass


class AgentError(Exception):
    """Base exception for agent-related errors."""

    pass


class LLMClientError(Exception):
    """Base exception for LLM client errors."""

    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""

    pass


class StorageError(Exception):
    """Base exception for storage-related errors."""

    pass
