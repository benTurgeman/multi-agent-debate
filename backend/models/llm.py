"""LLM provider models."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ModelProvider(str, Enum):
    """Supported LLM providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"


class LLMConfig(BaseModel):
    """Configuration for an LLM model."""

    provider: str = Field(
        ..., description="LLM provider (anthropic, openai, ollama, etc.)"
    )
    model_name: str = Field(
        ...,
        description="Specific model name (e.g., 'claude-3-5-sonnet-20241022', 'gpt-4o', 'llama2')",
    )
    api_key_env_var: Optional[str] = Field(
        None,
        description="Environment variable name containing the API key (e.g., 'ANTHROPIC_API_KEY'). Optional for local models.",
    )
    api_base: Optional[str] = Field(
        None,
        description="Base URL for the API (e.g., 'http://localhost:11434' for Ollama). Optional for cloud providers.",
    )

    @property
    def litellm_model_name(self) -> str:
        """
        Return the model name in LiteLLM format: 'provider/model_name'.

        Returns:
            Model name formatted for LiteLLM (e.g., 'anthropic/claude-3-5-sonnet-20241022')
        """
        return f"{self.provider}/{self.model_name}"
