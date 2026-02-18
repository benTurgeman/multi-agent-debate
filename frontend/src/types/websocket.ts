/**
 * WebSocket message types - mirrors backend/models/api.py
 */

import { DebateStatus } from './debate';
import { JudgeResult } from './judge';
import { Message } from './message';

// Base WebSocket message structure
export interface WebSocketMessage {
  type: string;
  payload: Record<string, unknown>;
  timestamp: string; // ISO format
}

// Event-specific payloads
export interface DebateStartedEvent {
  debate_id: string;
  topic: string;
  num_rounds: number;
  num_agents: number;
}

export interface RoundStartedEvent {
  debate_id: string;
  round_number: number;
  total_rounds: number;
}

export interface AgentThinkingEvent {
  debate_id: string;
  agent_id: string;
  agent_name: string;
  round_number: number;
  turn_number: number;
}

export interface MessageReceivedEvent {
  debate_id: string;
  message: Message;
}

export interface TurnCompleteEvent {
  debate_id: string;
  round_number: number;
  turn_number: number;
}

export interface RoundCompleteEvent {
  debate_id: string;
  round_number: number;
}

export interface JudgingStartedEvent {
  debate_id: string;
}

export interface JudgeResultEvent {
  debate_id: string;
  result: JudgeResult;
}

export interface DebateCompleteEvent {
  debate_id: string;
  winner_id: string;
  winner_name: string;
}

export interface DebateErrorEvent {
  debate_id: string;
  error_message: string;
  context?: string | null;
}

export interface ConnectionEstablishedEvent {
  debate_id: string;
  status: DebateStatus;
  message: string;
}

// Union type for all possible event types
export type DebateEvent =
  | DebateStartedEvent
  | RoundStartedEvent
  | AgentThinkingEvent
  | MessageReceivedEvent
  | TurnCompleteEvent
  | RoundCompleteEvent
  | JudgingStartedEvent
  | JudgeResultEvent
  | DebateCompleteEvent
  | DebateErrorEvent
  | ConnectionEstablishedEvent;

// Event type names
export enum WebSocketEventType {
  CONNECTION_ESTABLISHED = 'connection_established',
  DEBATE_STARTED = 'debate_started',
  ROUND_STARTED = 'round_started',
  AGENT_THINKING = 'agent_thinking',
  MESSAGE_RECEIVED = 'message_received',
  TURN_COMPLETE = 'turn_complete',
  ROUND_COMPLETE = 'round_complete',
  JUDGING_STARTED = 'judging_started',
  JUDGE_RESULT = 'judge_result',
  DEBATE_COMPLETE = 'debate_complete',
  ERROR = 'error',
  PING = 'ping',
  PONG = 'pong',
}
