/**
 * WinnerAnnouncement - Displays the debate winner with celebration animation
 */

import React from 'react';
import clsx from 'clsx';
import { motion } from 'framer-motion';
import { Trophy } from 'lucide-react';
import { Badge } from '../../atoms';

export interface WinnerAnnouncementProps {
  /**
   * Winner's name
   */
  winnerName: string;

  /**
   * Winner's score
   */
  winnerScore: number;

  /**
   * Winner's stance
   */
  winnerStance?: string;

  /**
   * Runner-up score (for comparison)
   */
  runnerUpScore?: number;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Map stance string to badge variant
 */
function getStanceVariant(stance?: string): 'pro' | 'con' | 'judge' {
  if (!stance) return 'judge';
  const lowerStance = stance.toLowerCase();
  if (lowerStance.includes('pro') || lowerStance.includes('for')) {
    return 'pro';
  }
  if (lowerStance.includes('con') || lowerStance.includes('against')) {
    return 'con';
  }
  return 'judge';
}

export const WinnerAnnouncement: React.FC<WinnerAnnouncementProps> = ({
  winnerName,
  winnerScore,
  winnerStance,
  runnerUpScore,
  className,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className={clsx(
        'bg-gradient-to-br from-purple-900/30 to-slate-900/30',
        'rounded-lg border border-purple-500/30 p-8',
        'text-center',
        className
      )}
    >
      {/* Trophy icon */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        className="flex justify-center mb-4"
      >
        <div className="relative">
          <Trophy className="w-16 h-16 text-yellow-500" strokeWidth={1.5} />
          {/* Glow effect */}
          <div className="absolute inset-0 blur-xl bg-yellow-500/30 rounded-full" />
        </div>
      </motion.div>

      {/* Winner announcement */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.5 }}
      >
        <h2 className="text-2xl font-bold text-slate-200 mb-2">
          Winner
        </h2>

        {/* Winner name and stance */}
        <div className="flex items-center justify-center gap-3 mb-4">
          <h3 className="text-3xl font-bold text-purple-400">
            {winnerName}
          </h3>
          {winnerStance && (
            <Badge variant={getStanceVariant(winnerStance)} size="md">
              {winnerStance}
            </Badge>
          )}
        </div>

        {/* Score display */}
        <div className="flex items-center justify-center gap-4">
          <div className="text-center">
            <div className="text-5xl font-bold text-purple-400">
              {winnerScore.toFixed(1)}
            </div>
            <div className="text-sm text-slate-400 mt-1">Score</div>
          </div>

          {runnerUpScore !== undefined && (
            <>
              <div className="text-2xl text-slate-600 font-bold">vs</div>
              <div className="text-center">
                <div className="text-3xl font-bold text-slate-500">
                  {runnerUpScore.toFixed(1)}
                </div>
                <div className="text-sm text-slate-500 mt-1">Runner-up</div>
              </div>
            </>
          )}
        </div>
      </motion.div>

      {/* Decorative particles */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 1 }}
        className="absolute inset-0 pointer-events-none overflow-hidden rounded-lg"
      >
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-purple-400 rounded-full"
            style={{
              left: `${20 + i * 15}%`,
              top: '50%',
            }}
            animate={{
              y: [-20, -60],
              opacity: [1, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.2,
              ease: 'easeOut',
            }}
          />
        ))}
      </motion.div>
    </motion.div>
  );
};
