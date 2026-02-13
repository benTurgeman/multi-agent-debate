"""Judge and scoring models."""
from typing import List

from pydantic import BaseModel, Field


class AgentScore(BaseModel):
    """Score for a single agent."""

    agent_id: str = Field(..., description="ID of the agent being scored")
    agent_name: str = Field(..., description="Display name of the agent")
    score: float = Field(..., ge=0.0, le=10.0, description="Score from 0-10")
    reasoning: str = Field(..., description="Explanation for the score")


class JudgeResult(BaseModel):
    """Final judgment and scores from the judge."""

    summary: str = Field(..., description="Overall debate analysis and summary")
    agent_scores: List[AgentScore] = Field(
        ..., description="Scores for each participant"
    )
    winner_id: str = Field(..., description="ID of the winning agent")
    winner_name: str = Field(..., description="Display name of the winning agent")
    key_arguments: List[str] = Field(
        default_factory=list, description="Key arguments identified in the debate"
    )

    def get_score_for_agent(self, agent_id: str) -> float:
        """
        Get the score for a specific agent.

        Args:
            agent_id: ID of the agent

        Returns:
            Agent's score, or 0.0 if not found
        """
        for score in self.agent_scores:
            if score.agent_id == agent_id:
                return score.score
        return 0.0
