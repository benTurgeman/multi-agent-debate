"""LLM provider models."""
from enum import Enum

from pydantic import BaseModel, Field


class ModelProvider(str, Enum):
    """Supported LLM providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class LLMConfig(BaseModel):
    """Configuration for an LLM model."""

    provider: ModelProvider = Field(
        ..., description="LLM provider (anthropic, openai, etc.)"
    )
    model_name: str = Field(
        ...,
        description="Specific model name (e.g., 'claude-3-5-sonnet-20241022', 'gpt-4o')",
    )
    api_key_env_var: str = Field(
        ...,
        description="Environment variable name containing the API key (e.g., 'ANTHROPIC_API_KEY')",
    )
