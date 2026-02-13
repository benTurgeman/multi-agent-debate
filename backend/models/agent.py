"""Agent models."""
from enum import Enum

from pydantic import BaseModel, Field

from models.llm import LLMConfig


class AgentRole(str, Enum):
    """Role of an agent in the debate."""

    DEBATER = "debater"
    JUDGE = "judge"


class AgentConfig(BaseModel):
    """Configuration for a debate agent."""

    agent_id: str = Field(..., description="Unique identifier for the agent")
    llm_config: LLMConfig = Field(..., description="LLM model configuration")
    role: AgentRole = Field(..., description="Agent role (debater or judge)")
    name: str = Field(..., description="Display name for the agent")
    stance: str = Field(
        ..., description="Agent's stance or position (e.g., 'Pro', 'Con', 'Neutral')"
    )
    system_prompt: str = Field(
        ..., description="Custom system prompt defining agent's persona and behavior"
    )
    temperature: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="LLM temperature parameter (0.0-2.0)",
    )
    max_tokens: int = Field(
        default=1024, ge=1, le=4096, description="Maximum tokens in response"
    )
