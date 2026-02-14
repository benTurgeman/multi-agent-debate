"""Static catalog service for LLM providers and models."""

from typing import List

from models.llm import ModelProvider
from models.provider_catalog import ModelInfo, ProviderInfo


# Static catalog of supported providers and models
PROVIDER_CATALOG: List[ProviderInfo] = [
    ProviderInfo(
        provider_id=ModelProvider.ANTHROPIC,
        display_name="Anthropic",
        description="Claude models by Anthropic",
        api_key_env_var="ANTHROPIC_API_KEY",
        documentation_url="https://docs.anthropic.com/",
        models=[
            ModelInfo(
                model_id="claude-3-5-sonnet-20241022",
                display_name="Claude 3.5 Sonnet",
                description="Most intelligent model, balanced performance and speed",
                context_window=200000,
                max_output_tokens=8192,
                recommended=True,
                pricing_tier="standard",
            ),
            ModelInfo(
                model_id="claude-3-opus-20240229",
                display_name="Claude 3 Opus",
                description="Most powerful model for complex tasks",
                context_window=200000,
                max_output_tokens=4096,
                recommended=False,
                pricing_tier="premium",
            ),
        ],
    ),
    ProviderInfo(
        provider_id=ModelProvider.OPENAI,
        display_name="OpenAI",
        description="GPT models by OpenAI",
        api_key_env_var="OPENAI_API_KEY",
        documentation_url="https://platform.openai.com/docs/",
        models=[
            ModelInfo(
                model_id="gpt-4o",
                display_name="GPT-4o",
                description="Fastest and most affordable flagship model",
                context_window=128000,
                max_output_tokens=16384,
                recommended=True,
                pricing_tier="standard",
            ),
            ModelInfo(
                model_id="gpt-4-turbo",
                display_name="GPT-4 Turbo",
                description="Previous generation, strong reasoning",
                context_window=128000,
                max_output_tokens=4096,
                recommended=False,
                pricing_tier="standard",
            ),
        ],
    ),
]


def get_provider_catalog() -> List[ProviderInfo]:
    """
    Get the static provider catalog.

    Returns:
        List of all supported providers with their models
    """
    return PROVIDER_CATALOG


def get_provider_by_id(provider_id: ModelProvider) -> ProviderInfo | None:
    """
    Get a specific provider by ID.

    Args:
        provider_id: Provider identifier to search for

    Returns:
        Provider information if found, None otherwise
    """
    for provider in PROVIDER_CATALOG:
        if provider.provider_id == provider_id:
            return provider
    return None
