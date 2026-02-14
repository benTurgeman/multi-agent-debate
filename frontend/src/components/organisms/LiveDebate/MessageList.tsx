/**
 * MessageList - Displays debate messages in real-time
 * Handles auto-scrolling, thinking indicators, and message animations
 */

import React from 'react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageBubble, ThinkingIndicator } from '../../molecules';
import { Message } from '../../../types';
import { useAutoScroll } from '../../../hooks';
import { useDebateStateStore } from '../../../stores';

export interface MessageListProps {
  /**
   * List of messages to display
   */
  messages: Message[];

  /**
   * Enable auto-scroll to latest message
   */
  autoScroll?: boolean;

  /**
   * Show thinking indicators for agents
   */
  showThinking?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Helper to normalize stance string to valid type
 */
function normalizeStance(stance: string): 'pro' | 'con' | 'judge' {
  const lower = stance.toLowerCase();
  if (lower === 'pro' || lower === 'for') return 'pro';
  if (lower === 'con' || lower === 'against') return 'con';
  return 'judge';
}

/**
 * Determine message alignment based on stance
 * Pro messages align left, Con messages align right
 */
function getMessageAlign(stance: string): 'left' | 'right' {
  const normalized = normalizeStance(stance);
  return normalized === 'pro' ? 'left' : 'right';
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  autoScroll = true,
  showThinking = true,
  className,
}) => {
  // Get thinking agents from store
  const thinkingAgents = useDebateStateStore((state) => state.thinkingAgents);

  // Auto-scroll when messages change
  const containerRef = useAutoScroll<HTMLDivElement>(
    [messages.length, thinkingAgents.length],
    {
      enabled: autoScroll,
      behavior: 'smooth',
    }
  );

  return (
    <div
      ref={containerRef}
      className={clsx(
        'flex-1 overflow-y-auto',
        'px-6 py-4',
        'scroll-smooth',
        className
      )}
    >
      <div className="flex flex-col gap-6">
        {/* Render all messages */}
        <AnimatePresence initial={false}>
          {messages.map((message, index) => {
            const stance = normalizeStance(message.stance);
            const align = getMessageAlign(message.stance);

            return (
              <motion.div
                key={`${message.agent_id}-${message.turn_number}-${index}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <MessageBubble
                  agentName={message.agent_name}
                  stance={stance}
                  content={message.content}
                  timestamp={message.timestamp}
                  roundNumber={message.round_number + 1} // Convert 0-indexed to 1-indexed
                  align={align}
                />
              </motion.div>
            );
          })}
        </AnimatePresence>

        {/* Show thinking indicators for agents currently thinking */}
        {showThinking && thinkingAgents.length > 0 && (
          <AnimatePresence>
            {thinkingAgents.map((agent) => (
              <ThinkingIndicator
                key={agent.agent_id}
                agentName={agent.agent_name}
                stance="pro" // Default to pro, could be enhanced to track actual stance
              />
            ))}
          </AnimatePresence>
        )}

        {/* Empty state when no messages */}
        {messages.length === 0 && thinkingAgents.length === 0 && (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <p className="text-slate-400 text-lg">No messages yet</p>
              <p className="text-slate-500 text-sm mt-2">
                Start the debate to see agent responses
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
