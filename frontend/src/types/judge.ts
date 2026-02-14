/**
 * Judge and scoring models - mirrors backend/models/judge.py
 */

export interface AgentScore {
  agent_id: string;
  agent_name: string;
  score: number; // 0.0 to 10.0
  reasoning: string;
}

export interface JudgeResult {
  summary: string;
  agent_scores: AgentScore[];
  winner_id: string;
  winner_name: string;
  key_arguments: string[];
}
