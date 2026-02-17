/**
 * API request and response types - mirrors backend/models/api.py
 */

import { DebateConfig, DebateState, DebateStatus } from './debate';

// Request types
export interface CreateDebateRequest {
  config: DebateConfig;
}

export interface StartDebateRequest {
  // Empty request body
}

// Response types
export interface CreateDebateResponse {
  debate_id: string;
  status: DebateStatus;
  message?: string;
}

export interface DebateResponse {
  debate: DebateState;
}

export interface DebateListResponse {
  debates: DebateState[];
  total: number;
}

export interface StartDebateResponse {
  debate_id: string;
  status: DebateStatus;
  message?: string;
}

export interface DebateStatusResponse {
  debate_id: string;
  status: DebateStatus;
  current_round: number;
  current_turn: number;
  total_rounds: number;
  message_count: number;
}

export interface ErrorResponse {
  error: string;
  detail?: string | null;
}

// Export format types
export type ExportFormat = 'json' | 'markdown' | 'text';
