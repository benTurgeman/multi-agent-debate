import React from 'react';
import clsx from 'clsx';

export interface TopicInputProps {
  /**
   * Current topic value
   */
  value: string;

  /**
   * Change handler
   */
  onChange: (value: string) => void;

  /**
   * Error message
   */
  error?: string;

  /**
   * Maximum character length
   */
  maxLength?: number;
}

export const TopicInput: React.FC<TopicInputProps> = ({
  value,
  onChange,
  error,
  maxLength = 500,
}) => {
  const characterCount = value.length;
  const isNearLimit = characterCount > maxLength * 0.8;

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor="topic-input" className="text-sm font-medium text-slate-200">
        Debate Topic
      </label>

      <textarea
        id="topic-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        maxLength={maxLength}
        rows={4}
        placeholder="Enter the debate topic (e.g., 'Should AI be regulated?')"
        className={clsx(
          'w-full rounded-lg border px-3 py-2 resize-none',
          'bg-slate-800 text-slate-200',
          'placeholder:text-slate-500',
          'transition-colors duration-200',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900',
          {
            'border-slate-700 focus:border-blue-500 focus:ring-blue-500': !error,
            'border-red-500 focus:border-red-500 focus:ring-red-500': error,
          }
        )}
      />

      {/* Character count and error */}
      <div className="flex items-center justify-between text-xs">
        {error ? (
          <span className="text-red-500">{error}</span>
        ) : (
          <span className="text-slate-500">
            Be specific and clear about the debate topic
          </span>
        )}

        <span
          className={clsx('font-medium', {
            'text-slate-500': !isNearLimit,
            'text-yellow-500': isNearLimit,
          })}
        >
          {characterCount} / {maxLength}
        </span>
      </div>
    </div>
  );
};
