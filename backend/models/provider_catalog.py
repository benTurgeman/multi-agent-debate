"""Provider catalog models for listing available LLM providers and models."""

from typing import List, Optional

from pydantic import BaseModel, Field

from models.llm import ModelProvider


class ModelInfo(BaseModel):
    """Information about a specific LLM model."""

    model_id: str = Field(
        ..., description="Model identifier (e.g., 'claude-3-5-sonnet-20241022')"
    )
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Model description/capabilities")
    context_window: int = Field(..., description="Token context window size")
    max_output_tokens: int = Field(..., description="Maximum output tokens")
    recommended: bool = Field(
        default=False, description="Whether this is a recommended model"
    )
    pricing_tier: str = Field(
        ..., description="Pricing tier (e.g., 'standard', 'premium', 'free')"
    )


class ProviderInfo(BaseModel):
    """Information about an LLM provider."""

    provider_id: ModelProvider = Field(..., description="Provider identifier")
    display_name: str = Field(..., description="Provider display name")
    description: str = Field(..., description="Provider description")
    api_key_env_var: Optional[str] = Field(
        None,
        description="Default environment variable for API key (None for local providers)",
    )
    documentation_url: str = Field(..., description="Link to provider documentation")
    models: List[ModelInfo] = Field(
        ..., description="Available models from this provider"
    )


class ProviderCatalogResponse(BaseModel):
    """Response containing all providers and their models."""

    providers: List[ProviderInfo] = Field(..., description="List of all providers")
