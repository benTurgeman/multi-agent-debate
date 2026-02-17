/**
 * Zustand store for debate configuration (creation form)
 * Manages state for creating new debates
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AgentConfig, DebateConfig } from '../types';

interface DebateConfigStore {
  // State
  topic: string;
  agents: AgentConfig[];
  numRounds: number;
  judgeConfig: AgentConfig | null;

  // Actions
  setTopic: (topic: string) => void;
  addAgent: (agent: AgentConfig) => void;
  updateAgent: (agentId: string, updates: Partial<AgentConfig>) => void;
  removeAgent: (agentId: string) => void;
  setAgents: (agents: AgentConfig[]) => void;
  setNumRounds: (rounds: number) => void;
  setJudgeConfig: (judge: AgentConfig) => void;
  getConfig: () => DebateConfig | null;
  isValid: () => boolean;
  reset: () => void;
}

const initialState = {
  topic: '',
  agents: [],
  numRounds: 3,
  judgeConfig: null,
};

export const useDebateConfigStore = create<DebateConfigStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      setTopic: (topic) => set({ topic }),

      addAgent: (agent) =>
        set((state) => ({
          agents: [...state.agents, agent],
        })),

      updateAgent: (agentId, updates) =>
        set((state) => ({
          agents: state.agents.map((agent) =>
            agent.agent_id === agentId ? { ...agent, ...updates } : agent
          ),
        })),

      removeAgent: (agentId) =>
        set((state) => ({
          agents: state.agents.filter((agent) => agent.agent_id !== agentId),
        })),

      setAgents: (agents) => set({ agents }),

      setNumRounds: (rounds) => set({ numRounds: Math.max(1, rounds) }),

      setJudgeConfig: (judge) => set({ judgeConfig: judge }),

      getConfig: () => {
        const state = get();
        if (!state.isValid()) return null;

        return {
          topic: state.topic,
          num_rounds: state.numRounds,
          agents: state.agents,
          judge_config: state.judgeConfig!,
        };
      },

      isValid: () => {
        const state = get();
        return (
          state.topic.trim().length > 0 &&
          state.agents.length >= 2 &&
          state.numRounds >= 1 &&
          state.judgeConfig !== null
        );
      },

      reset: () => set(initialState),
    }),
    {
      name: 'debate-config-storage', // localStorage key
      partialize: (state) => ({
        // Only persist these fields
        topic: state.topic,
        agents: state.agents,
        numRounds: state.numRounds,
        judgeConfig: state.judgeConfig,
      }),
    }
  )
);
