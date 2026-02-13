"""Agent orchestration for debate turn management."""
import asyncio
import logging
from typing import Optional, List

from models.agent import AgentConfig
from models.debate import DebateState
from models.message import Message
from services.llm.factory import create_llm_client
from services.prompt_builder import (
    build_debater_prompt,
    format_history_for_context,
    create_user_message,
)
from core.exceptions import DebateExecutionError

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates agent turns in a debate."""

    def __init__(self, max_turn_retries: int = 3):
        """
        Initialize the agent orchestrator.

        Args:
            max_turn_retries: Maximum retry attempts for a single turn
        """
        self.max_turn_retries = max_turn_retries

    def get_next_agent(self, debate_state: DebateState) -> AgentConfig:
        """
        Determine which agent should speak next.

        Args:
            debate_state: Current debate state

        Returns:
            AgentConfig for the next speaker

        Raises:
            DebateExecutionError: If unable to determine next agent
        """
        num_agents = len(debate_state.config.agents)
        if num_agents == 0:
            raise DebateExecutionError("No agents configured for debate")

        # Calculate which agent's turn it is based on current turn number
        agent_index = debate_state.current_turn % num_agents
        return debate_state.config.agents[agent_index]

    async def execute_turn(
        self,
        debate_state: DebateState,
        agent: AgentConfig,
    ) -> Message:
        """
        Execute a single turn for an agent with retry logic.

        Args:
            debate_state: Current debate state
            agent: Agent to execute turn for

        Returns:
            Message containing the agent's response

        Raises:
            DebateExecutionError: If turn fails after all retry attempts
        """
        attempt = 0
        last_exception = None

        while attempt < self.max_turn_retries:
            try:
                logger.info(
                    f"Executing turn for agent {agent.agent_id} "
                    f"(attempt {attempt + 1}/{self.max_turn_retries})"
                )

                # Create LLM client for this agent's model
                llm_client = create_llm_client(agent.llm_config)

                # Build system prompt
                system_prompt = build_debater_prompt(
                    agent=agent,
                    topic=debate_state.config.topic,
                    current_round=debate_state.current_round,
                    total_rounds=debate_state.config.num_rounds,
                )

                # Format history as context
                history_context = format_history_for_context(
                    history=debate_state.history,
                    topic=debate_state.config.topic,
                    current_round=debate_state.current_round,
                    total_rounds=debate_state.config.num_rounds,
                )

                # Call LLM
                response_text = await llm_client.send_message(
                    system_prompt=system_prompt,
                    messages=[create_user_message(history_context)],
                    temperature=agent.temperature,
                    max_tokens=agent.max_tokens,
                )

                # Create message object
                message = Message(
                    agent_id=agent.agent_id,
                    agent_name=agent.name,
                    content=response_text,
                    round_number=debate_state.current_round,
                    turn_number=debate_state.current_turn,
                    stance=agent.stance,
                )

                logger.info(
                    f"Successfully executed turn for agent {agent.agent_id} "
                    f"(round {debate_state.current_round}, turn {debate_state.current_turn})"
                )

                return message

            except Exception as e:
                attempt += 1
                last_exception = e
                logger.warning(
                    f"Turn execution failed for agent {agent.agent_id} "
                    f"(attempt {attempt}/{self.max_turn_retries}): {e}"
                )

                if attempt < self.max_turn_retries:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)

        # All retries exhausted
        error_msg = (
            f"Failed to execute turn for agent {agent.agent_id} "
            f"after {self.max_turn_retries} attempts. Last error: {last_exception}"
        )
        logger.error(error_msg)
        raise DebateExecutionError(error_msg) from last_exception

    def get_turn_order(self, debate_state: DebateState) -> List[str]:
        """
        Get the list of agent IDs in turn order.

        Args:
            debate_state: Current debate state

        Returns:
            List of agent IDs in the order they should speak
        """
        return [agent.agent_id for agent in debate_state.config.agents]

    def calculate_total_turns(self, debate_state: DebateState) -> int:
        """
        Calculate total number of turns in the debate.

        Args:
            debate_state: Debate state

        Returns:
            Total number of turns (rounds * number of agents)
        """
        num_agents = len(debate_state.config.agents)
        return debate_state.config.num_rounds * num_agents
