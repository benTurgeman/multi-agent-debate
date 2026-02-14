import React from 'react';
import clsx from 'clsx';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  /**
   * Label text for the select
   */
  label?: string;

  /**
   * Error message to display
   */
  error?: string;

  /**
   * Helper text to display below the select
   */
  helperText?: string;

  /**
   * Options for the select
   */
  options: SelectOption[];

  /**
   * Placeholder text
   */
  placeholder?: string;

  /**
   * Full width select
   */
  fullWidth?: boolean;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      label,
      error,
      helperText,
      options,
      placeholder,
      fullWidth = false,
      className,
      id,
      ...props
    },
    ref
  ) => {
    const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div className={clsx('flex flex-col gap-1.5', { 'w-full': fullWidth })}>
        {label && (
          <label
            htmlFor={selectId}
            className="text-sm font-medium text-slate-200"
          >
            {label}
          </label>
        )}

        <select
          ref={ref}
          id={selectId}
          className={clsx(
            // Base styles
            'rounded-lg border px-3 py-2',
            'bg-slate-800 text-slate-200',
            'transition-colors duration-200',
            'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900',
            'cursor-pointer',

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
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}

          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>

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

Select.displayName = 'Select';
