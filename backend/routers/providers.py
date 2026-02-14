"""REST API endpoints for provider catalog management."""

from fastapi import APIRouter

from models.provider_catalog import ProviderCatalogResponse
from services.provider_catalog import get_provider_catalog

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("", response_model=ProviderCatalogResponse)
async def list_providers() -> ProviderCatalogResponse:
    """
    Get all available LLM providers and their models.

    Returns a curated catalog of supported providers (Anthropic, OpenAI)
    with detailed information about each available model including
    context windows, output limits, and recommendations.

    Returns:
        Complete catalog of providers and models with metadata
    """
    providers = get_provider_catalog()
    return ProviderCatalogResponse(providers=providers)
