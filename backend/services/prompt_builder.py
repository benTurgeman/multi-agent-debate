"""Prompt building utilities for debate agents."""
from typing import List, Dict

from models.agent import AgentConfig
from models.message import Message


def build_debater_prompt(
    agent: AgentConfig,
    topic: str,
    current_round: int,
    total_rounds: int,
) -> str:
    """
    Build system prompt for a debater agent.

    Args:
        agent: Agent configuration
        topic: Debate topic
        current_round: Current round number
        total_rounds: Total number of rounds

    Returns:
        Complete system prompt for the agent
    """
    system_prompt = f"""{agent.system_prompt}

DEBATE CONTEXT:
- Topic: {topic}
- Your stance: {agent.stance}
- Current round: {current_round} of {total_rounds}

INSTRUCTIONS:
- Present clear arguments supporting your position
- Respond to opposing arguments from previous turns
- Maintain your persona and debate style
- Be persuasive but respectful
- Aim for 200-400 words per response
"""
    return system_prompt.strip()


def build_judge_prompt(
    topic: str,
    agents: List[AgentConfig],
    judge_config: AgentConfig,
) -> str:
    """
    Build system prompt for the judge agent.

    Args:
        topic: Debate topic
        agents: List of debater agents
        judge_config: Judge agent configuration

    Returns:
        Complete system prompt for the judge
    """
    # Build participant list with stances
    participants_info = []
    for agent in agents:
        participants_info.append(f"- {agent.name} ({agent.stance})")
    participants_str = "\n".join(participants_info)

    system_prompt = f"""{judge_config.system_prompt}

DEBATE TOPIC: {topic}

PARTICIPANTS:
{participants_str}

TASK:
1. Score each participant 0-10 on: argument quality, logic, evidence, rebuttals, persuasiveness
2. Provide detailed reasoning for each score
3. Identify key arguments from each side
4. Declare the winner (highest score)

Respond in JSON format:
{{
  "summary": "Overall debate analysis",
  "agent_scores": [
    {{"agent_id": "...", "agent_name": "...", "score": 8.5, "reasoning": "..."}}
  ],
  "winner_id": "...",
  "winner_name": "...",
  "key_arguments": ["...", "..."]
}}
"""
    return system_prompt.strip()


def format_history_for_context(
    history: List[Message],
    topic: str,
    current_round: int,
    total_rounds: int,
) -> str:
    """
    Format debate history as context for the next agent.

    Args:
        history: List of messages in the debate so far
        topic: Debate topic
        current_round: Current round number
        total_rounds: Total number of rounds

    Returns:
        Formatted history string for context
    """
    if not history:
        return f"""DEBATE TOPIC: {topic}
ROUND: {current_round} of {total_rounds}

DEBATE HISTORY:
(No previous messages)

YOUR TURN: Please provide your opening statement."""

    # Format all previous messages
    formatted_messages = []
    for msg in history:
        formatted_messages.append(
            f"[Round {msg.round_number}, Turn {msg.turn_number + 1}] "
            f"{msg.agent_name} ({msg.stance}): {msg.content}"
        )

    messages_str = "\n\n".join(formatted_messages)

    context = f"""DEBATE TOPIC: {topic}
ROUND: {current_round} of {total_rounds}

DEBATE HISTORY:
{messages_str}

YOUR TURN: Please provide your response."""

    return context.strip()


def format_history_for_judge(
    history: List[Message],
    topic: str,
) -> str:
    """
    Format complete debate history for judge evaluation.

    Args:
        history: Complete list of messages from the debate
        topic: Debate topic

    Returns:
        Formatted history string for judge evaluation
    """
    # Format all messages
    formatted_messages = []
    for msg in history:
        formatted_messages.append(
            f"[Round {msg.round_number}, Turn {msg.turn_number + 1}] "
            f"{msg.agent_name} ({msg.stance}):\n{msg.content}"
        )

    messages_str = "\n\n---\n\n".join(formatted_messages)

    context = f"""DEBATE TOPIC: {topic}

FULL TRANSCRIPT:
{messages_str}

Please evaluate the debate and provide your judgment in the specified JSON format."""

    return context.strip()


def create_user_message(content: str) -> Dict[str, str]:
    """
    Create a user message dict for LLM API.

    Args:
        content: Message content

    Returns:
        Message dict with role and content
    """
    return {"role": "user", "content": content}
