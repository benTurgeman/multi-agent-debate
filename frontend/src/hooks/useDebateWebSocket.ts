/**
 * WebSocket hook for real-time debate updates
 * Manages connection lifecycle, auto-reconnection, and event handling
 */

import { useEffect, useRef, useCallback } from 'react';
import { WS_BASE_URL } from '../api/config';
import { useDebateStateStore } from '../stores';
import {
  WebSocketEventType,
  DebateStartedEvent,
  RoundStartedEvent,
  AgentThinkingEvent,
  MessageReceivedEvent,
  TurnCompleteEvent,
  RoundCompleteEvent,
  JudgingStartedEvent,
  JudgeResultEvent,
  DebateCompleteEvent,
  DebateErrorEvent,
  ConnectionEstablishedEvent,
  DebateStatus,
} from '../types';

interface WebSocketMessage {
  type: string;
  debate_id: string;
  payload: any;
  timestamp: string;
}

interface UseDebateWebSocketOptions {
  /** Callback when connection is established */
  onConnect?: () => void;
  /** Callback when connection fails */
  onError?: (error: Error) => void;
  /** Callback when disconnected */
  onDisconnect?: () => void;
  /** Enable debug logging */
  debug?: boolean;
}

interface UseDebateWebSocketReturn {
  /** Connect to a debate's WebSocket */
  connect: (debateId: string) => void;
  /** Disconnect from current WebSocket */
  disconnect: () => void;
  /** Send a ping to keep connection alive */
  ping: () => void;
}

// Reconnection configuration
const INITIAL_RECONNECT_DELAY = 1000; // 1 second
const MAX_RECONNECT_DELAY = 30000; // 30 seconds
const RECONNECT_MULTIPLIER = 2;
const HEARTBEAT_INTERVAL = 30000; // 30 seconds

/**
 * Custom hook for managing WebSocket connection to debate
 */
