"""Configuration management for the debate system."""
import os
from functools import lru_cache
from typing import Dict, Optional

from dotenv import load_dotenv

from core.exceptions import ConfigurationError

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration."""

    def __init__(self):
        """Initialize settings."""
        self._api_keys_cache: Dict[str, str] = {}

    def get_api_key(self, env_var_name: str) -> str:
        """
        Get API key from environment variable.

        Args:
            env_var_name: Name of the environment variable containing the API key

        Returns:
            API key value

        Raises:
            ConfigurationError: If the environment variable is not set
        """
        # Check cache first
        if env_var_name in self._api_keys_cache:
            return self._api_keys_cache[env_var_name]

        # Get from environment
        api_key = os.getenv(env_var_name)
        if not api_key:
            raise ConfigurationError(
                f"API key environment variable '{env_var_name}' is not set. "
                f"Please set it in your .env file or environment."
            )

        # Cache and return
        self._api_keys_cache[env_var_name] = api_key
        return api_key

    def get_api_key_optional(self, env_var_name: str) -> Optional[str]:
        """
        Get API key from environment variable without raising an error if not set.

        Args:
            env_var_name: Name of the environment variable containing the API key

        Returns:
            API key value or None if not set
        """
        return os.getenv(env_var_name)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance
    """
    return Settings()
