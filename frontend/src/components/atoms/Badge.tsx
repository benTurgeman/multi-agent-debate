import React from 'react';
import clsx from 'clsx';

export interface BadgeProps {
  /**
   * Badge variant - corresponds to debate roles
   */
  variant: 'pro' | 'con' | 'judge' | 'neutral';

  /**
   * Badge content
   */
  children: React.ReactNode;

  /**
   * Size of the badge
   */
  size?: 'sm' | 'md';

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant,
  children,
  size = 'md',
  className,
}) => {
  const baseStyles = clsx(
    'inline-flex items-center justify-center',
    'font-medium rounded-full',
    'transition-colors duration-200',

    // Size variants
    {
      'px-2 py-0.5 text-xs': size === 'sm',
      'px-3 py-1 text-sm': size === 'md',
    }
  );

  const variantStyles = clsx({
    // Pro variant (green)
    'bg-green-500/10 text-green-500 border border-green-500/20':
      variant === 'pro',

    // Con variant (red)
    'bg-red-500/10 text-red-500 border border-red-500/20':
      variant === 'con',

    // Judge variant (purple)
    'bg-purple-500/10 text-purple-500 border border-purple-500/20':
      variant === 'judge',

    // Neutral variant (slate)
    'bg-slate-700/50 text-slate-300 border border-slate-600':
      variant === 'neutral',
  });

  return (
    <span className={clsx(baseStyles, variantStyles, className)}>
      {children}
    </span>
  );
};
