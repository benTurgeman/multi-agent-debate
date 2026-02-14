import React from 'react';
import clsx from 'clsx';
import { Button, StatusIndicator, type StatusType } from '../atoms';

export interface HeaderProps {
  /**
   * Connection status
   */
  connectionStatus?: StatusType;

  /**
   * Whether debate is in progress
   */
  isDebateActive?: boolean;

  /**
   * Whether debate is completed
   */
  isDebateComplete?: boolean;

  /**
   * Handler for start debate action
   */
  onStart?: () => void;

  /**
   * Handler for export action
   */
  onExport?: () => void;

  /**
   * Loading state for start button
   */
  isStarting?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const Header: React.FC<HeaderProps> = ({
  connectionStatus,
  isDebateActive = false,
  isDebateComplete = false,
  onStart,
  onExport,
  isStarting = false,
  className,
}) => {
  return (
    <header
      className={clsx(
        'w-full border-b border-slate-700 bg-slate-900',
        'px-6 py-4',
        className
      )}
    >
      <div className="flex items-center justify-between">
        {/* Left: App title */}
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-slate-100">
            AI Debate Arena
          </h1>

          {connectionStatus && (
            <StatusIndicator status={connectionStatus} size="sm" />
          )}
        </div>

        {/* Right: Action buttons */}
        <div className="flex items-center gap-3">
          {/* Start Debate button */}
          {!isDebateActive && !isDebateComplete && (
            <Button
              variant="primary"
              onClick={onStart}
              isLoading={isStarting}
              disabled={!onStart}
            >
              Start Debate
            </Button>
          )}

          {/* Export button (only show when debate is complete) */}
          {isDebateComplete && (
            <Button
              variant="secondary"
              onClick={onExport}
              disabled={!onExport}
            >
              Export Results
            </Button>
          )}
        </div>
      </div>
    </header>
  );
};
