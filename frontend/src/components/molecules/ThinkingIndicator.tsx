import React from 'react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

export interface ThinkingIndicatorProps {
  /**
   * Agent name who is thinking
   */
  agentName: string;

  /**
   * Agent's debate stance
   */
  stance: 'pro' | 'con' | 'judge';

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({
  agentName,
  stance,
  className,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={clsx('flex items-center gap-3 p-4', className)}
    >
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

      <div className="flex items-center gap-2">
        <span className="text-sm text-slate-400">
          {agentName} is thinking
        </span>

        {/* Animated dots */}
        <div className="flex items-center gap-1">
          {[0, 1, 2].map((index) => (
            <motion.div
              key={index}
              className="w-1.5 h-1.5 rounded-full bg-slate-500"
              animate={{
                opacity: [0.3, 1, 0.3],
                scale: [1, 1.2, 1],
              }}
              transition={{
                duration: 1.2,
                repeat: Infinity,
                delay: index * 0.2,
              }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
};
