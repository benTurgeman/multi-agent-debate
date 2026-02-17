"""Factory for creating LLM clients."""
import logging

from models.llm import LLMConfig
from services.llm.base import BaseLLMClient
from services.llm.litellm_client import LiteLLMClient
from core.config import get_settings

logger = logging.getLogger(__name__)


def create_llm_client(llm_config: LLMConfig) -> BaseLLMClient:
    """
    Factory method to create the appropriate LLM client using LiteLLM.

    Args:
        llm_config: LLM configuration specifying provider and model

    Returns:
        Initialized LiteLLM client instance

    Raises:
        ConfigurationError: If API key is required but missing
    """
    settings = get_settings()

    # Get API key from environment if specified (optional for local models)
    api_key = None
    if llm_config.api_key_env_var:
        api_key = settings.get_api_key_optional(llm_config.api_key_env_var)
        if api_key:
            logger.debug(
                f"Retrieved API key from environment variable: {llm_config.api_key_env_var}"
            )
        else:
            logger.warning(
                f"API key environment variable '{llm_config.api_key_env_var}' not set. "
                f"Proceeding without API key (local models only)."
            )

    # Create unified LiteLLM client
    logger.info(
        f"Creating LiteLLM client - Provider: {llm_config.provider}, "
        f"Model: {llm_config.model_name}, "
        f"API Base: {llm_config.api_base or 'default'}"
    )

    return LiteLLMClient(
        model_name=llm_config.litellm_model_name,
        api_key=api_key,
        api_base=llm_config.api_base,
    )
