"""Tests for LiteLLM unified client implementation."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import litellm

from services.llm.litellm_client import LiteLLMClient


class TestLiteLLMClient:
    """Tests for LiteLLM unified client."""

    @pytest.fixture
    def anthropic_client(self):
        """Create a LiteLLM client configured for Anthropic."""
        return LiteLLMClient(
            model_name="anthropic/claude-sonnet-4-5-20250929",
            api_key="test-anthropic-key",
        )

    @pytest.fixture
    def openai_client(self):
        """Create a LiteLLM client configured for OpenAI."""
        return LiteLLMClient(
            model_name="openai/gpt-4o",
            api_key="test-openai-key",
        )

    @pytest.fixture
    def ollama_client(self):
        """Create a LiteLLM client configured for Ollama."""
        return LiteLLMClient(
            model_name="ollama/llama2",
            api_base="http://localhost:11434",
        )

    @pytest.mark.asyncio
    async def test_send_message_anthropic(self, anthropic_client):
        """Test successful message sending to Anthropic via LiteLLM."""
        # Mock response
        mock_choice = MagicMock()
        mock_choice.message.content = "This is a test response from Claude"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = MagicMock(
            prompt_tokens=10, completion_tokens=20, total_tokens=30
        )

        # Mock litellm.acompletion
        with patch("litellm.acompletion", new=AsyncMock(return_value=mock_response)):
            result = await anthropic_client.send_message(
                system_prompt="You are a helpful assistant.",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=1.0,
                max_tokens=1024,
            )

            assert result == "This is a test response from Claude"
            litellm.acompletion.assert_called_once()

            # Verify call arguments
            call_args = litellm.acompletion.call_args
            assert call_args.kwargs["model"] == "anthropic/claude-sonnet-4-5-20250929"
            assert call_args.kwargs["temperature"] == 1.0
            assert call_args.kwargs["max_tokens"] == 1024
            assert call_args.kwargs["api_key"] == "test-anthropic-key"
            # Verify system prompt was added
            assert call_args.kwargs["messages"][0]["role"] == "system"
            assert (
                call_args.kwargs["messages"][0]["content"]
                == "You are a helpful assistant."
            )

    @pytest.mark.asyncio
    async def test_send_message_openai(self, openai_client):
        """Test successful message sending to OpenAI via LiteLLM."""
        # Mock response
        mock_choice = MagicMock()
        mock_choice.message.content = "This is a test response from GPT"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = MagicMock(
            prompt_tokens=15, completion_tokens=25, total_tokens=40
        )

        with patch("litellm.acompletion", new=AsyncMock(return_value=mock_response)):
            result = await openai_client.send_message(
                system_prompt="You are a helpful assistant.",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.7,
                max_tokens=2048,
            )

            assert result == "This is a test response from GPT"
            litellm.acompletion.assert_called_once()

            # Verify call arguments
            call_args = litellm.acompletion.call_args
            assert call_args.kwargs["model"] == "openai/gpt-4o"
            assert call_args.kwargs["temperature"] == 0.7
            assert call_args.kwargs["max_tokens"] == 2048

    @pytest.mark.asyncio
    async def test_send_message_ollama(self, ollama_client):
        """Test successful message sending to Ollama via LiteLLM."""
        # Mock response
        mock_choice = MagicMock()
        mock_choice.message.content = "This is a test response from Llama"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        # Ollama might not always return usage
        mock_response.usage = None

        with patch("litellm.acompletion", new=AsyncMock(return_value=mock_response)):
            result = await ollama_client.send_message(
                system_prompt="You are a helpful assistant.",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.8,
                max_tokens=512,
            )

            assert result == "This is a test response from Llama"
            litellm.acompletion.assert_called_once()

            # Verify api_base was passed
            call_args = litellm.acompletion.call_args
            assert call_args.kwargs["api_base"] == "http://localhost:11434"
            assert call_args.kwargs["model"] == "ollama/llama2"

    @pytest.mark.asyncio
    async def test_send_message_empty_response(self, anthropic_client):
        """Test handling of empty response from LiteLLM."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.choices = []

        with patch("litellm.acompletion", new=AsyncMock(return_value=mock_response)):
            with pytest.raises(
                ValueError, match="Empty response from anthropic via LiteLLM"
            ):
                await anthropic_client.send_message(
                    system_prompt="Test",
                    messages=[{"role": "user", "content": "Test"}],
                    temperature=1.0,
                    max_tokens=1024,
                )

    @pytest.mark.asyncio
    async def test_send_message_authentication_error(self, anthropic_client):
        """Test handling of authentication errors."""
        with patch(
            "litellm.acompletion",
            new=AsyncMock(
                side_effect=litellm.AuthenticationError(
                    message="Invalid API key",
                    llm_provider="anthropic",
                    model="claude-sonnet-4-5-20250929",
                )
            ),
        ):
            with pytest.raises(Exception, match="Authentication failed for anthropic"):
                await anthropic_client.send_message(
                    system_prompt="Test",
                    messages=[{"role": "user", "content": "Test"}],
                    temperature=1.0,
                    max_tokens=1024,
                )

    @pytest.mark.asyncio
    async def test_send_message_rate_limit_error(self, openai_client):
        """Test handling of rate limit errors (should retry)."""
        with patch(
            "litellm.acompletion",
            new=AsyncMock(
                side_effect=litellm.RateLimitError(
                    message="Rate limit exceeded", llm_provider="openai", model="gpt-4o"
                )
            ),
        ):
            with pytest.raises(litellm.RateLimitError):
                await openai_client.send_message(
                    system_prompt="Test",
                    messages=[{"role": "user", "content": "Test"}],
                    temperature=1.0,
                    max_tokens=1024,
                )

    @pytest.mark.asyncio
    async def test_send_message_context_window_exceeded(self, anthropic_client):
        """Test handling of context window exceeded errors."""
        with patch(
            "litellm.acompletion",
            new=AsyncMock(
                side_effect=litellm.ContextWindowExceededError(
                    message="Context too long",
                    llm_provider="anthropic",
                    model="claude-sonnet-4-5-20250929",
                )
            ),
        ):
            with pytest.raises(Exception, match="Message too long for anthropic"):
                await anthropic_client.send_message(
                    system_prompt="Test",
                    messages=[{"role": "user", "content": "Test"}],
                    temperature=1.0,
                    max_tokens=1024,
                )

    @pytest.mark.asyncio
    async def test_send_message_bad_request(self, openai_client):
        """Test handling of bad request errors."""
        with patch(
            "litellm.acompletion",
            new=AsyncMock(
                side_effect=litellm.BadRequestError(
                    message="Invalid request", llm_provider="openai", model="gpt-4o"
                )
            ),
        ):
            with pytest.raises(Exception, match="Invalid request to openai"):
                await openai_client.send_message(
                    system_prompt="Test",
                    messages=[{"role": "user", "content": "Test"}],
                    temperature=1.0,
                    max_tokens=1024,
                )

    @pytest.mark.asyncio
    async def test_send_message_service_unavailable(self, ollama_client):
        """Test handling of service unavailable errors (should retry)."""
        with patch(
            "litellm.acompletion",
            new=AsyncMock(
                side_effect=litellm.ServiceUnavailableError(
                    message="Service unavailable", llm_provider="ollama", model="llama2"
                )
            ),
        ):
            with pytest.raises(litellm.ServiceUnavailableError):
                await ollama_client.send_message(
                    system_prompt="Test",
                    messages=[{"role": "user", "content": "Test"}],
                    temperature=1.0,
                    max_tokens=1024,
                )

    @pytest.mark.asyncio
    async def test_send_message_connection_error(self, anthropic_client):
        """Test handling of connection errors (should retry)."""
        with patch(
            "litellm.acompletion",
            new=AsyncMock(
                side_effect=litellm.APIConnectionError(
                    message="Connection failed",
                    llm_provider="anthropic",
                    model="claude-sonnet-4-5-20250929",
                )
            ),
        ):
            with pytest.raises(litellm.APIConnectionError):
                await anthropic_client.send_message(
                    system_prompt="Test",
                    messages=[{"role": "user", "content": "Test"}],
                    temperature=1.0,
                    max_tokens=1024,
                )

    def test_get_provider_name_anthropic(self, anthropic_client):
        """Test extracting provider name from Anthropic model string."""
        assert anthropic_client.get_provider_name() == "anthropic"

    def test_get_provider_name_openai(self, openai_client):
        """Test extracting provider name from OpenAI model string."""
        assert openai_client.get_provider_name() == "openai"

    def test_get_provider_name_ollama(self, ollama_client):
        """Test extracting provider name from Ollama model string."""
        assert ollama_client.get_provider_name() == "ollama"

    def test_provider_extraction_from_model_name(self):
        """Test provider extraction from various model name formats."""
        # Standard format: provider/model
        client1 = LiteLLMClient(model_name="anthropic/claude-3-5-sonnet")
        assert client1.provider == "anthropic"

        client2 = LiteLLMClient(model_name="openai/gpt-4")
        assert client2.provider == "openai"

        client3 = LiteLLMClient(model_name="ollama/mistral")
        assert client3.provider == "ollama"

        # Edge case: no slash
        client4 = LiteLLMClient(model_name="some-model")
        assert client4.provider == "unknown"


