/**
 * Zustand store for active debate state
 * Manages real-time debate data from WebSocket events
 */

import { create } from 'zustand';
import { DebateState, DebateStatus, Message, JudgeResult } from '../types';

type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

interface ThinkingAgent {
  agent_id: string;
  agent_name: string;
}

interface DebateStateStore {
  // State
  debate: DebateState | null;
  connectionState: ConnectionState;
  thinkingAgents: ThinkingAgent[];
  errorMessage: string | null;

  // Actions
  setDebate: (debate: DebateState) => void;
  updateDebateStatus: (status: DebateStatus) => void;
  setCurrentRound: (round: number) => void;
  setCurrentTurn: (turn: number) => void;
  addMessage: (message: Message) => void;
  setJudgeResult: (result: JudgeResult) => void;
  setConnectionState: (state: ConnectionState) => void;
  addThinkingAgent: (agentId: string, agentName: string) => void;
  removeThinkingAgent: (agentId: string) => void;
  setError: (error: string | null) => void;
  reset: () => void;

  // Computed helpers
  getCurrentAgent: () => string | null;
  getMessageCount: () => number;
  getAgentMessageCount: (agentId: string) => number;
}

const initialState = {
  debate: null,
  connectionState: 'disconnected' as ConnectionState,
  thinkingAgents: [],
  errorMessage: null,
};

export const useDebateStateStore = create<DebateStateStore>((set, get) => ({
  ...initialState,

  setDebate: (debate) => set({ debate }),

  updateDebateStatus: (status) =>
    set((state) => ({
      debate: state.debate
        ? { ...state.debate, status }
        : null,
    })),

  setCurrentRound: (round) =>
    set((state) => ({
      debate: state.debate
        ? { ...state.debate, current_round: round }
        : null,
    })),

  setCurrentTurn: (turn) =>
    set((state) => ({
      debate: state.debate
        ? { ...state.debate, current_turn: turn }
        : null,
    })),

  addMessage: (message) =>
    set((state) => ({
      debate: state.debate
        ? {
            ...state.debate,
            history: [...state.debate.history, message],
          }
        : null,
    })),

  setJudgeResult: (result) =>
    set((state) => ({
      debate: state.debate
        ? { ...state.debate, judge_result: result }
        : null,
    })),

  setConnectionState: (connectionState) => set({ connectionState }),

  addThinkingAgent: (agent_id, agent_name) =>
    set((state) => ({
      thinkingAgents: [
        ...state.thinkingAgents.filter((a) => a.agent_id !== agent_id),
        { agent_id, agent_name },
      ],
    })),

  removeThinkingAgent: (agentId) =>
    set((state) => ({
      thinkingAgents: state.thinkingAgents.filter((a) => a.agent_id !== agentId),
    })),

  setError: (errorMessage) => set({ errorMessage }),

  reset: () => set(initialState),

  // Computed helpers
  getCurrentAgent: () => {
    const state = get();
    if (!state.debate) return null;

    const { config, current_turn } = state.debate;
    const agentIndex = current_turn % config.agents.length;
    return config.agents[agentIndex]?.agent_id || null;
  },

  getMessageCount: () => {
    const state = get();
    return state.debate?.history.length || 0;
  },

  getAgentMessageCount: (agentId: string) => {
    const state = get();
    if (!state.debate) return 0;

    return state.debate.history.filter((msg) => msg.agent_id === agentId).length;
  },
}));
