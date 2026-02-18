"""Manual test for 3-agent debate with real LLM APIs.

Run this script to test a real debate between 3 agents with mixed models.
Requires ANTHROPIC_API_KEY and OPENAI_API_KEY in .env file.

Usage:
    python manual_tests/test_3_agent_debate.py
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


def create_3_agent_debate() -> DebateConfig:
    """Create a 3-agent debate configuration with mixed models."""
    return DebateConfig(
        topic="Should governments implement universal basic income?",
        num_rounds=2,
        agents=[
            AgentConfig(
                agent_id="advocate",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="UBI Advocate",
                stance="Pro",
                system_prompt=(
                    "You are an economist and social policy expert who supports universal basic "
                    "income (UBI). Argue that UBI would reduce poverty, provide economic security, "
                    "stimulate entrepreneurship, and prepare society for automation-driven job losses."
                ),
                temperature=1.0,
                max_tokens=800,
            ),
            AgentConfig(
                agent_id="critic",
                llm_config=LLMConfig(
                    provider=ModelProvider.OPENAI,
                    model_name="gpt-4o",
                    api_key_env_var="OPENAI_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="UBI Critic",
                stance="Con",
                system_prompt=(
                    "You are a fiscal conservative economist who opposes universal basic income. "
                    "Argue that UBI is economically unsustainable, would reduce work incentives, "
                    "cause inflation, and create dependency rather than solving root problems."
                ),
                temperature=0.9,
                max_tokens=800,
            ),
            AgentConfig(
                agent_id="pragmatist",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="Pragmatist",
                stance="Neutral",
                system_prompt=(
                    "You are a pragmatic policy analyst who sees both benefits and challenges with UBI. "
                    "Acknowledge valid points from both sides, discuss implementation challenges, "
                    "and propose evidence-based conditional or pilot approaches."
                ),
                temperature=1.0,
                max_tokens=800,
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
            name="Expert Judge",
            stance="Neutral",
            system_prompt=(
                "You are an expert in economics and public policy with deep knowledge of UBI research. "
                "Evaluate each participant on: argument strength, evidence quality, engagement with "
                "other participants' points, and overall persuasiveness. Provide detailed scores "
                "(0-10) and identify the most compelling arguments from all sides."
            ),
            temperature=0.7,
            max_tokens=2048,
        ),
    )


async def main():
    """Run 3-agent debate test."""
    print("=" * 80)
    print("3-AGENT DEBATE TEST (Mixed Models: Claude + GPT-4)")
    print("=" * 80)
    print()

    # Create debate manager
    manager = DebateManager()

    # Event callback to show progress
    def on_event(event):
        if event.event_type == DebateEventType.DEBATE_STARTED:
            print("🎬 Debate started!")

        elif event.event_type == DebateEventType.ROUND_STARTED:
            print(f"\n{'=' * 80}")
            print(f"📍 ROUND {event.payload['round_number']}")
            print(f"{'=' * 80}")

        elif event.event_type == DebateEventType.AGENT_THINKING:
            print(f"\n💭 {event.payload['agent_name']} is preparing response...")

        elif event.event_type == DebateEventType.MESSAGE_RECEIVED:
            msg = event.payload["message"]
            print(f"\n🗣️  {msg['agent_name']} ({msg['stance']}):")
            print(f"─" * 80)
            print(msg["content"])
            print(f"─" * 80)

        elif event.event_type == DebateEventType.ROUND_COMPLETE:
            print(f"\n✅ Round {event.payload['round_number']} complete")

        elif event.event_type == DebateEventType.JUDGING_STARTED:
            print(f"\n{'=' * 80}")
            print("⚖️  JUDGE IS EVALUATING THE DEBATE")
            print(f"{'=' * 80}")

        elif event.event_type == DebateEventType.JUDGE_RESULT:
            result = event.payload["judge_result"]
            print(f"\n{'=' * 80}")
            print("🏆 FINAL JUDGMENT")
            print(f"{'=' * 80}")
            print(f"\n🥇 Winner: {result['winner_name']}\n")
            print("📊 Scores:")
            for score in result["agent_scores"]:
                stars = "⭐" * int(score["score"])
                print(f"\n  {score['agent_name']}: {score['score']}/10 {stars}")
                print(f"  └─ {score['reasoning']}")
            print(f"\n📝 Summary:")
            print(f"  {result['summary']}")
            if result.get("key_arguments"):
                print(f"\n🔑 Key Arguments:")
                for arg in result["key_arguments"]:
                    print(f"  • {arg}")

        elif event.event_type == DebateEventType.DEBATE_COMPLETE:
            print(f"\n{'=' * 80}")
            print("✨ DEBATE COMPLETE!")
            print(f"{'=' * 80}")

        elif event.event_type == DebateEventType.ERROR:
            print(f"\n❌ Error: {event.payload['error_message']}")

    manager.register_event_callback(on_event)

    # Create and run debate
    config = create_3_agent_debate()
    debate_state = manager.create_debate(config)

    print(f"Debate ID: {debate_state.debate_id}")
    print(f"Topic: {config.topic}")
    print(f"Rounds: {config.num_rounds}")
    print(f"Participants:")
    for agent in config.agents:
        model_info = f"{agent.llm_config.provider.value}/{agent.llm_config.model_name}"
        print(f"  • {agent.name} ({agent.stance}) - {model_info}")
    print()

    try:
        result = await manager.run_debate(debate_state)
        print(f"\n✅ Final status: {result.status.value}")
        print(f"📨 Total messages: {len(result.history)}")
        return result
    except Exception as e:
        print(f"\n❌ Error running debate: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
