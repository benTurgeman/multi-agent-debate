import React from 'react';
import { Trash2 } from 'lucide-react';
import { AgentConfig } from '../../../types';
import { Badge, Button } from '../../atoms';

export interface ParticipantsListProps {
  /**
   * List of agent configurations
   */
  agents: AgentConfig[];

  /**
   * Handler for removing an agent
   */
  onRemove: (agentId: string) => void;

  /**
   * Handler for adding a new agent
   */
  onAdd: () => void;
}

export const ParticipantsList: React.FC<ParticipantsListProps> = ({
  agents,
  onRemove,
  onAdd,
}) => {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-slate-200">
          Participants ({agents.length})
        </label>
        <Button size="sm" variant="primary" onClick={onAdd}>
          + Add Agent
        </Button>
      </div>

      {agents.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-700 bg-slate-800/50 px-4 py-8 text-center">
          <p className="text-sm text-slate-400 mb-2">No agents added yet</p>
          <p className="text-xs text-slate-500">
            Add at least 2 agents to start a debate
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {agents.map((agent) => (
            <div
              key={agent.agent_id}
              className="rounded-lg border border-slate-700 bg-slate-800 p-3 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-sm font-semibold text-slate-200 truncate">
                      {agent.name}
                    </h4>
                    <Badge
                      variant={
                        agent.stance.toLowerCase() === 'pro'
                          ? 'pro'
                          : agent.stance.toLowerCase() === 'con'
                          ? 'con'
                          : 'neutral'
                      }
                      size="sm"
                    >
                      {agent.stance}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-400 truncate">
                    {agent.llm_config.model_name}
                  </p>
                </div>

                <button
                  onClick={() => onRemove(agent.agent_id)}
                  className="flex-shrink-0 p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-red-500 transition-colors"
                  aria-label="Remove agent"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {agents.length > 0 && agents.length < 2 && (
        <p className="text-xs text-yellow-500">
          Add at least one more agent to start a debate
        </p>
      )}
    </div>
  );
};
