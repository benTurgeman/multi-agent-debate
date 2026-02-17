/**
 * ScoreCards - Displays score cards for each agent
 */

import React from 'react';
import clsx from 'clsx';
import { motion } from 'framer-motion';
import { Badge } from '../../atoms';
import type { AgentScore } from '../../../types';

export interface ScoreCardsProps {
  /**
   * Agent scores from judge result
   */
  scores: AgentScore[];

  /**
   * Agent stance mapping (agent_id -> stance)
   */
  agentStances?: Record<string, string>;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Map stance string to badge variant
 */
function getStanceVariant(stance?: string): 'pro' | 'con' | 'judge' | 'neutral' {
  if (!stance) return 'neutral';
  const lowerStance = stance.toLowerCase();
  if (lowerStance.includes('pro') || lowerStance.includes('for')) {
    return 'pro';
  }
  if (lowerStance.includes('con') || lowerStance.includes('against')) {
    return 'con';
  }
  return 'neutral';
}

/**
 * Individual score card component
 */
const ScoreCard: React.FC<{
  score: AgentScore;
  stance?: string;
  index: number;
}> = ({ score, stance, index }) => {
  const percentage = (score.score / 10) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className="bg-slate-800 rounded-lg border border-slate-700 p-5"
    >
      {/* Header with name and stance */}
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold text-slate-200 truncate">
          {score.agent_name}
        </h4>
        {stance && (
          <Badge variant={getStanceVariant(stance)} size="sm">
            {stance}
          </Badge>
        )}
      </div>

      {/* Score display */}
      <div className="mb-4">
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-4xl font-bold text-purple-400">
            {score.score.toFixed(1)}
          </span>
          <span className="text-lg text-slate-500">/ 10</span>
        </div>

        {/* Progress bar */}
        <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ delay: index * 0.1 + 0.2, duration: 0.8, ease: 'easeOut' }}
            className={clsx(
              'h-full rounded-full',
              percentage >= 80
                ? 'bg-green-500'
                : percentage >= 60
                ? 'bg-purple-500'
                : percentage >= 40
                ? 'bg-yellow-500'
                : 'bg-red-500'
            )}
          />
        </div>
      </div>

      {/* Judge's reasoning */}
      <div>
        <p className="text-sm text-slate-500 mb-1 font-medium">
          Judge's Reasoning:
        </p>
        <p className="text-sm text-slate-300 leading-relaxed">
          {score.reasoning}
        </p>
      </div>
    </motion.div>
  );
};

export const ScoreCards: React.FC<ScoreCardsProps> = ({
  scores,
  agentStances = {},
  className,
}) => {
  return (
    <div className={clsx('grid gap-4', className)}>
      {/* Header */}
      <h3 className="text-lg font-semibold text-slate-200">
        Agent Scores
      </h3>

      {/* Score cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {scores.map((score, index) => (
          <ScoreCard
            key={score.agent_id}
            score={score}
            stance={agentStances[score.agent_id]}
            index={index}
          />
        ))}
      </div>
    </div>
  );
};
