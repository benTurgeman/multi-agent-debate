"""Tests for persona service and API endpoints."""
import json
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from main import app
from models.persona import PersonaStyle, PersonaTemplate
from services.persona_service import PersonaService


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def personas_config_path() -> str:
    """Get path to personas config file."""
    return str(Path(__file__).parent.parent / "config" / "personas.json")


@pytest.fixture
def temp_personas_file(tmp_path) -> Path:
    """Create a temporary personas JSON file for testing."""
    personas_data = [
        {
            "persona_id": "test-philosopher",
            "name": "Test Philosopher",
            "expertise": "Logic and Testing",
            "debate_style": "socratic",
            "description": "A test persona for unit testing",
            "system_prompt_template": "Test prompt with {stance}",
            "suggested_temperature": 0.7,
            "suggested_max_tokens": 1024,
            "tags": ["test", "philosophy"],
        },
        {
            "persona_id": "test-scientist",
            "name": "Test Scientist",
            "expertise": "Data Analysis",
            "debate_style": "analytical",
            "description": "Another test persona",
            "system_prompt_template": "Science prompt {stance}",
            "suggested_temperature": 0.5,
            "suggested_max_tokens": 1200,
            "tags": ["science", "test"],
        },
    ]

    personas_file = tmp_path / "personas.json"
    with open(personas_file, "w", encoding="utf-8") as f:
        json.dump(personas_data, f)

    return personas_file


