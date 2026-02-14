/**
 * ParticipantsPanel - Right sidebar showing all debate participants
 * Displays agent cards with real-time status and statistics
 */

import React from 'react';
import clsx from 'clsx';
import { AgentStatsCard } from './AgentStatsCard';
import { useDebateStateStore } from '../../../stores';

export interface ParticipantsPanelProps {
  /**
   * Additional CSS classes
   */
  className?: string;
}

export const ParticipantsPanel: React.FC<ParticipantsPanelProps> = ({
  className,
}) => {
  // Get debate state from store
  const debate = useDebateStateStore((state) => state.debate);

  // Early return if no debate
  if (!debate) {
    return (
      <div
        className={clsx(
          'flex flex-col items-center justify-center',
          'h-full bg-slate-900 rounded-lg border border-slate-800',
          'p-6',
          className
        )}
      >
        <div className="text-center">
          <p className="text-slate-400 text-base">No participants</p>
          <p className="text-slate-500 text-sm mt-2">
            Start a debate to see participants here
          </p>
        </div>
      </div>
    );
  }

  // Get all debater agents (exclude judge)
  const debaters = debate.config.agents;

  return (
    <div
      className={clsx(
        'flex flex-col h-full',
        'bg-slate-900 rounded-lg border border-slate-800',
        'overflow-hidden',
        className
      )}
    >
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-slate-800">
        <h2 className="text-lg font-semibold text-slate-200">Participants</h2>
        <p className="text-sm text-slate-500 mt-1">
          {debaters.length} agent{debaters.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Agent cards - scrollable */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {debaters.map((agent) => (
          <AgentStatsCard key={agent.agent_id} agent={agent} />
        ))}
      </div>

      {/* Footer with judge info (optional) */}
      {debate.config.judge_config && (
        <div className="flex-shrink-0 px-6 py-4 border-t border-slate-800 bg-slate-950">
          <div className="text-sm">
            <p className="text-slate-500">Judge:</p>
            <p className="text-slate-300 mt-1 font-medium">
              {debate.config.judge_config.name}
            </p>
            <p className="text-slate-500 text-xs mt-0.5">
              {debate.config.judge_config.llm_config.model_name}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
