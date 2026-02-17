import React, { useState } from 'react';
import { useDebateConfigStore } from '../../../stores';
import { TopicInput } from './TopicInput';
import { RoundsInput } from './RoundsInput';
import { ParticipantsList } from './ParticipantsList';
import { JudgeSelect } from './JudgeSelect';
import { AddParticipantModal } from './AddParticipantModal';
import { Button } from '../../atoms';

export interface DebateConfigProps {
  /**
   * Handler for starting the debate
   */
  onStartDebate?: () => void;

  /**
   * Whether debate is being created
   */
  isCreating?: boolean;
}

export const DebateConfig: React.FC<DebateConfigProps> = ({
  onStartDebate,
  isCreating = false,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const {
    topic,
    agents,
    numRounds,
    judgeConfig,
    setTopic,
    addAgent,
    removeAgent,
    setNumRounds,
    setJudgeConfig,
    isValid,
  } = useDebateConfigStore();

  const canStartDebate = isValid() && !isCreating;

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100 mb-1">
          Debate Configuration
        </h2>
        <p className="text-sm text-slate-400">
          Set up your debate topic, participants, and rules
        </p>
      </div>

      {/* Topic Input */}
      <TopicInput
        value={topic}
        onChange={setTopic}
        error={topic.trim().length === 0 ? undefined : ''}
      />

      {/* Participants List */}
      <ParticipantsList
        agents={agents}
        onRemove={removeAgent}
        onAdd={() => setIsModalOpen(true)}
      />

      {/* Rounds Input */}
      <RoundsInput value={numRounds} onChange={setNumRounds} />

      {/* Judge Select */}
      <JudgeSelect value={judgeConfig} onChange={setJudgeConfig} />

      {/* Start Debate Button */}
      <div className="pt-4 border-t border-slate-700">
        <Button
          variant="primary"
          onClick={onStartDebate}
          disabled={!canStartDebate}
          isLoading={isCreating}
          fullWidth
          size="lg"
        >
          {isCreating ? 'Creating Debate...' : 'Create Debate'}
        </Button>

        {!isValid() && (
          <p className="text-xs text-yellow-500 mt-2 text-center">
            {!topic.trim()
              ? 'Enter a debate topic'
              : agents.length < 2
              ? 'Add at least 2 agents'
              : !judgeConfig
              ? 'Select a judge model'
              : 'Complete all fields to start'}
          </p>
        )}
      </div>

      {/* Add Participant Modal */}
      <AddParticipantModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={addAgent}
      />
    </div>
  );
};
