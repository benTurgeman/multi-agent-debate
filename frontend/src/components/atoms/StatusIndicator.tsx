import React from 'react';
import clsx from 'clsx';

export type StatusType = 'connected' | 'connecting' | 'disconnected' | 'error';

export interface StatusIndicatorProps {
  /**
   * Current connection status
   */
  status: StatusType;

  /**
   * Optional label to display next to the indicator
   */
  label?: string;

  /**
   * Show animated pulse for active states
   */
  animated?: boolean;

  /**
   * Size of the indicator
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  animated = true,
  size = 'md',
  className,
}) => {
  const dotSize = clsx({
    'w-2 h-2': size === 'sm',
    'w-3 h-3': size === 'md',
    'w-4 h-4': size === 'lg',
  });

  const statusColor = clsx({
    'bg-green-500': status === 'connected',
    'bg-yellow-500': status === 'connecting',
    'bg-slate-500': status === 'disconnected',
    'bg-red-500': status === 'error',
  });

  const statusLabel = label || {
    connected: 'Connected',
    connecting: 'Connecting...',
    disconnected: 'Disconnected',
    error: 'Connection Error',
  }[status];

  return (
    <div
      className={clsx('inline-flex items-center gap-2', className)}
      role="status"
      aria-label={statusLabel}
    >
      <div className="relative">
        {/* Main dot */}
        <div className={clsx('rounded-full', dotSize, statusColor)} />

        {/* Animated pulse ring */}
        {animated && (status === 'connected' || status === 'connecting') && (
          <div
            className={clsx(
              'absolute inset-0 rounded-full animate-ping opacity-75',
              statusColor
            )}
          />
        )}
      </div>

      {statusLabel && (
        <span className="text-sm text-slate-300">{statusLabel}</span>
      )}
    </div>
  );
};
