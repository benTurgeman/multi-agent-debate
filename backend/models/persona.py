"""Persona models."""
from enum import Enum

from pydantic import BaseModel, Field


class PersonaStyle(str, Enum):
    """Debate style of a persona."""

    AGGRESSIVE = "aggressive"
    DIPLOMATIC = "diplomatic"
    ANALYTICAL = "analytical"
    SOCRATIC = "socratic"


class PersonaTemplate(BaseModel):
    """Template for a debate persona with predefined characteristics."""

    persona_id: str = Field(..., description="Unique identifier for the persona")
    name: str = Field(..., description="Display name of the persona")
    expertise: str = Field(..., description="Area of expertise or specialization")
    debate_style: PersonaStyle = Field(..., description="Debate approach style")
    description: str = Field(
        ..., description="Brief description of the persona's characteristics"
    )
    system_prompt_template: str = Field(
        ...,
        description="System prompt template with {stance} placeholder for debate position",
    )
    suggested_temperature: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Recommended LLM temperature for this persona",
    )
    suggested_max_tokens: int = Field(
        default=1024, ge=1, le=4096, description="Recommended max tokens for responses"
    )
    tags: list[str] = Field(
        default_factory=list, description="Tags for categorizing the persona"
    )


class PersonaCatalogResponse(BaseModel):
    """Response containing available persona templates."""

    personas: list[PersonaTemplate] = Field(
        ..., description="List of available persona templates"
    )
    total: int = Field(..., description="Total number of personas in the catalog")
