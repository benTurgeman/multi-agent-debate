"""REST API endpoints for debate management."""
import asyncio
import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import PlainTextResponse

from core.exceptions import DebateNotFoundError, StorageError
from models.api import (
    CreateDebateRequest,
    CreateDebateResponse,
    DebateListResponse,
    DebateResponse,
    StartDebateResponse,
    DebateStatusResponse,
    ErrorResponse,
)
from models.debate import DebateStatus
from services.debate_manager import DebateManager
from storage.memory_store import get_debate_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/debates", tags=["debates"])

# Global debate manager instance
_debate_manager: DebateManager | None = None


def get_debate_manager() -> DebateManager:
    """Get or create the global debate manager instance."""
    global _debate_manager
    if _debate_manager is None:
        _debate_manager = DebateManager()
    return _debate_manager


@router.post(
    "",
    response_model=CreateDebateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
async def create_debate(request: CreateDebateRequest) -> CreateDebateResponse:
    """
    Create a new debate.

    Args:
        request: Debate configuration

    Returns:
        Debate creation response with debate ID

    Raises:
        HTTPException: If debate creation fails
    """
    try:
        debate_manager = get_debate_manager()
        store = get_debate_store()

        # Create debate state
        debate_state = debate_manager.create_debate(request.config)

        # Store in database
        await store.create(debate_state)

        logger.info(f"Created debate {debate_state.debate_id}")

        return CreateDebateResponse(
            debate_id=debate_state.debate_id,
            status=debate_state.status,
            message="Debate created successfully",
        )

    except StorageError as e:
        logger.error(f"Storage error creating debate: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating debate: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create debate: {str(e)}",
        )


@router.get(
    "",
    response_model=DebateListResponse,
    responses={500: {"model": ErrorResponse}},
)
async def list_debates() -> DebateListResponse:
    """
    List all debates.

    Returns:
        List of all debates with their current state
    """
    try:
        store = get_debate_store()
        debates = await store.list_all()

        logger.info(f"Retrieved {len(debates)} debates")

        return DebateListResponse(
            debates=debates,
            total=len(debates),
        )

    except Exception as e:
        logger.error(f"Error listing debates: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list debates: {str(e)}",
        )


@router.get(
    "/{debate_id}",
    response_model=DebateResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_debate(debate_id: str) -> DebateResponse:
    """
    Get a specific debate by ID.

    Args:
        debate_id: Debate ID

    Returns:
        Complete debate state

    Raises:
        HTTPException: If debate not found
    """
    try:
        store = get_debate_store()
        debate = await store.get(debate_id)

        return DebateResponse(debate=debate)

    except DebateNotFoundError as e:
        logger.warning(f"Debate not found: {debate_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error retrieving debate {debate_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve debate: {str(e)}",
        )


async def _run_debate_background(debate_id: str) -> None:
    """
    Background task to run a debate.

    Args:
        debate_id: ID of the debate to run
    """
    try:
        store = get_debate_store()
        debate_manager = get_debate_manager()

        # Get debate state
        debate_state = await store.get(debate_id)

        # Run the debate
        updated_state = await debate_manager.run_debate(debate_state)

        # Update storage
        await store.update(updated_state)

        logger.info(f"Debate {debate_id} completed successfully")

    except Exception as e:
        logger.error(f"Error running debate {debate_id}: {e}", exc_info=True)
        # Try to update debate status to failed
        try:
            store = get_debate_store()
            debate_state = await store.get(debate_id)
            debate_state.status = DebateStatus.FAILED
            debate_state.error_message = str(e)
            await store.update(debate_state)
        except Exception as update_error:
            logger.error(f"Failed to update debate status: {update_error}")


@router.post(
    "/{debate_id}/start",
    response_model=StartDebateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
async def start_debate(
    debate_id: str, background_tasks: BackgroundTasks
) -> StartDebateResponse:
    """
    Start debate execution in the background.

    Args:
        debate_id: Debate ID
        background_tasks: FastAPI background tasks

    Returns:
        Response indicating debate has been started

    Raises:
        HTTPException: If debate not found or already running
    """
    try:
        store = get_debate_store()

        # Get debate state
        debate_state = await store.get(debate_id)

        # Check if debate is in a valid state to start
        if debate_state.status == DebateStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debate is already in progress",
            )
        elif debate_state.status == DebateStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debate has already completed",
            )

        # Schedule debate execution as background task
        background_tasks.add_task(_run_debate_background, debate_id)

        logger.info(f"Started debate execution for {debate_id}")

        return StartDebateResponse(
            debate_id=debate_id,
            status=DebateStatus.IN_PROGRESS,
            message="Debate execution started. Connect to WebSocket for real-time updates.",
        )

    except DebateNotFoundError as e:
        logger.warning(f"Debate not found: {debate_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting debate {debate_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start debate: {str(e)}",
        )


@router.get(
    "/{debate_id}/status",
    response_model=DebateStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_debate_status(debate_id: str) -> DebateStatusResponse:
    """
    Get current status of a debate.

    Args:
        debate_id: Debate ID

    Returns:
        Current debate status information

    Raises:
        HTTPException: If debate not found
    """
    try:
        store = get_debate_store()
        debate = await store.get(debate_id)

        return DebateStatusResponse(
            debate_id=debate.debate_id,
            status=debate.status,
            current_round=debate.current_round,
            current_turn=debate.current_turn,
            total_rounds=debate.config.num_rounds,
            message_count=len(debate.history),
        )

    except DebateNotFoundError as e:
        logger.warning(f"Debate not found: {debate_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error retrieving debate status {debate_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve debate status: {str(e)}",
        )


@router.get(
    "/{debate_id}/export",
    responses={404: {"model": ErrorResponse}},
)
async def export_debate(
    debate_id: str,
    format: Literal["json", "markdown", "text"] = "json",
):
    """
    Export debate transcript in various formats.

    Args:
        debate_id: Debate ID
        format: Export format (json, markdown, or text)

    Returns:
        Debate transcript in requested format

    Raises:
        HTTPException: If debate not found
    """
    try:
        store = get_debate_store()
        debate = await store.get(debate_id)

        if format == "json":
            # Return full debate state as JSON
            return DebateResponse(debate=debate)

        elif format == "markdown":
            # Generate markdown format
            content = _export_markdown(debate)
            return PlainTextResponse(content=content, media_type="text/markdown")

        elif format == "text":
            # Generate plain text format
            content = _export_text(debate)
            return PlainTextResponse(content=content, media_type="text/plain")

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {format}",
            )

    except DebateNotFoundError as e:
        logger.warning(f"Debate not found: {debate_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting debate {debate_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export debate: {str(e)}",
        )


@router.delete(
    "/{debate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
async def delete_debate(debate_id: str) -> None:
    """
    Delete a debate.

    Args:
        debate_id: Debate ID

    Raises:
        HTTPException: If debate not found
    """
    try:
        store = get_debate_store()
        await store.delete(debate_id)

        logger.info(f"Deleted debate {debate_id}")

    except DebateNotFoundError as e:
        logger.warning(f"Debate not found: {debate_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error deleting debate {debate_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete debate: {str(e)}",
        )


def _export_markdown(debate) -> str:
    """
    Export debate to Markdown format.

    Args:
        debate: DebateState object

    Returns:
        Markdown formatted string
    """
    lines = []

    # Header
    lines.append(f"# Debate: {debate.config.topic}")
    lines.append("")
    lines.append(f"**Date:** {debate.created_at.isoformat()}")
    lines.append(f"**Rounds:** {debate.config.num_rounds}")
    lines.append(f"**Status:** {debate.status.value}")
    lines.append("")

    # Participants
    lines.append("## Participants")
    lines.append("")
    for agent in debate.config.agents:
        lines.append(f"- **{agent.name}** ({agent.stance})")
        lines.append(f"  - Model: {agent.llm_config.provider.value}/{agent.llm_config.model_name}")
        lines.append(f"  - Role: {agent.role.value}")
    lines.append("")

    # Debate Transcript
    lines.append("## Debate Transcript")
    lines.append("")

    current_round = 0
    for message in debate.history:
        if message.round_number != current_round:
            current_round = message.round_number
            lines.append(f"### Round {current_round}")
            lines.append("")

        lines.append(f"**{message.agent_name} ({message.stance}):**")
        lines.append("")
        lines.append(message.content)
        lines.append("")

    # Judge's Decision
    if debate.judge_result:
        lines.append("## Judge's Decision")
        lines.append("")
        lines.append(f"**Winner:** {debate.judge_result.winner_name}")
        lines.append("")
        lines.append(f"### Summary")
        lines.append("")
        lines.append(debate.judge_result.summary)
        lines.append("")

        lines.append("### Scores")
        lines.append("")
        for score in debate.judge_result.agent_scores:
            lines.append(f"- **{score.agent_name}:** {score.score}/10")
            lines.append(f"  - {score.reasoning}")
            lines.append("")

        if debate.judge_result.key_arguments:
            lines.append("### Key Arguments")
            lines.append("")
            for arg in debate.judge_result.key_arguments:
                lines.append(f"- {arg}")
            lines.append("")

    return "\n".join(lines)


def _export_text(debate) -> str:
    """
    Export debate to plain text format.

    Args:
        debate: DebateState object

    Returns:
        Plain text formatted string
    """
    lines = []

    # Header
    lines.append(f"DEBATE: {debate.config.topic}")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Date: {debate.created_at.isoformat()}")
    lines.append(f"Rounds: {debate.config.num_rounds}")
    lines.append(f"Status: {debate.status.value}")
    lines.append("")

    # Participants
    lines.append("PARTICIPANTS:")
    lines.append("-" * 80)
    for agent in debate.config.agents:
        lines.append(f"{agent.name} ({agent.stance})")
        lines.append(f"  Model: {agent.llm_config.provider.value}/{agent.llm_config.model_name}")
        lines.append(f"  Role: {agent.role.value}")
    lines.append("")

    # Debate Transcript
    lines.append("DEBATE TRANSCRIPT:")
    lines.append("-" * 80)
    lines.append("")

    current_round = 0
    for message in debate.history:
        if message.round_number != current_round:
            current_round = message.round_number
            lines.append(f"\nROUND {current_round}")
            lines.append("-" * 40)
            lines.append("")

        lines.append(f"{message.agent_name} ({message.stance}):")
        lines.append("")
        lines.append(message.content)
        lines.append("")

    # Judge's Decision
    if debate.judge_result:
        lines.append("JUDGE'S DECISION:")
        lines.append("-" * 80)
        lines.append("")
        lines.append(f"Winner: {debate.judge_result.winner_name}")
        lines.append("")
        lines.append("Summary:")
        lines.append(debate.judge_result.summary)
        lines.append("")

        lines.append("Scores:")
        for score in debate.judge_result.agent_scores:
            lines.append(f"  {score.agent_name}: {score.score}/10")
            lines.append(f"    {score.reasoning}")
            lines.append("")

        if debate.judge_result.key_arguments:
            lines.append("Key Arguments:")
            for arg in debate.judge_result.key_arguments:
                lines.append(f"  - {arg}")
            lines.append("")

    return "\n".join(lines)
