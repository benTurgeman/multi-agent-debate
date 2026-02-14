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

      {/* Main content area - responsive layout */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left panel - Configuration (25% on desktop, full width on mobile/tablet) */}
        <aside
          className={clsx(
            'border-slate-700 overflow-y-auto',
            // Mobile/Tablet: full width, border bottom
            'w-full border-b',
            // Desktop (lg+): 25% width, border right
            'lg:w-1/4 lg:border-r lg:border-b-0'
          )}
        >
          <div className="p-4 md:p-6">{leftPanel}</div>
        </aside>

        {/* Center + Right panel container - stack on tablet/mobile */}
        <div className="flex-1 flex flex-col md:flex-col lg:flex-row overflow-hidden">
          {/* Center panel - Live Debate (50% on desktop, full width on mobile/tablet) */}
          <main
            className={clsx(
              'overflow-y-auto',
              // Mobile/Tablet: full width
              'w-full',
              // Desktop (lg+): 50% width (flex-1 takes remaining space)
              'lg:flex-1'
            )}
          >
            <div className="p-4 md:p-6">{centerPanel}</div>
          </main>

          {/* Right panel - Participants (25% on desktop, full width on mobile/tablet) */}
          <aside
            className={clsx(
              'border-slate-700 overflow-y-auto',
              // Mobile/Tablet: full width, border top
              'w-full border-t',
              // Desktop (lg+): 25% width, border left
              'lg:w-1/4 lg:border-l lg:border-t-0'
            )}
          >
            <div className="p-4 md:p-6">{rightPanel}</div>
          </aside>
        </div>
      </div>

      {/* Bottom panel - Verdict (full width, conditional) */}
      {bottomPanel && <div className="border-t border-slate-700">{bottomPanel}</div>}
    </div>
  );
};
