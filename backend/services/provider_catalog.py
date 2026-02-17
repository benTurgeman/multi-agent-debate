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
                model_id="claude-opus-4-6",
                display_name="Claude Opus 4.6",
                description="Latest and most capable Claude model for complex reasoning",
                context_window=200000,
                max_output_tokens=8192,
                recommended=True,
                pricing_tier="premium",
            ),
            ModelInfo(
                model_id="claude-sonnet-4-5-20250929",
                display_name="Claude Sonnet 4.5",
                description="Balanced performance and speed for most tasks",
                context_window=200000,
                max_output_tokens=8192,
                recommended=True,
                pricing_tier="standard",
            ),
            ModelInfo(
                model_id="claude-opus-4-5-20251101",
                display_name="Claude Opus 4.5",
                description="Powerful model for complex reasoning tasks",
                context_window=200000,
                max_output_tokens=8192,
                recommended=False,
                pricing_tier="premium",
            ),
            ModelInfo(
                model_id="claude-haiku-4-5-20251001",
                display_name="Claude Haiku 4.5",
                description="Fast and efficient model for simpler tasks",
                context_window=200000,
                max_output_tokens=4096,
                recommended=False,
                pricing_tier="economy",
            ),
            ModelInfo(
                model_id="claude-opus-4-1-20250805",
                display_name="Claude Opus 4.1",
                description="Advanced reasoning model",
                context_window=200000,
                max_output_tokens=8192,
                recommended=False,
                pricing_tier="premium",
            ),
            ModelInfo(
                model_id="claude-opus-4-20250514",
                display_name="Claude Opus 4",
                description="Previous generation Opus model",
                context_window=200000,
                max_output_tokens=4096,
                recommended=False,
                pricing_tier="premium",
            ),
            ModelInfo(
                model_id="claude-sonnet-4-20250514",
                display_name="Claude Sonnet 4",
                description="Previous generation Sonnet model",
                context_window=200000,
                max_output_tokens=8192,
                recommended=False,
                pricing_tier="standard",
            ),
            ModelInfo(
                model_id="claude-3-haiku-20240307",
                display_name="Claude Haiku 3",
                description="Claude 3 generation fast model",
                context_window=200000,
                max_output_tokens=4096,
                recommended=False,
                pricing_tier="economy",
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
    ProviderInfo(
        provider_id=ModelProvider.OLLAMA,
        display_name="Ollama",
        description="Local LLM models via Ollama",
        api_key_env_var=None,  # No API key required for local models
        documentation_url="https://ollama.ai/",
        models=[
            ModelInfo(
                model_id="llama2",
                display_name="Llama 2 7B",
                description="Meta's Llama 2 7B model - good for general tasks",
                context_window=4096,
                max_output_tokens=2048,
                recommended=False,
                pricing_tier="free",
            ),
            ModelInfo(
                model_id="llama2:13b",
                display_name="Llama 2 13B",
                description="Meta's Llama 2 13B model - better reasoning",
                context_window=4096,
                max_output_tokens=2048,
                recommended=False,
                pricing_tier="free",
            ),
            ModelInfo(
                model_id="mistral",
                display_name="Mistral 7B",
                description="Mistral 7B model - efficient and capable",
                context_window=8192,
                max_output_tokens=4096,
                recommended=False,
                pricing_tier="free",
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
