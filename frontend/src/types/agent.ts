/**
 * Agent models - mirrors backend/models/agent.py
 */

import { LLMConfig } from './llm';

export enum AgentRole {
  DEBATER = 'debater',
  JUDGE = 'judge',
}

export interface AgentConfig {
  agent_id: string;
  llm_config: LLMConfig;
  role: AgentRole;
  name: string;
  stance: string;
  system_prompt: string;
  temperature: number;
  max_tokens: number;
}
