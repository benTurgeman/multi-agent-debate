import React from 'react';
import clsx from 'clsx';
import { Badge, StatusIndicator, type StatusType } from '../atoms';

export interface AgentCardProps {
  /**
   * Agent name
   */
  name: string;

  /**
   * Agent's debate stance
   */
  stance: 'pro' | 'con' | 'judge';

  /**
   * LLM model name
   */
  model: string;

  /**
   * Current agent status
   */
  status?: StatusType;

  /**
   * Number of messages sent by this agent
   */
  messageCount?: number;

  /**
   * Optional score (shown after debate completion)
   */
  score?: number;

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const AgentCard: React.FC<AgentCardProps> = ({
  name,
  stance,
  model,
  status,
  messageCount,
  score,
  className,
}) => {
  return (
    <div
      className={clsx(
        'rounded-lg border border-slate-700 bg-slate-800 p-4',
        'transition-all duration-200 hover:border-slate-600',
        className
      )}
    >
      {/* Header with name and badge */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <h3 className="text-lg font-semibold text-slate-200 truncate">
          {name}
        </h3>
        <Badge variant={stance} size="sm">
          {stance.charAt(0).toUpperCase() + stance.slice(1)}
        </Badge>
      </div>

      {/* Model info */}
      <p className="text-sm text-slate-400 mb-3 truncate" title={model}>
        {model}
      </p>

      {/* Status and stats */}
      <div className="flex flex-col gap-2">
        {status && (
          <StatusIndicator status={status} size="sm" animated={status === 'connecting'} />
        )}

        <div className="flex items-center justify-between text-sm">
          {messageCount !== undefined && (
            <span className="text-slate-400">
              Messages: <span className="text-slate-200 font-medium">{messageCount}</span>
            </span>
          )}

          {score !== undefined && (
            <span className="text-slate-400">
              Score: <span className="text-slate-200 font-medium">{score}/10</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
