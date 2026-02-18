"""Manual test for 2-agent debate with real LLM APIs.

Run this script to test a real debate between 2 agents.
Requires ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file.

Usage:
    python manual_tests/test_2_agent_debate.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.debate_manager import DebateManager, DebateEventType
from models.debate import DebateConfig
from models.agent import AgentConfig, AgentRole
from models.llm import LLMConfig, ModelProvider


def create_2_agent_debate() -> DebateConfig:
    """Create a 2-agent debate configuration."""
    return DebateConfig(
        topic="Artificial Intelligence will benefit humanity more than harm it",
        num_rounds=2,
        agents=[
            AgentConfig(
                agent_id="optimist",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="Tech Optimist",
                stance="Pro",
                system_prompt=(
                    "You are an optimistic technologist who believes in AI's potential to solve "
                    "humanity's greatest challenges. Present compelling arguments about AI's "
                    "benefits in healthcare, education, scientific research, and quality of life."
                ),
                temperature=1.0,
                max_tokens=1024,
            ),
            AgentConfig(
                agent_id="skeptic",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="AI Skeptic",
                stance="Con",
                system_prompt=(
                    "You are a thoughtful AI safety researcher who is concerned about the risks "
                    "of advanced AI. Present well-reasoned arguments about potential harms: "
                    "job displacement, privacy concerns, algorithmic bias, and existential risks."
                ),
                temperature=0.9,
                max_tokens=1024,
            ),
        ],
        judge_config=AgentConfig(
            agent_id="judge",
            llm_config=LLMConfig(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-5-sonnet-20241022",
                api_key_env_var="ANTHROPIC_API_KEY",
            ),
            role=AgentRole.JUDGE,
            name="Impartial Judge",
            stance="Neutral",
            system_prompt=(
                "You are an impartial debate judge with expertise in AI and technology ethics. "
                "Evaluate arguments based on: logical coherence, use of evidence, addressing "
                "counterarguments, and overall persuasiveness. Provide scores from 0-10 for each "
                "debater and declare a winner with detailed reasoning."
            ),
            temperature=0.7,
            max_tokens=2048,
        ),
    )


async def main():
    """Run 2-agent debate test."""
    print("=" * 80)
    print("2-AGENT DEBATE TEST")
    print("=" * 80)
    print()

    # Create debate manager
    manager = DebateManager()

    # Event callback to show progress
    def on_event(event):
        if event.event_type == DebateEventType.DEBATE_STARTED:
            print("🎬 Debate started!")

        elif event.event_type == DebateEventType.ROUND_STARTED:
            print(f"\n📍 Round {event.payload['round_number']} started")

        elif event.event_type == DebateEventType.AGENT_THINKING:
            print(f"   💭 {event.payload['agent_name']} is thinking...")

        elif event.event_type == DebateEventType.MESSAGE_RECEIVED:
            msg = event.payload["message"]
            print(f"\n   🗣️  {msg['agent_name']} ({msg['stance']}):")
            print(f"   {msg['content'][:200]}...")  # First 200 chars

        elif event.event_type == DebateEventType.ROUND_COMPLETE:
            print(f"\n✅ Round {event.payload['round_number']} complete")

        elif event.event_type == DebateEventType.JUDGING_STARTED:
            print(f"\n⚖️  Judge is evaluating...")

        elif event.event_type == DebateEventType.JUDGE_RESULT:
            result = event.payload["judge_result"]
            print(f"\n{'=' * 80}")
            print("🏆 JUDGE'S DECISION")
            print(f"{'=' * 80}")
            print(f"\nWinner: {result['winner_name']}")
            print(f"\nScores:")
            for score in result["agent_scores"]:
                print(f"  - {score['agent_name']}: {score['score']}/10")
                print(f"    Reasoning: {score['reasoning']}")
            print(f"\nSummary: {result['summary']}")

        elif event.event_type == DebateEventType.DEBATE_COMPLETE:
            print(f"\n{'=' * 80}")
            print("✨ Debate complete!")
            print(f"{'=' * 80}")

        elif event.event_type == DebateEventType.ERROR:
            print(f"\n❌ Error: {event.payload['error_message']}")

    manager.register_event_callback(on_event)

    # Create and run debate
    config = create_2_agent_debate()
    debate_state = manager.create_debate(config)

    print(f"Debate ID: {debate_state.debate_id}")
    print(f"Topic: {config.topic}")
    print(f"Rounds: {config.num_rounds}")
    print(f"Agents: {len(config.agents)}")
    print()

    try:
        result = await manager.run_debate(debate_state)
        print(f"\n✅ Final status: {result.status.value}")
        return result
    except Exception as e:
        print(f"\n❌ Error running debate: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
