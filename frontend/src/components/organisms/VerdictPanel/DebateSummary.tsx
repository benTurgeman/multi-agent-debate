/**
 * DebateSummary - Displays judge's overall debate summary
 */

import React from 'react';
import clsx from 'clsx';

export interface DebateSummaryProps {
  /**
   * Judge's overall summary of the debate
   */
  summary: string;

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const DebateSummary: React.FC<DebateSummaryProps> = ({
  summary,
  className,
}) => {
  return (
    <div
      className={clsx(
        'bg-slate-800 rounded-lg border border-slate-700 p-6',
        className
      )}
    >
      <h3 className="text-lg font-semibold text-slate-200 mb-3">
        Judge's Summary
      </h3>
      <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
        {summary}
      </p>
    </div>
  );
};
