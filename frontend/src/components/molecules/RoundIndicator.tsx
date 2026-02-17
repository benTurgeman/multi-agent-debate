import React from 'react';
import clsx from 'clsx';

export interface RoundIndicatorProps {
  /**
   * Current round number (1-indexed for display)
   */
  currentRound: number;

  /**
   * Total number of rounds
   */
  totalRounds: number;

  /**
   * Optional current turn indicator
   */
  currentTurn?: string;

  /**
   * Size variant
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const RoundIndicator: React.FC<RoundIndicatorProps> = ({
  currentRound,
  totalRounds,
  currentTurn,
  size = 'md',
  className,
}) => {
  const textSize = clsx({
    'text-sm': size === 'sm',
    'text-base': size === 'md',
    'text-lg': size === 'lg',
  });

  return (
    <div
      className={clsx(
        'inline-flex items-center gap-3 px-4 py-2',
        'rounded-lg bg-slate-800 border border-slate-700',
        className
      )}
    >
      {/* Round progress */}
      <div className="flex items-center gap-2">
        <span className={clsx('font-semibold text-slate-200', textSize)}>
          Round {currentRound} of {totalRounds}
        </span>

        {/* Progress bar */}
        <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 transition-all duration-300"
            style={{ width: `${(currentRound / totalRounds) * 100}%` }}
          />
        </div>
      </div>

      {/* Current turn indicator */}
      {currentTurn && (
        <>
          <div className="w-px h-4 bg-slate-700" />
          <span className={clsx('text-slate-400', textSize)}>
            {currentTurn}'s Turn
          </span>
        </>
      )}
    </div>
  );
};
