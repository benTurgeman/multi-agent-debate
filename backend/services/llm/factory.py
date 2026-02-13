"""Factory for creating LLM clients."""
import logging

from models.llm import LLMConfig, ModelProvider
from services.llm.base import BaseLLMClient
from services.llm.anthropic_client import AnthropicClient
from services.llm.openai_client import OpenAIClient
from core.config import get_settings
from core.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


def create_llm_client(llm_config: LLMConfig) -> BaseLLMClient:
    """
    Factory method to create the appropriate LLM client.

    Args:
        llm_config: LLM configuration specifying provider and model

    Returns:
        Initialized LLM client instance

    Raises:
        ConfigurationError: If provider is unsupported or API key is missing
    """
    settings = get_settings()

    # Get API key from environment
    try:
        api_key = settings.get_api_key(llm_config.api_key_env_var)
    except ConfigurationError as e:
        logger.error(
            f"Failed to get API key for {llm_config.provider}: {e}"
        )
        raise

    # Create appropriate client based on provider
    if llm_config.provider == ModelProvider.ANTHROPIC:
        logger.info(
            f"Creating Anthropic client for model: {llm_config.model_name}"
        )
        return AnthropicClient(api_key=api_key, model_name=llm_config.model_name)

    elif llm_config.provider == ModelProvider.OPENAI:
        logger.info(
            f"Creating OpenAI client for model: {llm_config.model_name}"
        )
        return OpenAIClient(api_key=api_key, model_name=llm_config.model_name)

    else:
        raise ConfigurationError(
            f"Unsupported LLM provider: {llm_config.provider}. "
            f"Supported providers: {[p.value for p in ModelProvider]}"
        )
