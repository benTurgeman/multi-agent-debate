import React from 'react';
import clsx from 'clsx';

export interface LoadingSpinnerProps {
  /**
   * Size of the spinner
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Color of the spinner
   */
  color?: 'primary' | 'white' | 'slate';

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'white',
  className,
}) => {
  const sizeStyles = clsx({
    'w-4 h-4': size === 'sm',
    'w-6 h-6': size === 'md',
    'w-8 h-8': size === 'lg',
  });

  const colorStyles = clsx({
    'border-blue-600': color === 'primary',
    'border-white': color === 'white',
    'border-slate-400': color === 'slate',
  });

  return (
    <div
      className={clsx(
        'animate-spin rounded-full border-2 border-t-transparent',
        sizeStyles,
        colorStyles,
        className
      )}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};
