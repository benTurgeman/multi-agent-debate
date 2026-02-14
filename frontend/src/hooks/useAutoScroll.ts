/**
 * Auto-scroll hook for scrollable containers
 * Automatically scrolls to bottom when dependencies change (e.g., new messages)
 */

import { useEffect, useRef } from 'react';

interface UseAutoScrollOptions {
  /** Enable or disable auto-scroll */
  enabled?: boolean;
  /** Scroll behavior (smooth or instant) */
  behavior?: ScrollBehavior;
  /** Offset from bottom to consider "at bottom" */
  threshold?: number;
}

/**
 * Hook for auto-scrolling a container to the bottom
 *
 * @param dependencies - Array of dependencies that trigger scroll (e.g., [messages.length])
 * @param options - Configuration options
 * @returns Ref to attach to the scrollable container
 *
 * @example
 * const containerRef = useAutoScroll([messages.length], { behavior: 'smooth' });
 * return <div ref={containerRef}>...</div>;
 */
export function useAutoScroll<T extends HTMLElement = HTMLDivElement>(
  dependencies: any[],
  options: UseAutoScrollOptions = {}
): React.RefObject<T> {
  const {
    enabled = true,
    behavior = 'smooth',
    threshold = 100,
  } = options;

  const containerRef = useRef<T>(null);
  const isUserScrollingRef = useRef(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Check if user has scrolled away from bottom
   */
  const checkScrollPosition = () => {
    if (!containerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

    // If user scrolled more than threshold away from bottom, disable auto-scroll
    isUserScrollingRef.current = distanceFromBottom > threshold;
  };

  /**
   * Scroll to bottom of container
   */
  const scrollToBottom = () => {
    if (!containerRef.current || !enabled) return;

    // Only auto-scroll if user hasn't manually scrolled away
    if (!isUserScrollingRef.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior,
      });
    }
  };

  /**
   * Listen for scroll events to detect manual scrolling
   */
  useEffect(() => {
    const container = containerRef.current;
    if (!container || !enabled) return;

    const handleScroll = () => {
      // Clear existing timeout
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }

      // Debounce scroll position check
      scrollTimeoutRef.current = setTimeout(() => {
        checkScrollPosition();
      }, 150);
    };

    container.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      container.removeEventListener('scroll', handleScroll);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [enabled]);

  /**
   * Auto-scroll when dependencies change
   */
  useEffect(() => {
    if (enabled) {
      scrollToBottom();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return containerRef;
}
