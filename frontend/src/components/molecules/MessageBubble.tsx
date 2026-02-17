import React from 'react';
import clsx from 'clsx';
import { format } from 'date-fns';
import { Badge } from '../atoms';

export interface MessageBubbleProps {
  /**
   * Agent name
   */
  agentName: string;

  /**
   * Agent's debate stance
   */
  stance: 'pro' | 'con' | 'judge';

  /**
   * Message content
   */
  content: string;

  /**
   * Message timestamp
   */
  timestamp: string | Date;

  /**
   * Round number
   */
  roundNumber?: number;

  /**
   * Align message to left or right
   */
  align?: 'left' | 'right';

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  agentName,
  stance,
  content,
  timestamp,
  roundNumber,
  align = 'left',
  className,
}) => {
  const formattedTime = typeof timestamp === 'string'
    ? format(new Date(timestamp), 'h:mm a')
    : format(timestamp, 'h:mm a');

  return (
    <div
      className={clsx(
        'flex flex-col gap-2 max-w-3xl',
        {
          'items-start': align === 'left',
          'items-end ml-auto': align === 'right',
        },
        className
      )}
    >
      {/* Header with agent name and badge */}
      <div className="flex items-center gap-2">
        {/* Avatar circle with initial */}
        <div
          className={clsx(
            'w-8 h-8 rounded-full flex items-center justify-center',
            'text-white font-semibold text-sm',
            {
              'bg-green-500': stance === 'pro',
              'bg-red-500': stance === 'con',
              'bg-purple-500': stance === 'judge',
            }
          )}
        >
          {agentName.charAt(0).toUpperCase()}
        </div>

        <span className="text-sm font-medium text-slate-200">{agentName}</span>
        <Badge variant={stance} size="sm">
          {stance.charAt(0).toUpperCase() + stance.slice(1)}
        </Badge>

        {roundNumber !== undefined && (
          <span className="text-xs text-slate-500">Round {roundNumber}</span>
        )}
      </div>

      {/* Message content */}
      <div
        className={clsx(
          'rounded-lg px-4 py-3',
          'bg-slate-800 border border-slate-700',
          'w-full'
        )}
      >
        <p className="text-slate-200 whitespace-pre-wrap break-words">
          {content}
        </p>
      </div>

      {/* Timestamp */}
      <span className="text-xs text-slate-500">{formattedTime}</span>
    </div>
  );
};