export function useDebateWebSocket(
  options: UseDebateWebSocketOptions = {}
): UseDebateWebSocketReturn {
  const { onConnect, onError, onDisconnect, debug = false } = options;

  // Store actions
  const {
    setDebate,
    updateDebateStatus,
    setCurrentRound,
    setCurrentTurn,
    addMessage,
    setJudgeResult,
    setConnectionState,
    addThinkingAgent,
    removeThinkingAgent,
    setError,
  } = useDebateStateStore();

  // Refs for stable state across renders
  const wsRef = useRef<WebSocket | null>(null);
  const debateIdRef = useRef<string | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectDelayRef = useRef<number>(INITIAL_RECONNECT_DELAY);
  const shouldReconnectRef = useRef<boolean>(true);

  /**
   * Log debug messages if debug mode is enabled
   */
  const log = useCallback(
    (...args: any[]) => {
      if (debug) {
        console.log('[useDebateWebSocket]', ...args);
      }
    },
    [debug]
  );

  /**
   * Clear reconnection timeout
   */
  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  /**
   * Clear heartbeat interval
   */
  const clearHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  /**
   * Start heartbeat ping/pong mechanism
   */
  const startHeartbeat = useCallback(() => {
    clearHeartbeat();

    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        log('Sending heartbeat ping');
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, HEARTBEAT_INTERVAL);
  }, [clearHeartbeat, log]);

  /**
   * Handle incoming WebSocket messages
   */
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        log('Received message:', message.type);

        switch (message.type) {
          case WebSocketEventType.CONNECTION_ESTABLISHED: {
            const payload = message.payload as ConnectionEstablishedEvent;
            log('Connection established:', payload);
            setConnectionState('connected');
            reconnectDelayRef.current = INITIAL_RECONNECT_DELAY;
            onConnect?.();
            break;
          }

          case WebSocketEventType.DEBATE_STARTED: {
            const payload = message.payload as DebateStartedEvent;
            log('Debate started:', payload);
            updateDebateStatus(DebateStatus.IN_PROGRESS);
            break;
          }

          case WebSocketEventType.ROUND_STARTED: {
            const payload = message.payload as RoundStartedEvent;
            log('Round started:', payload.round_number);
            setCurrentRound(payload.round_number);
            break;
          }

          case WebSocketEventType.AGENT_THINKING: {
            const payload = message.payload as AgentThinkingEvent;
            log('Agent thinking:', payload.agent_name);
            addThinkingAgent(payload.agent_id, payload.agent_name);
            setCurrentTurn(payload.turn_number);
            break;
          }

          case WebSocketEventType.MESSAGE_RECEIVED: {
            const payload = message.payload as MessageReceivedEvent;
            log('Message received from:', payload.message.agent_name);
            addMessage(payload.message);
            // Remove thinking indicator for this agent
            removeThinkingAgent(payload.message.agent_id);
            break;
          }

          case WebSocketEventType.TURN_COMPLETE: {
            const payload = message.payload as TurnCompleteEvent;
            log('Turn complete:', `Round ${payload.round_number}, Turn ${payload.turn_number}`);
            // Turn completion is informational - state already updated by MESSAGE_RECEIVED
            break;
          }

          case WebSocketEventType.ROUND_COMPLETE: {
            const payload = message.payload as RoundCompleteEvent;
            log('Round complete:', payload.round_number);
            // Round completion is informational - next ROUND_STARTED will update state
            break;
          }

          case WebSocketEventType.JUDGING_STARTED: {
            const payload = message.payload as JudgingStartedEvent;
            log('Judging started for debate:', payload.debate_id);
            // Could add a "judging" status or loading indicator here if desired
            break;
          }

          case WebSocketEventType.JUDGE_RESULT: {
            const payload = message.payload as JudgeResultEvent;
            log('Judge result received');
            setJudgeResult(payload.result);
            break;
          }

          case WebSocketEventType.DEBATE_COMPLETE: {
            const payload = message.payload as DebateCompleteEvent;
            log('Debate complete. Winner:', payload.winner_name);
            updateDebateStatus(DebateStatus.COMPLETED);
            break;
          }

          case WebSocketEventType.ERROR: {
            const payload = message.payload as DebateErrorEvent;
            log('Debate error:', payload.error_message);
            setError(payload.error_message);
            updateDebateStatus(DebateStatus.FAILED);
            break;
          }

          case WebSocketEventType.PONG: {
            log('Received pong');
            break;
          }

          default:
            log('Unknown message type:', message.type);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    },
    [
      log,
      setConnectionState,
      updateDebateStatus,
      setCurrentRound,
      setCurrentTurn,
      addThinkingAgent,
      removeThinkingAgent,
      addMessage,
      setJudgeResult,
      setError,
      onConnect,
    ]
  );

  /**
   * Attempt to reconnect with exponential backoff
   */
  const attemptReconnect = useCallback(() => {
    if (!shouldReconnectRef.current || !debateIdRef.current) {
      return;
    }

    clearReconnectTimeout();

    log(`Reconnecting in ${reconnectDelayRef.current}ms...`);
    setConnectionState('connecting');

    reconnectTimeoutRef.current = setTimeout(() => {
      if (debateIdRef.current) {
        log('Attempting reconnection...');
        connect(debateIdRef.current);

        // Increase delay for next attempt (exponential backoff)
        reconnectDelayRef.current = Math.min(
          reconnectDelayRef.current * RECONNECT_MULTIPLIER,
          MAX_RECONNECT_DELAY
        );
      }
    }, reconnectDelayRef.current);
  }, [log, setConnectionState]);

  /**
   * Handle WebSocket errors
   */
  const handleError = useCallback(
    (event: Event) => {
      log('WebSocket error:', event);
      setConnectionState('error');

      const error = new Error('WebSocket connection error');
      onError?.(error);
    },
    [log, setConnectionState, onError]
  );

  /**
   * Handle WebSocket close
   */
  const handleClose = useCallback(
    (event: CloseEvent) => {
      log('WebSocket closed:', event.code, event.reason);

      clearHeartbeat();
      wsRef.current = null;

      // Update state
      setConnectionState('disconnected');
      onDisconnect?.();

      // Attempt reconnection if not a normal closure and reconnect is enabled
      if (event.code !== 1000 && shouldReconnectRef.current) {
        attemptReconnect();
      }
    },
    [log, clearHeartbeat, setConnectionState, onDisconnect, attemptReconnect]
  );

  /**
   * Handle WebSocket open
   */
  const handleOpen = useCallback(() => {
    log('WebSocket connected');
    startHeartbeat();
  }, [log, startHeartbeat]);

  /**
   * Connect to a debate's WebSocket
   */
  const connect = useCallback(
    (debateId: string) => {
      // Close existing connection if any
      if (wsRef.current) {
        shouldReconnectRef.current = false;
        wsRef.current.close();
        clearReconnectTimeout();
        clearHeartbeat();
      }

      log('Connecting to debate:', debateId);
      debateIdRef.current = debateId;
      shouldReconnectRef.current = true;
      setConnectionState('connecting');

      try {
        const url = `${WS_BASE_URL}/api/ws/${debateId}`;
        log('WebSocket URL:', url);

        const ws = new WebSocket(url);
        wsRef.current = ws;

        // Set up event handlers
        ws.onopen = handleOpen;
        ws.onmessage = handleMessage;
        ws.onerror = handleError;
        ws.onclose = handleClose;
      } catch (error) {
        log('Error creating WebSocket:', error);
        setConnectionState('error');
        onError?.(error as Error);
      }
    },
    [
      log,
      setConnectionState,
      handleOpen,
      handleMessage,
      handleError,
      handleClose,
      clearReconnectTimeout,
      clearHeartbeat,
      onError,
    ]
  );

  /**
   * Disconnect from current WebSocket
   */
  const disconnect = useCallback(() => {
    log('Disconnecting...');
    shouldReconnectRef.current = false;
    clearReconnectTimeout();
    clearHeartbeat();

    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnected');
      wsRef.current = null;
    }

    debateIdRef.current = null;
    setConnectionState('disconnected');
  }, [log, clearReconnectTimeout, clearHeartbeat, setConnectionState]);

  /**
   * Send a ping to keep connection alive
   */
  const ping = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      log('Sending manual ping');
      wsRef.current.send(JSON.stringify({ type: 'ping' }));
    }
  }, [log]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      shouldReconnectRef.current = false;
      clearReconnectTimeout();
      clearHeartbeat();

      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounted');
      }
    };
  }, [clearReconnectTimeout, clearHeartbeat]);

  return {
    connect,
    disconnect,
    ping,
  };
}
