/**
 * Central export file for all TypeScript types
 * Mirrors backend Pydantic models for type safety
 */

// LLM types
export { ModelProvider, type LLMConfig } from './llm';

// Agent types
export { AgentRole, type AgentConfig } from './agent';

// Message types
export { type Message, type MessageHistory } from './message';

// Judge types
export { type AgentScore, type JudgeResult } from './judge';

// Debate types
export { DebateStatus, type DebateConfig, type DebateState } from './debate';

// Provider catalog types
export { type ModelInfo, type ProviderInfo, type ProviderCatalogResponse } from './provider';

// Persona types
export { PersonaStyle, type PersonaTemplate, type PersonaCatalogResponse } from './persona';

// WebSocket types
export {
  WebSocketEventType,
  type WebSocketMessage,
  type DebateStartedEvent,
  type RoundStartedEvent,
  type AgentThinkingEvent,
  type MessageReceivedEvent,
  type TurnCompleteEvent,
  type RoundCompleteEvent,
  type JudgingStartedEvent,
  type JudgeResultEvent,
  type DebateCompleteEvent,
  type DebateErrorEvent,
  type ConnectionEstablishedEvent,
  type DebateEvent,
} from './websocket';

// API types
export {
  type CreateDebateRequest,
  type StartDebateRequest,
  type CreateDebateResponse,
  type DebateResponse,
  type DebateListResponse,
  type StartDebateResponse,
  type DebateStatusResponse,
  type ErrorResponse,
  type ExportFormat,
} from './api';
