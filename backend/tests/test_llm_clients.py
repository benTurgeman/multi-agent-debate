"""Tests for LLM client implementations."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import anthropic
import openai

from models.llm import LLMConfig, ModelProvider
from services.llm.anthropic_client import AnthropicClient
from services.llm.openai_client import OpenAIClient
from services.llm.factory import create_llm_client
from core.exceptions import ConfigurationError


class TestAnthropicClient:
    """Tests for Anthropic LLM client."""

    @pytest.fixture
    def anthropic_client(self):
        """Create an Anthropic client for testing."""
        return AnthropicClient(
            api_key="test-api-key",
            model_name="claude-3-5-sonnet-20241022"
        )

    @pytest.mark.asyncio
    async def test_send_message_success(self, anthropic_client):
        """Test successful message sending to Anthropic API."""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is a test response from Claude")]
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)

        # Mock the client's messages.create method
        anthropic_client.client.messages.create = AsyncMock(return_value=mock_response)

        # Test the send_message method
        result = await anthropic_client.send_message(
            system_prompt="You are a helpful assistant.",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=1.0,
            max_tokens=1024,
        )

        assert result == "This is a test response from Claude"
        anthropic_client.client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_empty_response(self, anthropic_client):
        """Test handling of empty response from Anthropic API."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.content = []

        anthropic_client.client.messages.create = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="Empty response from Anthropic API"):
            await anthropic_client.send_message(
                system_prompt="Test",
                messages=[{"role": "user", "content": "Test"}],
                temperature=1.0,
                max_tokens=1024,
            )

    @pytest.mark.asyncio
    async def test_send_message_connection_error(self, anthropic_client):
        """Test handling of connection errors."""
        anthropic_client.client.messages.create = AsyncMock(
            side_effect=anthropic.APIConnectionError(request=MagicMock())
        )

        with pytest.raises(anthropic.APIConnectionError):
            await anthropic_client.send_message(
                system_prompt="Test",
                messages=[{"role": "user", "content": "Test"}],
                temperature=1.0,
                max_tokens=1024,
            )

    @pytest.mark.asyncio
    async def test_send_message_rate_limit_error(self, anthropic_client):
        """Test handling of rate limit errors."""
        anthropic_client.client.messages.create = AsyncMock(
            side_effect=anthropic.RateLimitError(
                response=MagicMock(),
                body=None,
                message="Rate limit exceeded"
            )
        )

        with pytest.raises(anthropic.RateLimitError):
            await anthropic_client.send_message(
                system_prompt="Test",
                messages=[{"role": "user", "content": "Test"}],
                temperature=1.0,
                max_tokens=1024,
            )

    def test_get_provider_name(self, anthropic_client):
        """Test getting provider name."""
        assert anthropic_client.get_provider_name() == "anthropic"


class TestOpenAIClient:
    """Tests for OpenAI LLM client."""

    @pytest.fixture
    def openai_client(self):
        """Create an OpenAI client for testing."""
        return OpenAIClient(
            api_key="test-api-key",
            model_name="gpt-4o"
        )

    @pytest.mark.asyncio
    async def test_send_message_success(self, openai_client):
        """Test successful message sending to OpenAI API."""
        # Mock response
        mock_choice = MagicMock()
        mock_choice.message.content = "This is a test response from GPT"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=20)

        # Mock the client's chat.completions.create method
        openai_client.client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Test the send_message method
        result = await openai_client.send_message(
            system_prompt="You are a helpful assistant.",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=1.0,
            max_tokens=1024,
        )

        assert result == "This is a test response from GPT"
        openai_client.client.chat.completions.create.assert_called_once()

        # Verify system prompt was added to messages
        call_args = openai_client.client.chat.completions.create.call_args
        messages_arg = call_args.kwargs["messages"]
        assert messages_arg[0]["role"] == "system"
        assert messages_arg[0]["content"] == "You are a helpful assistant."

    @pytest.mark.asyncio
    async def test_send_message_empty_response(self, openai_client):
        """Test handling of empty response from OpenAI API."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.choices = []

        openai_client.client.chat.completions.create = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="Empty response from OpenAI API"):
            await openai_client.send_message(
                system_prompt="Test",
                messages=[{"role": "user", "content": "Test"}],
                temperature=1.0,
                max_tokens=1024,
            )

    @pytest.mark.asyncio
    async def test_send_message_connection_error(self, openai_client):
        """Test handling of connection errors."""
        openai_client.client.chat.completions.create = AsyncMock(
            side_effect=openai.APIConnectionError(request=MagicMock())
        )

        with pytest.raises(openai.APIConnectionError):
            await openai_client.send_message(
                system_prompt="Test",
                messages=[{"role": "user", "content": "Test"}],
                temperature=1.0,
                max_tokens=1024,
            )

    @pytest.mark.asyncio
    async def test_send_message_rate_limit_error(self, openai_client):
        """Test handling of rate limit errors."""
        openai_client.client.chat.completions.create = AsyncMock(
            side_effect=openai.RateLimitError(
                response=MagicMock(),
                body=None,
                message="Rate limit exceeded"
            )
        )

        with pytest.raises(openai.RateLimitError):
            await openai_client.send_message(
                system_prompt="Test",
                messages=[{"role": "user", "content": "Test"}],
                temperature=1.0,
                max_tokens=1024,
            )

    def test_get_provider_name(self, openai_client):
        """Test getting provider name."""
        assert openai_client.get_provider_name() == "openai"


class TestLLMFactory:
    """Tests for LLM client factory."""

    @patch("services.llm.factory.get_settings")
    def test_create_anthropic_client(self, mock_get_settings):
        """Test creating Anthropic client via factory."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.get_api_key.return_value = "test-anthropic-key"
        mock_get_settings.return_value = mock_settings

        # Create config
        config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="ANTHROPIC_API_KEY"
        )

        # Create client
        client = create_llm_client(config)

        assert isinstance(client, AnthropicClient)
        assert client.get_provider_name() == "anthropic"
        mock_settings.get_api_key.assert_called_once_with("ANTHROPIC_API_KEY")

    @patch("services.llm.factory.get_settings")
    def test_create_openai_client(self, mock_get_settings):
        """Test creating OpenAI client via factory."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.get_api_key.return_value = "test-openai-key"
        mock_get_settings.return_value = mock_settings

        # Create config
        config = LLMConfig(
            provider=ModelProvider.OPENAI,
            model_name="gpt-4o",
            api_key_env_var="OPENAI_API_KEY"
        )

        # Create client
        client = create_llm_client(config)

        assert isinstance(client, OpenAIClient)
        assert client.get_provider_name() == "openai"
        mock_settings.get_api_key.assert_called_once_with("OPENAI_API_KEY")

    @patch("services.llm.factory.get_settings")
    def test_create_client_missing_api_key(self, mock_get_settings):
        """Test error handling when API key is missing."""
        # Mock settings to raise error
        mock_settings = MagicMock()
        mock_settings.get_api_key.side_effect = ConfigurationError("API key not found")
        mock_get_settings.return_value = mock_settings

        # Create config
        config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key_env_var="MISSING_KEY"
        )

        # Should raise ConfigurationError
        with pytest.raises(ConfigurationError, match="API key not found"):
            create_llm_client(config)
