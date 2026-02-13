"""Tests for core.config module."""
import os

import pytest

from core.config import Settings, get_settings
from core.exceptions import ConfigurationError


class TestSettings:
    """Test Settings class."""

    def test_get_api_key_success(self, mock_anthropic_api_key):
        """Test successful API key retrieval."""
        settings = Settings()
        api_key = settings.get_api_key("ANTHROPIC_API_KEY")
        assert api_key == mock_anthropic_api_key

    def test_get_api_key_not_set(self, clean_environment):
        """Test API key retrieval when environment variable is not set."""
        settings = Settings()
        with pytest.raises(ConfigurationError) as exc_info:
            settings.get_api_key("NONEXISTENT_API_KEY")
        assert "NONEXISTENT_API_KEY" in str(exc_info.value)

    def test_get_api_key_caching(self, mock_anthropic_api_key):
        """Test that API keys are cached after first retrieval."""
        settings = Settings()

        # First call
        key1 = settings.get_api_key("ANTHROPIC_API_KEY")

        # Change environment variable
        os.environ["ANTHROPIC_API_KEY"] = "different-key"

        # Second call should return cached value
        key2 = settings.get_api_key("ANTHROPIC_API_KEY")

        assert key1 == key2 == mock_anthropic_api_key

    def test_get_api_key_optional_success(self, mock_openai_api_key):
        """Test optional API key retrieval when key is set."""
        settings = Settings()
        api_key = settings.get_api_key_optional("OPENAI_API_KEY")
        assert api_key == mock_openai_api_key

    def test_get_api_key_optional_not_set(self, clean_environment):
        """Test optional API key retrieval when key is not set."""
        settings = Settings()
        api_key = settings.get_api_key_optional("NONEXISTENT_API_KEY")
        assert api_key is None


def test_get_settings_singleton():
    """Test that get_settings returns the same instance (cached)."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
