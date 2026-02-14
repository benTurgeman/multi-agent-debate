/**
 * Main App component
 * Integrates all organisms into a complete debate application
 */

import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/templates/Header';
import { DebateLayout } from './components/templates/DebateLayout';
import { DebateConfig } from './components/organisms/DebateConfig';
import { LiveDebate } from './components/organisms/LiveDebate';
import { ParticipantsPanel } from './components/organisms/ParticipantsPanel';
import { VerdictPanel } from './components/organisms/VerdictPanel';
import { useDebateConfigStore, useDebateStateStore } from './stores';
import { useDebateWebSocket } from './hooks/useDebateWebSocket';
import { debatesApi } from './api/debates';
import { DebateStatus } from './types';
import type { StatusType } from './components/atoms';

function App() {
  // Local state for app lifecycle
  const [debateId, setDebateId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get config and state stores
  const { getConfig } = useDebateConfigStore();
  const { debate, connectionState, updateDebateStatus, setDebate } =
    useDebateStateStore();

  // WebSocket hook
  const { connect, disconnect } = useDebateWebSocket({
    debug: true,
    onConnect: () => {
      console.log('Connected to debate WebSocket');
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
      setError('WebSocket connection failed');
    },
  });

  // Enable dark mode by default
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  /**
   * Create and start debate
   */
  const handleStartDebate = useCallback(async () => {
    const config = getConfig();
    if (!config) {
      setError('Invalid debate configuration');
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      // Step 1: Create debate
      const createResponse = await debatesApi.create(config);
      const newDebateId = createResponse.debate_id;
      setDebateId(newDebateId);

      // Step 2: Connect WebSocket
      connect(newDebateId);

      // Step 3: Fetch initial state
      const debateState = await debatesApi.get(newDebateId);
      setDebate(debateState);

      // Step 4: Start debate execution
      setIsStarting(true);
      await debatesApi.start(newDebateId);
      updateDebateStatus(DebateStatus.IN_PROGRESS);

      setIsStarting(false);
    } catch (err) {
      console.error('Failed to start debate:', err);
      setError(err instanceof Error ? err.message : 'Failed to start debate');
      setIsCreating(false);
      setIsStarting(false);
    }

    setIsCreating(false);
  }, [getConfig, connect, setDebate, updateDebateStatus]);

  /**
   * Map connection state to status indicator type
   */
  const getConnectionStatus = (): StatusType => {
    switch (connectionState) {
      case 'connected':
        return 'connected';
      case 'connecting':
        return 'connecting';
      case 'error':
        return 'error';
      case 'disconnected':
        return 'disconnected';
      default:
        return 'disconnected';
    }
  };

  /**
   * Determine if debate is active
   */
  const isDebateActive = debate?.status === DebateStatus.IN_PROGRESS;

  /**
   * Determine if debate is complete
   */
  const isDebateComplete = debate?.status === DebateStatus.COMPLETED;

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return (
    <DebateLayout
      header={
        <Header
          connectionStatus={debateId ? getConnectionStatus() : undefined}
          isDebateActive={isDebateActive}
          isDebateComplete={isDebateComplete}
          isStarting={isStarting}
        />
      }
      leftPanel={
        <DebateConfig
          onStartDebate={handleStartDebate}
          isCreating={isCreating || isStarting}
        />
      }
      centerPanel={
        <div className="h-full">
          {error && (
            <div className="mb-4 bg-red-500/10 border border-red-500/20 rounded-lg p-4">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}
          <LiveDebate />
        </div>
      }
      rightPanel={<ParticipantsPanel />}
      bottomPanel={
        <VerdictPanel
          show={isDebateComplete && !!debate?.judge_result}
        />
      }
    />
  );
}

export default App;
