"""Manual test for 5-agent debate with real LLM APIs.

Run this script to test a complex debate between 5 agents with diverse perspectives.
Requires ANTHROPIC_API_KEY in .env file.

Usage:
    python manual_tests/test_5_agent_debate.py
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


def create_5_agent_debate() -> DebateConfig:
    """Create a 5-agent debate configuration with diverse perspectives."""
    return DebateConfig(
        topic="What is the most important challenge facing humanity in the next 50 years?",
        num_rounds=2,
        agents=[
            AgentConfig(
                agent_id="climate_expert",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="Climate Scientist",
                stance="Climate Change",
                system_prompt=(
                    "You are a climate scientist arguing that climate change is humanity's greatest "
                    "challenge. Present evidence of its cascading effects on ecosystems, economies, "
                    "and societies. Emphasize the urgency and irreversibility of climate tipping points."
                ),
                temperature=1.0,
                max_tokens=700,
            ),
            AgentConfig(
                agent_id="ai_researcher",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="AI Researcher",
                stance="AI Alignment",
                system_prompt=(
                    "You are an AI safety researcher arguing that ensuring beneficial AGI is "
                    "humanity's greatest challenge. Discuss existential risks, the difficulty of "
                    "alignment, and why this overshadows other concerns as AI capabilities accelerate."
                ),
                temperature=1.0,
                max_tokens=700,
            ),
            AgentConfig(
                agent_id="health_expert",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="Global Health Expert",
                stance="Pandemic Preparedness",
                system_prompt=(
                    "You are a global health expert arguing that pandemic preparedness is the most "
                    "critical challenge. Reference COVID-19 lessons, emerging diseases, antimicrobial "
                    "resistance, and bioterrorism risks. Emphasize the interconnected global health system."
                ),
                temperature=1.0,
                max_tokens=700,
            ),
            AgentConfig(
                agent_id="economist",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="Development Economist",
                stance="Economic Inequality",
                system_prompt=(
                    "You are a development economist arguing that rising global inequality is the "
                    "biggest challenge. Discuss wealth concentration, resource conflicts, social "
                    "instability, and how inequality undermines solutions to other global problems."
                ),
                temperature=1.0,
                max_tokens=700,
            ),
            AgentConfig(
                agent_id="political_scientist",
                llm_config=LLMConfig(
                    provider=ModelProvider.ANTHROPIC,
                    model_name="claude-3-5-sonnet-20241022",
                    api_key_env_var="ANTHROPIC_API_KEY",
                ),
                role=AgentRole.DEBATER,
                name="Political Scientist",
                stance="Democratic Erosion",
                system_prompt=(
                    "You are a political scientist arguing that the erosion of democratic institutions "
                    "is our greatest challenge. Discuss rising authoritarianism, misinformation, "
                    "tribalism, and why functional governance is prerequisite to solving other crises."
                ),
                temperature=1.0,
                max_tokens=700,
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
            name="Interdisciplinary Judge",
            stance="Neutral",
            system_prompt=(
                "You are a polymath judge with expertise across climate science, AI, public health, "
                "economics, and political science. Evaluate each argument on: evidence quality, "
                "consideration of counterarguments, acknowledgment of interconnections, and "
                "persuasiveness. Identify which challenge has the strongest case for being most critical."
            ),
            temperature=0.7,
            max_tokens=3000,
        ),
    )


async def main():
    """Run 5-agent debate test."""
    print("=" * 80)
    print("5-AGENT DEBATE TEST - HUMANITY'S GREATEST CHALLENGE")
    print("=" * 80)
    print()

    # Create debate manager
    manager = DebateManager()

    # Event callback to show progress
    turn_count = {"count": 0}

    def on_event(event):
        if event.event_type == DebateEventType.DEBATE_STARTED:
            print("🎬 Debate started with 5 participants!")
            print()

        elif event.event_type == DebateEventType.ROUND_STARTED:
            print(f"\n{'=' * 80}")
            print(f"📍 ROUND {event.payload['round_number']} BEGINS")
            print(f"{'=' * 80}\n")

        elif event.event_type == DebateEventType.AGENT_THINKING:
            turn_count["count"] += 1
            print(f"[Turn {turn_count['count']}/10] 💭 {event.payload['agent_name']} is formulating argument...")

        elif event.event_type == DebateEventType.MESSAGE_RECEIVED:
            msg = event.payload["message"]
            print(f"\n{'─' * 80}")
            print(f"🗣️  {msg['agent_name']} - {msg['stance']}")
            print(f"{'─' * 80}")
            print(msg["content"])
            print(f"{'─' * 80}\n")

        elif event.event_type == DebateEventType.ROUND_COMPLETE:
            print(f"✅ Round {event.payload['round_number']} complete\n")

        elif event.event_type == DebateEventType.JUDGING_STARTED:
            print(f"\n{'=' * 80}")
            print("⚖️  FINAL JUDGMENT IN PROGRESS")
            print("⚖️  (This may take a moment with 5 participants to evaluate...)")
            print(f"{'=' * 80}\n")

        elif event.event_type == DebateEventType.JUDGE_RESULT:
            result = event.payload["judge_result"]
            print(f"{'=' * 80}")
            print("🏆 FINAL VERDICT")
            print(f"{'=' * 80}\n")

            print(f"🥇 WINNER: {result['winner_name']}\n")

            print("📊 DETAILED SCORES:\n")
            sorted_scores = sorted(
                result["agent_scores"],
                key=lambda x: x["score"],
                reverse=True
            )
            for i, score in enumerate(sorted_scores, 1):
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
                stars = "⭐" * int(score["score"])
                print(f"{medal} #{i} - {score['agent_name']}: {score['score']}/10 {stars}")
                print(f"      Reasoning: {score['reasoning']}\n")

            print(f"{'─' * 80}")
            print("📝 JUDGE'S SUMMARY:")
            print(f"{'─' * 80}")
            print(result['summary'])

            if result.get("key_arguments"):
                print(f"\n{'─' * 80}")
                print("🔑 KEY TAKEAWAYS:")
                print(f"{'─' * 80}")
                for arg in result["key_arguments"]:
                    print(f"  • {arg}")

        elif event.event_type == DebateEventType.DEBATE_COMPLETE:
            print(f"\n{'=' * 80}")
            print("✨ 5-AGENT DEBATE COMPLETE!")
            print(f"{'=' * 80}\n")

        elif event.event_type == DebateEventType.ERROR:
            print(f"\n❌ ERROR: {event.payload['error_message']}")

    manager.register_event_callback(on_event)

    # Create and run debate
    config = create_5_agent_debate()
    debate_state = manager.create_debate(config)

    print(f"📋 Debate Configuration:")
    print(f"   ID: {debate_state.debate_id}")
    print(f"   Topic: {config.topic}")
    print(f"   Rounds: {config.num_rounds}")
    print(f"   Total turns: {config.num_rounds * len(config.agents)}")
    print()
    print(f"👥 Participants:")
    for i, agent in enumerate(config.agents, 1):
        print(f"   {i}. {agent.name} - arguing for {agent.stance}")
    print()

    try:
        start_time = asyncio.get_event_loop().time()
        result = await manager.run_debate(debate_state)
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        print(f"✅ Status: {result.status.value}")
        print(f"📨 Total messages: {len(result.history)}")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print()
        return result
    except Exception as e:
        print(f"\n❌ Error running debate: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    print("\n⚠️  This test will make multiple LLM API calls and may take 2-3 minutes.")
    print("⚠️  Ensure ANTHROPIC_API_KEY is set in your .env file.\n")
    input("Press Enter to continue...")
    asyncio.run(main())
