import React from 'react';
import clsx from 'clsx';
import { LoadingSpinner } from './LoadingSpinner';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Visual variant of the button
   */
  variant?: 'primary' | 'secondary' | 'danger';

  /**
   * Loading state - shows spinner and disables button
   */
  isLoading?: boolean;

  /**
   * Full width button
   */
  fullWidth?: boolean;

  /**
   * Button size
   */
  size?: 'sm' | 'md' | 'lg';
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  isLoading = false,
  fullWidth = false,
  size = 'md',
  className,
  children,
  disabled,
  ...props
}) => {
  const baseStyles = clsx(
    // Base styles
    'inline-flex items-center justify-center gap-2',
    'font-medium rounded-lg transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900',
    'disabled:opacity-50 disabled:cursor-not-allowed',

    // Size variants
    {
      'px-3 py-1.5 text-sm': size === 'sm',
      'px-4 py-2 text-base': size === 'md',
      'px-6 py-3 text-lg': size === 'lg',
    },

    // Width
    {
      'w-full': fullWidth,
    }
  );

  const variantStyles = clsx({
    // Primary variant
    'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500':
      variant === 'primary',

    // Secondary variant
    'bg-slate-700 hover:bg-slate-600 text-slate-200 focus:ring-slate-500':
      variant === 'secondary',

    // Danger variant
    'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500':
      variant === 'danger',
  });

  return (
    <button
      className={clsx(baseStyles, variantStyles, className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <LoadingSpinner size="sm" />}
      {children}
    </button>
  );
};
