/**
 * VerdictPanel - Bottom panel showing debate results and verdict
 * Slides up when debate completes
 */

import React, { useState } from 'react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu } from '@headlessui/react';
import { Download, ChevronDown, FileJson, FileText, FileType } from 'lucide-react';
import { Button } from '../../atoms';
import { WinnerAnnouncement } from './WinnerAnnouncement';
import { ScoreCards } from './ScoreCards';
import { KeyArguments } from './KeyArguments';
import { DebateSummary } from './DebateSummary';
import { useDebateStateStore } from '../../../stores';
import { debatesApi, type ExportFormat } from '../../../api/debates';

export interface VerdictPanelProps {
  /**
   * Whether to show the panel
   */
  show: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Export menu item component
 */
const ExportMenuItem: React.FC<{
  format: ExportFormat;
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
}> = ({ label, icon, onClick }) => (
  <Menu.Item>
    {({ active }) => (
      <button
        onClick={onClick}
        className={clsx(
          'w-full flex items-center gap-3 px-4 py-2.5 text-sm',
          'transition-colors duration-150',
          active
            ? 'bg-slate-700 text-slate-100'
            : 'text-slate-300'
        )}
      >
        <span className="w-5 h-5 flex items-center justify-center">
          {icon}
        </span>
        <span>{label}</span>
      </button>
    )}
  </Menu.Item>
);

export const VerdictPanel: React.FC<VerdictPanelProps> = ({
  show,
  className,
}) => {
  const debate = useDebateStateStore((state) => state.debate);
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Don't render if no debate or no judge result
  if (!debate || !debate.judge_result) {
    return null;
  }

  const { judge_result } = debate;

  // Get agent stances for score cards
  const agentStances = debate.config.agents.reduce(
    (acc, agent) => {
      acc[agent.agent_id] = agent.stance;
      return acc;
    },
    {} as Record<string, string>
  );

  // Get winner's stance
  const winnerAgent = debate.config.agents.find(
    (a) => a.agent_id === judge_result.winner_id
  );

  // Get runner-up score
  const sortedScores = [...judge_result.agent_scores].sort((a, b) => b.score - a.score);
  const runnerUpScore = sortedScores[1]?.score;

  /**
   * Handle export with error handling
   */
  const handleExport = async (format: ExportFormat) => {
    if (!debate) return;

    setIsExporting(true);
    setExportError(null);

    try {
      await debatesApi.downloadExport(
        debate.debate_id,
        format,
        `debate-${debate.debate_id}.${format}`
      );
    } catch (error) {
      console.error('Export failed:', error);
      setExportError(error instanceof Error ? error.message : 'Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ y: '100%' }}
          animate={{ y: 0 }}
          exit={{ y: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className={clsx(
            'fixed bottom-0 left-0 right-0',
            'bg-slate-950 border-t border-slate-800',
            'overflow-y-auto',
            'shadow-2xl',
            className
          )}
          style={{ maxHeight: '80vh' }}
        >
          <div className="max-w-7xl mx-auto p-6 space-y-6">
            {/* Header with close and export buttons */}
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-slate-200">
                Debate Results
              </h2>

              {/* Export dropdown */}
              <Menu as="div" className="relative">
                <Menu.Button
                  as={Button}
                  variant="secondary"
                  disabled={isExporting}
                  className="flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  {isExporting ? 'Exporting...' : 'Export Results'}
                  <ChevronDown className="w-4 h-4" />
                </Menu.Button>

                <Menu.Items
                  className={clsx(
                    'absolute right-0 mt-2 w-56',
                    'bg-slate-800 border border-slate-700 rounded-lg',
                    'shadow-xl overflow-hidden',
                    'focus:outline-none z-10'
                  )}
                >
                  <div className="py-1">
                    <ExportMenuItem
                      format="json"
                      label="Export as JSON"
                      icon={<FileJson className="w-4 h-4" />}
                      onClick={() => handleExport('json')}
                    />
                    <ExportMenuItem
                      format="markdown"
                      label="Export as Markdown"
                      icon={<FileType className="w-4 h-4" />}
                      onClick={() => handleExport('markdown')}
                    />
                    <ExportMenuItem
                      format="text"
                      label="Export as Text"
                      icon={<FileText className="w-4 h-4" />}
                      onClick={() => handleExport('text')}
                    />
                  </div>
                </Menu.Items>
              </Menu>
            </div>

            {/* Export error message */}
            {exportError && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                <p className="text-sm text-red-400">
                  Export failed: {exportError}
                </p>
              </div>
            )}

            {/* Winner announcement */}
            <WinnerAnnouncement
              winnerName={judge_result.winner_name}
              winnerScore={judge_result.agent_scores.find(
                (s) => s.agent_id === judge_result.winner_id
              )?.score || 0}
              winnerStance={winnerAgent?.stance}
              runnerUpScore={runnerUpScore}
            />

            {/* Score cards */}
            <ScoreCards
              scores={judge_result.agent_scores}
              agentStances={agentStances}
            />

            {/* Key arguments */}
            {judge_result.key_arguments.length > 0 && (
              <KeyArguments arguments={judge_result.key_arguments} />
            )}

            {/* Judge's summary */}
            <DebateSummary summary={judge_result.summary} />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
