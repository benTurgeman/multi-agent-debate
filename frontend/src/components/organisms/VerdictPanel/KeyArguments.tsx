/**
 * KeyArguments - Displays list of key arguments from the debate
 */

import React from 'react';
import clsx from 'clsx';

export interface KeyArgumentsProps {
  /**
   * Array of key arguments identified by the judge
   */
  arguments: string[];

  /**
   * Additional CSS classes
   */
  className?: string;
}

export const KeyArguments: React.FC<KeyArgumentsProps> = ({
  arguments: args,
  className,
}) => {
  if (args.length === 0) {
    return null;
  }

  return (
    <div
      className={clsx(
        'bg-slate-800 rounded-lg border border-slate-700 p-6',
        className
      )}
    >
      <h3 className="text-lg font-semibold text-slate-200 mb-4">
        Key Arguments
      </h3>
      <ul className="space-y-3">
        {args.map((argument, index) => (
          <li key={index} className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-sm font-medium">
              {index + 1}
            </span>
            <p className="text-slate-300 leading-relaxed flex-1">
              {argument}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
};
