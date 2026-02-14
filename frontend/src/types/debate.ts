/**
 * Debate models - mirrors backend/models/debate.py
 */

import { AgentConfig } from './agent';
import { JudgeResult } from './judge';
import { Message } from './message';

export enum DebateStatus {
  CREATED = 'created',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface DebateConfig {
  topic: string;
  num_rounds: number;
  agents: AgentConfig[];
  judge_config: AgentConfig;
}

export interface DebateState {
  debate_id: string;
  config: DebateConfig;
  status: DebateStatus;
  current_round: number;
  current_turn: number;
  history: Message[];
  judge_result: JudgeResult | null;
  error_message: string | null;
  created_at: string; // ISO format datetime
  started_at: string | null;
  completed_at: string | null;
}
