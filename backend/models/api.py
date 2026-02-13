"""API request and response models."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from models.debate import DebateConfig, DebateState, DebateStatus
from models.judge import JudgeResult
from models.message import Message


# Request schemas
class CreateDebateRequest(BaseModel):
    """Request to create a new debate."""

    config: DebateConfig = Field(..., description="Debate configuration")


class StartDebateRequest(BaseModel):
    """Request to start a debate (can be empty)."""

    pass


# Response schemas
class CreateDebateResponse(BaseModel):
    """Response after creating a debate."""

    debate_id: str = Field(..., description="Unique debate ID")
    status: DebateStatus = Field(..., description="Current debate status")
    message: str = Field(default="Debate created successfully")


class DebateResponse(BaseModel):
    """Response containing debate state."""

    debate: DebateState = Field(..., description="Complete debate state")


class DebateListResponse(BaseModel):
    """Response containing list of debates."""

    debates: List[DebateState] = Field(..., description="List of all debates")
    total: int = Field(..., description="Total number of debates")


class StartDebateResponse(BaseModel):
    """Response after starting a debate."""

    debate_id: str = Field(..., description="Debate ID")
    status: DebateStatus = Field(..., description="Current debate status")
    message: str = Field(
        default="Debate execution started. Connect to WebSocket for real-time updates."
    )


class DebateStatusResponse(BaseModel):
    """Response containing current debate status."""

    debate_id: str = Field(..., description="Debate ID")
    status: DebateStatus = Field(..., description="Current debate status")
    current_round: int = Field(..., description="Current round number")
    current_turn: int = Field(..., description="Current turn number")
    total_rounds: int = Field(..., description="Total number of rounds")
    message_count: int = Field(..., description="Number of messages so far")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


# WebSocket message types
class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    type: str = Field(..., description="Message type")
    payload: Dict[str, Any] = Field(
        default_factory=dict, description="Message payload"
    )
    timestamp: str = Field(..., description="Message timestamp (ISO format)")


class DebateStartedEvent(BaseModel):
    """Event: Debate has started."""

    debate_id: str
    topic: str
    num_rounds: int
    num_agents: int


class RoundStartedEvent(BaseModel):
    """Event: New round has started."""

    debate_id: str
    round_number: int
    total_rounds: int


class AgentThinkingEvent(BaseModel):
    """Event: Agent is preparing response."""

    debate_id: str
    agent_id: str
    agent_name: str
    round_number: int
    turn_number: int


class MessageReceivedEvent(BaseModel):
    """Event: Agent response received."""

    debate_id: str
    message: Message


class TurnCompleteEvent(BaseModel):
    """Event: Turn completed."""

    debate_id: str
    round_number: int
    turn_number: int


class RoundCompleteEvent(BaseModel):
    """Event: Round completed."""

    debate_id: str
    round_number: int


class JudgingStartedEvent(BaseModel):
    """Event: Judge evaluation started."""

    debate_id: str


class JudgeResultEvent(BaseModel):
    """Event: Judge result received."""

    debate_id: str
    result: JudgeResult


class DebateCompleteEvent(BaseModel):
    """Event: Debate completed."""

    debate_id: str
    winner_id: str
    winner_name: str


class DebateErrorEvent(BaseModel):
    """Event: Error occurred."""

    debate_id: str
    error_message: str
    context: Optional[str] = None
