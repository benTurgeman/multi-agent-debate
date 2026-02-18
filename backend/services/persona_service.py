"""Persona service for loading and managing debate persona templates."""

import json
import logging
from pathlib import Path
from typing import Dict, List

from pydantic import ValidationError

from models.persona import PersonaTemplate

logger = logging.getLogger(__name__)


class PersonaService:
    """Service for managing debate persona templates."""

    def __init__(self, config_path: str | None = None):
        """
        Initialize the persona service.

        Args:
            config_path: Path to personas JSON configuration file.
                        If None, uses default path relative to this file.
        """
        if config_path is None:
            # Default path relative to this service file
            service_dir = Path(__file__).parent.parent
            config_path = str(service_dir / "config" / "personas.json")

        self.personas: Dict[str, PersonaTemplate] = {}
        self._load_personas(config_path)

    def _load_personas(self, config_path: str) -> None:
        """
        Load and validate personas from JSON configuration file.

        Args:
            config_path: Path to personas JSON file

        Raises:
            FileNotFoundError: If config file does not exist
            ValueError: If JSON is invalid or personas fail validation
        """
        config_file = Path(config_path)

        if not config_file.exists():
            logger.error(f"Personas config file not found: {config_path}")
            raise FileNotFoundError(f"Personas config file not found: {config_path}")

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                personas_data = json.load(f)

            if not isinstance(personas_data, list):
                raise ValueError("Personas config must be a JSON array")

            loaded_count = 0
            for persona_dict in personas_data:
                try:
                    persona = PersonaTemplate(**persona_dict)

                    # Check for duplicate persona_id
                    if persona.persona_id in self.personas:
                        logger.warning(
                            f"Duplicate persona_id '{persona.persona_id}' found, skipping"
                        )
                        continue

                    self.personas[persona.persona_id] = persona
                    loaded_count += 1
                except ValidationError as e:
                    logger.warning(
                        f"Invalid persona data, skipping: {persona_dict.get('persona_id', 'unknown')} - {e}"
                    )
                    continue

            logger.info(f"Loaded {loaded_count} personas from {config_path}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in personas config: {e}")
            raise ValueError(f"Invalid JSON in personas config: {e}") from e

    def list_personas(self) -> List[PersonaTemplate]:
        """
        Get all available persona templates.

        Returns:
            List of all loaded persona templates
        """
        return list(self.personas.values())

    def get_persona(self, persona_id: str) -> PersonaTemplate | None:
        """
        Get a specific persona template by ID.

        Args:
            persona_id: Unique identifier for the persona

        Returns:
            PersonaTemplate if found, None otherwise
        """
        return self.personas.get(persona_id)
