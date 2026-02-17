"""REST API endpoints for persona catalog management."""

from fastapi import APIRouter

from models.persona import PersonaCatalogResponse
from services.persona_service import PersonaService

router = APIRouter(prefix="/api/personas", tags=["personas"])

# Initialize persona service singleton
persona_service = PersonaService()


@router.get("", response_model=PersonaCatalogResponse)
async def list_personas() -> PersonaCatalogResponse:
    """
    Get all available persona templates.

    Returns a catalog of preconfigured debate personas with distinct
    archetypes (Socratic Philosopher, Trial Lawyer, Data Scientist, etc.).
    Each persona includes expertise, debate style, and prompt templates.

    Returns:
        Complete catalog of persona templates with metadata
    """
    personas = persona_service.list_personas()
    return PersonaCatalogResponse(personas=personas, total=len(personas))