class TestLiteLLMFactory:
    """Tests for factory with LiteLLM client."""

    @patch("services.llm.factory.get_settings")
    def test_create_litellm_client_anthropic(self, mock_get_settings):
        """Test creating LiteLLM client for Anthropic via factory."""
        from models.llm import LLMConfig
        from services.llm.factory import create_llm_client

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.get_api_key_optional.return_value = "test-anthropic-key"
        mock_get_settings.return_value = mock_settings

        # Create config
        config = LLMConfig(
            provider="anthropic",
            model_name="claude-sonnet-4-5-20250929",
            api_key_env_var="ANTHROPIC_API_KEY",
        )

        # Create client
        client = create_llm_client(config)

        assert isinstance(client, LiteLLMClient)
        assert client.get_provider_name() == "anthropic"
        assert client.model_name == "anthropic/claude-sonnet-4-5-20250929"
        mock_settings.get_api_key_optional.assert_called_once_with("ANTHROPIC_API_KEY")

    @patch("services.llm.factory.get_settings")
    def test_create_litellm_client_ollama_no_api_key(self, mock_get_settings):
        """Test creating LiteLLM client for Ollama without API key."""
        from models.llm import LLMConfig
        from services.llm.factory import create_llm_client

        # Mock settings
        mock_settings = MagicMock()
        mock_get_settings.return_value = mock_settings

        # Create config for Ollama (no API key)
        config = LLMConfig(
            provider="ollama", model_name="llama2", api_base="http://localhost:11434"
        )

        # Create client
        client = create_llm_client(config)

        assert isinstance(client, LiteLLMClient)
        assert client.get_provider_name() == "ollama"
        assert client.model_name == "ollama/llama2"
        assert client.api_base == "http://localhost:11434"
        assert client.api_key is None
        # Should not call get_api_key_optional when api_key_env_var is None
        mock_settings.get_api_key_optional.assert_not_called()
