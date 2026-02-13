"""Pytest configuration and fixtures."""
import os
from typing import Generator
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def mock_anthropic_api_key() -> Generator[str, None, None]:
    """Mock Anthropic API key environment variable."""
    original = os.environ.get("ANTHROPIC_API_KEY")
    test_key = "sk-ant-test-key-123"
    os.environ["ANTHROPIC_API_KEY"] = test_key
    yield test_key
    if original:
        os.environ["ANTHROPIC_API_KEY"] = original
    else:
        os.environ.pop("ANTHROPIC_API_KEY", None)


@pytest.fixture
def mock_openai_api_key() -> Generator[str, None, None]:
    """Mock OpenAI API key environment variable."""
    original = os.environ.get("OPENAI_API_KEY")
    test_key = "sk-test-key-456"
    os.environ["OPENAI_API_KEY"] = test_key
    yield test_key
    if original:
        os.environ["OPENAI_API_KEY"] = original
    else:
        os.environ.pop("OPENAI_API_KEY", None)


@pytest.fixture
def clean_environment() -> Generator[None, None, None]:
    """Clean environment variables for testing."""
    # Store original values
    original_anthropic = os.environ.get("ANTHROPIC_API_KEY")
    original_openai = os.environ.get("OPENAI_API_KEY")

    # Remove keys
    os.environ.pop("ANTHROPIC_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)

    yield

    # Restore original values
    if original_anthropic:
        os.environ["ANTHROPIC_API_KEY"] = original_anthropic
    if original_openai:
        os.environ["OPENAI_API_KEY"] = original_openai


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing."""
    client = Mock()
    client.send_message = AsyncMock(return_value="Mock LLM response")
    client.get_provider_name = Mock(return_value="mock_provider")
    return client
