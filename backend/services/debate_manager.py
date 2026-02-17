"""Debate lifecycle management and orchestration."""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Callable, Optional, Any, Dict
from enum import Enum

from models.debate import DebateState, DebateConfig, DebateStatus
from models.judge import JudgeResult, AgentScore
from models.message import Message
from services.agent_orchestrator import AgentOrchestrator
from services.llm.factory import create_llm_client
from services.prompt_builder import (
    build_judge_prompt,
    format_history_for_judge,
    create_user_message,
)
from core.exceptions import DebateExecutionError

logger = logging.getLogger(__name__)


class DebateEventType(str, Enum):
    """Types of events that can occur during a debate."""

    DEBATE_STARTED = "debate_started"
    ROUND_STARTED = "round_started"
    AGENT_THINKING = "agent_thinking"
    MESSAGE_RECEIVED = "message_received"
    TURN_COMPLETE = "turn_complete"
    ROUND_COMPLETE = "round_complete"
    JUDGING_STARTED = "judging_started"
    JUDGE_RESULT = "judge_result"
    DEBATE_COMPLETE = "debate_complete"
    ERROR = "error"


class DebateEvent:
    """Event that occurs during a debate."""

    def __init__(
        self,
        event_type: DebateEventType,
        debate_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a debate event.

        Args:
            event_type: Type of event
            debate_id: ID of the debate
            payload: Optional event payload data
        """
        self.event_type = event_type
        self.debate_id = debate_id
        self.payload = payload or {}
        self.timestamp = datetime.now(timezone.utc)


# Type alias for event callback function
EventCallback = Callable[[DebateEvent], None]


class DebateManager:
    """Manages the complete lifecycle of a debate."""

    def __init__(
        self,
        orchestrator: Optional[AgentOrchestrator] = None,
        rate_limit_delay: float = 1.0,
    ):
        """
        Initialize the debate manager.

        Args:
            orchestrator: Agent orchestrator instance (creates default if None)
            rate_limit_delay: Delay in seconds between turns for rate limiting
        """
        self.orchestrator = orchestrator or AgentOrchestrator()
        self.rate_limit_delay = rate_limit_delay
        self._event_callbacks: list[EventCallback] = []

    def register_event_callback(self, callback: EventCallback) -> None:
        """
        Register a callback function to receive debate events.

        Args:
            callback: Function to call when events occur
        """
        self._event_callbacks.append(callback)

    def _emit_event(self, event: DebateEvent) -> None:
        """
        Emit an event to all registered callbacks.

        Args:
            event: Event to emit
        """
        logger.debug(
            f"Emitting event: {event.event_type} for debate {event.debate_id}"
        )
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}", exc_info=True)

    def create_debate(self, config: DebateConfig) -> DebateState:
        """
        Create a new debate from configuration.

        Args:
            config: Debate configuration

        Returns:
            Initial debate state
        """
        debate_state = DebateState(config=config)
        logger.info(f"Created debate {debate_state.debate_id} on topic: {config.topic}")
        return debate_state

    async def run_debate(self, debate_state: DebateState) -> DebateState:
        """
        Run the complete debate lifecycle.

        Args:
            debate_state: Debate state to execute

        Returns:
            Updated debate state with results

        Raises:
            DebateExecutionError: If debate execution fails
        """
        try:
            # Mark debate as started
            debate_state.status = DebateStatus.IN_PROGRESS
            debate_state.started_at = datetime.now(timezone.utc)

            self._emit_event(
                DebateEvent(
                    event_type=DebateEventType.DEBATE_STARTED,
                    debate_id=debate_state.debate_id,
                    payload={
                        "topic": debate_state.config.topic,
                        "num_rounds": debate_state.config.num_rounds,
                        "num_agents": len(debate_state.config.agents),
                    },
                )
            )

            # Execute all rounds
            for round_num in range(1, debate_state.config.num_rounds + 1):
                await self._execute_round(debate_state, round_num)

            # Invoke judge
            judge_result = await self._invoke_judge(debate_state)
            debate_state.judge_result = judge_result

            # Mark debate as completed
            debate_state.status = DebateStatus.COMPLETED
            debate_state.completed_at = datetime.now(timezone.utc)

            self._emit_event(
                DebateEvent(
                    event_type=DebateEventType.DEBATE_COMPLETE,
                    debate_id=debate_state.debate_id,
                    payload={
                        "winner_id": judge_result.winner_id,
                        "winner_name": judge_result.winner_name,
                        "total_messages": len(debate_state.history),
                    },
                )
            )

            logger.info(
                f"Debate {debate_state.debate_id} completed. "
                f"Winner: {judge_result.winner_name}"
            )

            return debate_state

        except Exception as e:
            # Mark debate as failed
            debate_state.status = DebateStatus.FAILED
            debate_state.error_message = str(e)
            debate_state.completed_at = datetime.now(timezone.utc)

            self._emit_event(
                DebateEvent(
                    event_type=DebateEventType.ERROR,
                    debate_id=debate_state.debate_id,
                    payload={
                        "error_message": str(e),
                        "error_type": type(e).__name__,
                    },
                )
            )

            logger.error(
                f"Debate {debate_state.debate_id} failed: {e}",
                exc_info=True,
            )

            raise DebateExecutionError(
                f"Debate execution failed: {e}"
            ) from e

    async def _execute_round(
        self,
        debate_state: DebateState,
        round_num: int,
    ) -> None:
        """
        Execute a single round of the debate.

        Args:
            debate_state: Current debate state
            round_num: Round number (1-indexed)
        """
        debate_state.current_round = round_num

        self._emit_event(
            DebateEvent(
                event_type=DebateEventType.ROUND_STARTED,
                debate_id=debate_state.debate_id,
                payload={"round_number": round_num},
            )
        )

        logger.info(
            f"Starting round {round_num}/{debate_state.config.num_rounds} "
            f"for debate {debate_state.debate_id}"
        )

        # Get turn order for this round
        turn_order = self.orchestrator.get_turn_order(debate_state)

        # Execute each turn in the round
        for turn_index, agent_id in enumerate(turn_order):
            agent = debate_state.get_agent_by_id(agent_id)
            if not agent:
                raise DebateExecutionError(
                    f"Agent {agent_id} not found in debate configuration"
                )

            # Update turn counter
            debate_state.current_turn = turn_index

            # Emit agent thinking event
            self._emit_event(
                DebateEvent(
                    event_type=DebateEventType.AGENT_THINKING,
                    debate_id=debate_state.debate_id,
                    payload={
                        "agent_id": agent_id,
                        "agent_name": agent.name,
                        "round_number": round_num,
                        "turn_number": turn_index,
                    },
                )
            )

            # Execute the turn
            message = await self.orchestrator.execute_turn(debate_state, agent)

            # Add message to history
            debate_state.add_message(message)

            # Emit message received event
            self._emit_event(
                DebateEvent(
                    event_type=DebateEventType.MESSAGE_RECEIVED,
                    debate_id=debate_state.debate_id,
                    payload={
                        "message": message.model_dump(mode='json'),
                    },
                )
            )

            # Emit turn complete event
            self._emit_event(
                DebateEvent(
                    event_type=DebateEventType.TURN_COMPLETE,
                    debate_id=debate_state.debate_id,
                    payload={
                        "round_number": round_num,
                        "turn_number": turn_index,
                        "agent_id": agent_id,
                    },
                )
            )

            # Rate limiting: sleep between turns (except after last turn)
            if turn_index < len(turn_order) - 1 or round_num < debate_state.config.num_rounds:
                await asyncio.sleep(self.rate_limit_delay)

        # Emit round complete event
        self._emit_event(
            DebateEvent(
                event_type=DebateEventType.ROUND_COMPLETE,
                debate_id=debate_state.debate_id,
                payload={"round_number": round_num},
            )
        )

        logger.info(
            f"Completed round {round_num}/{debate_state.config.num_rounds} "
            f"for debate {debate_state.debate_id}"
        )

    async def _invoke_judge(self, debate_state: DebateState) -> JudgeResult:
        """
        Invoke the judge to evaluate the debate.

        Args:
            debate_state: Completed debate state

        Returns:
            Judge's evaluation and scores

        Raises:
            DebateExecutionError: If judge invocation fails
        """
        self._emit_event(
            DebateEvent(
                event_type=DebateEventType.JUDGING_STARTED,
                debate_id=debate_state.debate_id,
                payload={"total_messages": len(debate_state.history)},
            )
        )

        logger.info(f"Invoking judge for debate {debate_state.debate_id}")

        try:
            # Create LLM client for judge
            judge_config = debate_state.config.judge_config
            llm_client = create_llm_client(judge_config.llm_config)

            # Build judge prompt
            system_prompt = build_judge_prompt(
                topic=debate_state.config.topic,
                agents=debate_state.config.agents,
                judge_config=judge_config,
            )

            # Format complete history for judge
            history_context = format_history_for_judge(
                history=debate_state.history,
                topic=debate_state.config.topic,
            )

            # Call judge LLM
            response_text = await llm_client.send_message(
                system_prompt=system_prompt,
                messages=[create_user_message(history_context)],
                temperature=judge_config.temperature,
                max_tokens=judge_config.max_tokens,
            )

            # Parse judge response
            judge_result = self._parse_judge_response(
                response_text, debate_state.config.agents
            )

            self._emit_event(
                DebateEvent(
                    event_type=DebateEventType.JUDGE_RESULT,
                    debate_id=debate_state.debate_id,
                    payload={"judge_result": judge_result.model_dump(mode='json')},
                )
            )

            logger.info(
                f"Judge evaluation complete for debate {debate_state.debate_id}. "
                f"Winner: {judge_result.winner_name}"
            )

            return judge_result

        except Exception as e:
            error_msg = f"Failed to invoke judge: {e}"
            logger.error(error_msg, exc_info=True)
            raise DebateExecutionError(error_msg) from e

    def _parse_judge_response(
        self, response_text: str, agents: list
    ) -> JudgeResult:
        """
        Parse the judge's response into a JudgeResult.

        Args:
            response_text: Raw response from judge LLM
            agents: List of agents in the debate

        Returns:
            Parsed JudgeResult

        Raises:
            DebateExecutionError: If parsing fails
        """
        try:
            # Try to extract JSON from the response
            # Look for JSON block in markdown code fence or raw JSON
            response_text = response_text.strip()

            # Remove markdown code fences if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]

            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            judge_data = json.loads(response_text)

            # Validate and create JudgeResult
            judge_result = JudgeResult(**judge_data)

            return judge_result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse judge JSON response: {e}")
            logger.debug(f"Raw judge response: {response_text}")

            # Fallback: create a basic result with equal scores
            fallback_scores = [
                AgentScore(
                    agent_id=agent.agent_id,
                    agent_name=agent.name,
                    score=5.0,
                    reasoning="Unable to parse judge response. Default score assigned.",
                )
                for agent in agents
            ]

            return JudgeResult(
                summary=f"Judge evaluation failed to parse. Raw response: {response_text[:200]}...",
                agent_scores=fallback_scores,
                winner_id=agents[0].agent_id,
                winner_name=agents[0].name,
                key_arguments=["Unable to extract key arguments"],
            )

        except Exception as e:
            error_msg = f"Error parsing judge response: {e}"
            logger.error(error_msg, exc_info=True)
            raise DebateExecutionError(error_msg) from e
