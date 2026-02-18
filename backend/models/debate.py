"""Debate models and state management."""
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from models.agent import AgentConfig
from models.judge import JudgeResult
from models.message import Message


class DebateStatus(str, Enum):
    """Status of a debate."""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class DebateConfig(BaseModel):
    """Configuration for a debate."""

    topic: str = Field(..., description="Debate topic or proposition")
    num_rounds: int = Field(..., ge=1, description="Number of debate rounds")
    agents: List[AgentConfig] = Field(
        ..., min_length=2, description="List of participating agents (minimum 2)"
    )
    judge_config: AgentConfig = Field(..., description="Judge agent configuration")

    @field_validator("agents")
    @classmethod
    def validate_minimum_agents(cls, v: List[AgentConfig]) -> List[AgentConfig]:
        """
        Validate that there are at least 2 agents.

        Args:
            v: List of agents

        Returns:
            Validated list of agents

        Raises:
            ValueError: If fewer than 2 agents
        """
        if len(v) < 2:
            raise ValueError("At least 2 agents are required for a debate")
        return v

    @field_validator("agents")
    @classmethod
    def validate_unique_agent_ids(cls, v: List[AgentConfig]) -> List[AgentConfig]:
        """
        Validate that all agent IDs are unique.

        Args:
            v: List of agents

        Returns:
            Validated list of agents

        Raises:
            ValueError: If duplicate agent IDs exist
        """
        agent_ids = [agent.agent_id for agent in v]
        if len(agent_ids) != len(set(agent_ids)):
            raise ValueError("All agent IDs must be unique")
        return v


class DebateState(BaseModel):
    """Current state of a debate."""

    debate_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique debate ID"
    )
    config: DebateConfig = Field(..., description="Debate configuration")
    status: DebateStatus = Field(
        default=DebateStatus.CREATED, description="Current debate status"
    )
    current_round: int = Field(default=0, ge=0, description="Current round number")
    current_turn: int = Field(default=0, ge=0, description="Current turn number")
    history: List[Message] = Field(
        default_factory=list, description="Complete message history"
    )
    judge_result: Optional[JudgeResult] = Field(
        default=None, description="Final judge result (after completion)"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if debate failed"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the debate was created",
    )
    started_at: Optional[datetime] = Field(
        default=None, description="When the debate started"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="When the debate completed"
    )

    def add_message(self, message: Message) -> None:
        """
        Add a message to the debate history.

        Args:
            message: Message to add
        """
        self.history.append(message)

    def get_agent_by_id(self, agent_id: str) -> Optional[AgentConfig]:
        """
        Get an agent configuration by ID.

        Args:
            agent_id: Agent ID to search for

        Returns:
            AgentConfig if found, None otherwise
        """
        for agent in self.config.agents:
            if agent.agent_id == agent_id:
                return agent
        return None
