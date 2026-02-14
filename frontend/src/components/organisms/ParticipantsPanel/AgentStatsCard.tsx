/**
 * AgentStatsCard - Shows individual agent stats during debate
 * Displays agent info, current status, and message count
 */

import React from 'react';
import { AgentConfig } from '../../../types';
import { AgentCard } from '../../molecules';
import { useDebateStateStore } from '../../../stores';
import { DebateStatus } from '../../../types';

export interface AgentStatsCardProps {
  /**
   * Agent configuration
   */
  agent: AgentConfig;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get agent status text based on debate state
 */
function getAgentStatus(
  agentId: string,
  debateStatus: DebateStatus,
  isThinking: boolean,
  isCurrentTurn: boolean
): string {
  // If debate is completed, all agents are done
  if (debateStatus === DebateStatus.COMPLETED) {
    return 'Completed';
  }

  // If debate failed, show error state
  if (debateStatus === DebateStatus.FAILED) {
    return 'Stopped';
  }

  // If agent is currently thinking
  if (isThinking) {
    return 'Thinking...';
  }

  // If it's this agent's turn
  if (isCurrentTurn) {
    return 'Active';
  }

  // If debate hasn't started yet
  if (debateStatus === DebateStatus.CREATED) {
    return 'Ready';
  }

  // Otherwise, agent is waiting
  return 'Waiting...';
}

/**
 * Map stance string to badge variant
 */
function getStanceVariant(stance: string): 'pro' | 'con' | 'judge' {
  const lowerStance = stance.toLowerCase();
  if (lowerStance.includes('pro') || lowerStance.includes('for')) {
    return 'pro';
  }
  if (lowerStance.includes('con') || lowerStance.includes('against')) {
    return 'con';
  }
  return 'judge';
}

export const AgentStatsCard: React.FC<AgentStatsCardProps> = ({
  agent,
  className,
}) => {
  // Get debate state
  const debate = useDebateStateStore((state) => state.debate);
  const thinkingAgents = useDebateStateStore((state) => state.thinkingAgents);
  const getCurrentAgent = useDebateStateStore((state) => state.getCurrentAgent);
  const getAgentMessageCount = useDebateStateStore(
    (state) => state.getAgentMessageCount
  );

  // Compute agent-specific state
  const isThinking = thinkingAgents.some((a) => a.agent_id === agent.agent_id);
  const currentAgentId = getCurrentAgent();
  const isCurrentTurn = currentAgentId === agent.agent_id;
  const messageCount = getAgentMessageCount(agent.agent_id);
  const status = getAgentStatus(
    agent.agent_id,
    debate?.status || DebateStatus.CREATED,
    isThinking,
    isCurrentTurn
  );

  // Get score if debate is completed
  const score =
    debate?.status === DebateStatus.COMPLETED && debate.judge_result
      ? debate.judge_result.agent_scores.find((s) => s.agent_id === agent.agent_id)
          ?.score
      : undefined;

  // Extract model name for display
  const modelName = agent.llm_config.model_name;

  return (
    <div className={className}>
      <AgentCard
        name={agent.name}
        stance={getStanceVariant(agent.stance)}
        model={modelName}
        messageCount={messageCount}
        score={score}
      />

      {/* Custom status text below the card */}
      <div className="mt-2 px-2">
        <div className="flex items-center gap-2">
          {/* Status dot with color based on state */}
          <div
            className={`w-2 h-2 rounded-full ${
              status === 'Thinking...'
                ? 'bg-blue-500 animate-pulse'
                : status === 'Active'
                ? 'bg-green-500'
                : status === 'Completed'
                ? 'bg-slate-500'
                : status === 'Stopped'
                ? 'bg-red-500'
                : 'bg-slate-600'
            }`}
          />
          <span
            className={`text-sm ${
              status === 'Thinking...' || status === 'Active'
                ? 'text-slate-300 font-medium'
                : 'text-slate-500'
            }`}
          >
            {status}
          </span>
        </div>
      </div>
    </div>
  );
};