class TestPersonaService:
    """Test PersonaService class."""

    def test_load_personas_from_file(self, temp_personas_file):
        """Test loading personas from JSON file."""
        service = PersonaService(config_path=str(temp_personas_file))

        assert len(service.personas) == 2
        assert "test-philosopher" in service.personas
        assert "test-scientist" in service.personas

    def test_load_personas_with_default_path(self, personas_config_path):
        """Test loading personas from default config path."""
        service = PersonaService()

        personas = service.list_personas()
        assert len(personas) >= 8  # Should have at least 8 starter personas
        assert all(isinstance(p, PersonaTemplate) for p in personas)

    def test_list_personas(self, temp_personas_file):
        """Test listing all personas."""
        service = PersonaService(config_path=str(temp_personas_file))
        personas = service.list_personas()

        assert len(personas) == 2
        assert all(isinstance(p, PersonaTemplate) for p in personas)

    def test_get_persona_by_id(self, temp_personas_file):
        """Test getting specific persona by ID."""
        service = PersonaService(config_path=str(temp_personas_file))

        persona = service.get_persona("test-philosopher")
        assert persona is not None
        assert persona.persona_id == "test-philosopher"
        assert persona.name == "Test Philosopher"
        assert persona.expertise == "Logic and Testing"
        assert persona.debate_style == PersonaStyle.SOCRATIC

    def test_get_nonexistent_persona(self, temp_personas_file):
        """Test getting persona that doesn't exist."""
        service = PersonaService(config_path=str(temp_personas_file))

        persona = service.get_persona("nonexistent")
        assert persona is None

    def test_load_invalid_json(self, tmp_path):
        """Test handling of invalid JSON file."""
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        with pytest.raises(ValueError, match="Invalid JSON"):
            PersonaService(config_path=str(invalid_file))

    def test_load_missing_file(self):
        """Test handling of missing config file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            PersonaService(config_path="/nonexistent/path.json")

    def test_skip_invalid_persona(self, tmp_path):
        """Test that invalid personas are skipped with warning."""
        personas_data = [
            {
                "persona_id": "valid-persona",
                "name": "Valid Persona",
                "expertise": "Testing",
                "debate_style": "analytical",
                "description": "Valid persona",
                "system_prompt_template": "Prompt {stance}",
                "suggested_temperature": 0.7,
                "suggested_max_tokens": 1024,
                "tags": ["test"],
            },
            {
                # Missing required fields - should be skipped
                "persona_id": "invalid-persona",
                "name": "Invalid",
            },
        ]

        personas_file = tmp_path / "mixed.json"
        with open(personas_file, "w", encoding="utf-8") as f:
            json.dump(personas_data, f)

        service = PersonaService(config_path=str(personas_file))

        # Should load only the valid persona
        assert len(service.personas) == 1
        assert "valid-persona" in service.personas
        assert "invalid-persona" not in service.personas

    def test_duplicate_persona_id(self, tmp_path):
        """Test that duplicate persona IDs are handled."""
        personas_data = [
            {
                "persona_id": "duplicate",
                "name": "First",
                "expertise": "Testing",
                "debate_style": "analytical",
                "description": "First persona",
                "system_prompt_template": "Prompt {stance}",
                "suggested_temperature": 0.7,
                "suggested_max_tokens": 1024,
                "tags": [],
            },
            {
                "persona_id": "duplicate",
                "name": "Second",
                "expertise": "Testing",
                "debate_style": "socratic",
                "description": "Second persona",
                "system_prompt_template": "Different prompt {stance}",
                "suggested_temperature": 0.5,
                "suggested_max_tokens": 512,
                "tags": [],
            },
        ]

        personas_file = tmp_path / "duplicates.json"
        with open(personas_file, "w", encoding="utf-8") as f:
            json.dump(personas_data, f)

        service = PersonaService(config_path=str(personas_file))

        # Should keep only the first occurrence
        assert len(service.personas) == 1
        assert service.personas["duplicate"].name == "First"


class TestPersonasAPI:
    """Test /api/personas endpoints."""

    def test_list_personas_endpoint(self, client):
        """Test GET /api/personas returns personas catalog."""
        response = client.get("/api/personas")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "personas" in data
        assert "total" in data
        assert isinstance(data["personas"], list)
        assert data["total"] == len(data["personas"])

        # Verify we have at least 8 starter personas
        assert len(data["personas"]) >= 8

    def test_personas_have_required_fields(self, client):
        """Test that all personas have required fields."""
        response = client.get("/api/personas")
        assert response.status_code == 200

        personas = response.json()["personas"]

        required_fields = [
            "persona_id",
            "name",
            "expertise",
            "debate_style",
            "description",
            "system_prompt_template",
            "suggested_temperature",
            "suggested_max_tokens",
            "tags",
        ]

        for persona in personas:
            for field in required_fields:
                assert (
                    field in persona
                ), f"Missing field {field} in persona {persona.get('name', 'unknown')}"

    def test_persona_ids_are_unique(self, client):
        """Test that all persona IDs are unique."""
        response = client.get("/api/personas")
        assert response.status_code == 200

        personas = response.json()["personas"]
        persona_ids = [p["persona_id"] for p in personas]

        # Check for uniqueness
        assert len(persona_ids) == len(set(persona_ids)), "Duplicate persona_id found"

    def test_system_prompt_templates_have_stance_placeholder(self, client):
        """Test that all system prompt templates include {stance} placeholder."""
        response = client.get("/api/personas")
        assert response.status_code == 200

        personas = response.json()["personas"]

        for persona in personas:
            template = persona["system_prompt_template"]
            assert (
                "{stance}" in template
            ), f"Persona {persona['name']} missing {{stance}} placeholder"

    def test_personas_have_valid_debate_styles(self, client):
        """Test that all personas have valid debate styles."""
        response = client.get("/api/personas")
        assert response.status_code == 200

        personas = response.json()["personas"]
        valid_styles = ["aggressive", "diplomatic", "analytical", "socratic"]

        for persona in personas:
            assert (
                persona["debate_style"] in valid_styles
            ), f"Invalid debate_style for {persona['name']}: {persona['debate_style']}"

    def test_suggested_parameters_are_valid(self, client):
        """Test that suggested parameters are within valid ranges."""
        response = client.get("/api/personas")
        assert response.status_code == 200

        personas = response.json()["personas"]

        for persona in personas:
            # Temperature should be between 0 and 2
            assert (
                0.0 <= persona["suggested_temperature"] <= 2.0
            ), f"Invalid temperature for {persona['name']}"

            # Max tokens should be reasonable
            assert (
                1 <= persona["suggested_max_tokens"] <= 4096
            ), f"Invalid max_tokens for {persona['name']}"


class TestPersonaCatalogIntegrity:
    """Test the integrity of the actual personas.json catalog."""

    def test_all_starter_personas_exist(self, client):
        """Test that all 8 expected starter personas are present."""
        response = client.get("/api/personas")
        assert response.status_code == 200

        personas = response.json()["personas"]
        persona_names = {p["name"] for p in personas}

        expected_personas = {
            "Socratic Philosopher",
            "Data Scientist",
            "Trial Lawyer",
            "Academic Researcher",
            "Political Strategist",
            "Entrepreneur",
            "Ethicist",
            "Investigative Journalist",
        }

        for expected_name in expected_personas:
            assert (
                expected_name in persona_names
            ), f"Missing expected persona: {expected_name}"

    def test_personas_have_meaningful_descriptions(self, client):
        """Test that personas have non-empty descriptions."""
        response = client.get("/api/personas")
        assert response.status_code == 200

        personas = response.json()["personas"]

        for persona in personas:
            assert (
                len(persona["description"]) > 10
            ), f"Persona {persona['name']} has insufficient description"
            assert (
                len(persona["expertise"]) > 0
            ), f"Persona {persona['name']} missing expertise"
            assert (
                len(persona["system_prompt_template"]) > 50
            ), f"Persona {persona['name']} has insufficient prompt template"
