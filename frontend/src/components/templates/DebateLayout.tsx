import React from 'react';
import clsx from 'clsx';

export interface DebateLayoutProps {
  /**
   * Header component
   */
  header: React.ReactNode;

  /**
   * Left panel content (config)
   */
  leftPanel: React.ReactNode;

  /**
   * Center panel content (live debate)
   */
  centerPanel: React.ReactNode;

  /**
   * Right panel content (participants/stats)
   */
  rightPanel: React.ReactNode;

  /**
   * Bottom panel content (verdict - optional)
   */
  bottomPanel?: React.ReactNode;

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const DebateLayout: React.FC<DebateLayoutProps> = ({
  header,
  leftPanel,
  centerPanel,
  rightPanel,
  bottomPanel,
  className,
}) => {
  return (
    <div className={clsx('min-h-screen bg-slate-900 flex flex-col', className)}>
      {/* Header */}
      {header}

      {/* Main content area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel - Configuration (25%) */}
        <aside className="w-1/4 border-r border-slate-700 overflow-y-auto">
          <div className="p-6">{leftPanel}</div>
        </aside>

        {/* Center panel - Live Debate (50%) */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-6">{centerPanel}</div>
        </main>

        {/* Right panel - Participants (25%) */}
        <aside className="w-1/4 border-l border-slate-700 overflow-y-auto">
          <div className="p-6">{rightPanel}</div>
        </aside>
      </div>

      {/* Bottom panel - Verdict (full width, conditional) */}
      {bottomPanel && (
        <div className="border-t border-slate-700">
          {bottomPanel}
        </div>
      )}
    </div>
  );
};
