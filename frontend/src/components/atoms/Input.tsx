import React from 'react';
import clsx from 'clsx';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /**
   * Label text for the input
   */
  label?: string;

  /**
   * Error message to display
   */
  error?: string;

  /**
   * Helper text to display below the input
   */
  helperText?: string;

  /**
   * Full width input
   */
  fullWidth?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, fullWidth = false, className, id, ...props }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div className={clsx('flex flex-col gap-1.5', { 'w-full': fullWidth })}>
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium text-slate-200"
          >
            {label}
          </label>
        )}

        <input
          ref={ref}
          id={inputId}
          className={clsx(
            // Base styles
            'rounded-lg border px-3 py-2',
            'bg-slate-800 text-slate-200',
            'placeholder:text-slate-500',
            'transition-colors duration-200',
            'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900',

            // Border and focus states
            {
              'border-slate-700 focus:border-blue-500 focus:ring-blue-500': !error,
              'border-red-500 focus:border-red-500 focus:ring-red-500': error,
            },

            // Disabled state
            'disabled:opacity-50 disabled:cursor-not-allowed',

            className
          )}
          {...props}
        />

        {error && (
          <p className="text-sm text-red-500" role="alert">
            {error}
          </p>
        )}

        {helperText && !error && (
          <p className="text-sm text-slate-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
