import React from 'react';
import { Input } from '../../atoms';

export interface RoundsInputProps {
  /**
   * Current number of rounds
   */
  value: number;

  /**
   * Change handler
   */
  onChange: (value: number) => void;

  /**
   * Minimum rounds allowed
   */
  min?: number;

  /**
   * Maximum rounds allowed
   */
  max?: number;
}

export const RoundsInput: React.FC<RoundsInputProps> = ({
  value,
  onChange,
  min = 1,
  max = 10,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value, 10);
    if (!isNaN(newValue)) {
      onChange(Math.max(min, Math.min(max, newValue)));
    }
  };

  return (
    <Input
      type="number"
      label="Number of Rounds"
      value={value}
      onChange={handleChange}
      min={min}
      max={max}
      helperText={`Each agent speaks once per round (${min}-${max} rounds)`}
      fullWidth
    />
  );
};
