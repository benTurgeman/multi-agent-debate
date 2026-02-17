/**
 * LiveDebate - Main container for live debate view
 * Displays round indicator and real-time message stream
 */

import React from 'react';
import clsx from 'clsx';
import { RoundIndicator } from '../../molecules';
import { MessageList } from './MessageList';
import { useDebateStateStore } from '../../../stores';
import { DebateStatus } from '../../../types';

export interface LiveDebateProps {
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get current agent's name for turn indicator
 */
function getCurrentAgentName(
  agentId: string | null,
  agents: Array<{ agent_id: string; name: string }>
): string | undefined {
  if (!agentId) return undefined;
  return agents.find((a) => a.agent_id === agentId)?.name;
}

export const LiveDebate: React.FC<LiveDebateProps> = ({ className }) => {
  // Get debate state from store
  const debate = useDebateStateStore((state) => state.debate);
  const getCurrentAgent = useDebateStateStore((state) => state.getCurrentAgent);

  // Early return if no debate
  if (!debate) {
    return (
      <div
        className={clsx(
          'flex flex-col items-center justify-center',
          'h-full bg-slate-900 rounded-lg border border-slate-800',
          className
        )}
      >
        <div className="text-center">
          <p className="text-slate-400 text-lg">No active debate</p>
          <p className="text-slate-500 text-sm mt-2">
            Configure and start a debate to see it here
          </p>
        </div>
      </div>
    );
  }

  // Get current agent info
  const currentAgentId = getCurrentAgent();
  const currentAgentName = getCurrentAgentName(
    currentAgentId,
    debate.config.agents
  );

  // Backend sends 1-indexed round numbers, use them directly
  const displayRound = debate.current_round;
  const totalRounds = debate.config.num_rounds;

  return (
    <div
      className={clsx(
        'flex flex-col h-full',
        'bg-slate-900 rounded-lg border border-slate-800',
        'overflow-hidden',
        className
      )}
    >
      {/* Header with round indicator */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-slate-800">
        <div className="flex items-center justify-between">
          {/* Round indicator */}
          <RoundIndicator
            currentRound={displayRound}
            totalRounds={totalRounds}
            currentTurn={currentAgentName}
            size="md"
          />

          {/* Status badge */}
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm text-slate-400">Live</span>
          </div>
        </div>

        {/* Debate topic */}
        <div className="mt-3">
          <p className="text-sm text-slate-500">Topic:</p>
          <p className="text-base text-slate-200 mt-1">
            {debate.config.topic}
          </p>
        </div>
      </div>

      {/* Message list - takes remaining space and scrolls */}
      <MessageList
        messages={debate.history}
        autoScroll={true}
        showThinking={true}
        className="flex-1"
      />

      {/* Footer with message count */}
      <div className="flex-shrink-0 px-6 py-3 border-t border-slate-800 bg-slate-950">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-500">
            {debate.history.length} message{debate.history.length !== 1 ? 's' : ''}
          </span>

          {debate.status === DebateStatus.COMPLETED && (
            <span className="text-green-500 font-medium">
              Debate Complete
            </span>
          )}

          {debate.status === DebateStatus.IN_PROGRESS && (
            <span className="text-blue-500 font-medium">
              In Progress
            </span>
          )}

          {debate.status === DebateStatus.FAILED && (
            <span className="text-red-500 font-medium">
              Failed
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
