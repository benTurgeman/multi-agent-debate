/**
 * Zustand store for UI state and preferences
 * Manages UI-specific state (dark mode, current view, modals, etc.)
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type ViewMode = 'config' | 'debate' | 'results';

interface UIStore {
  // State
  darkMode: boolean;
  currentView: ViewMode;
  isAddAgentModalOpen: boolean;
  isExportMenuOpen: boolean;
  activeDebateId: string | null;

  // Actions
  toggleDarkMode: () => void;
  setDarkMode: (enabled: boolean) => void;
  setCurrentView: (view: ViewMode) => void;
  openAddAgentModal: () => void;
  closeAddAgentModal: () => void;
  toggleExportMenu: () => void;
  closeExportMenu: () => void;
  setActiveDebateId: (debateId: string | null) => void;
  reset: () => void;
}

const initialState = {
  darkMode: true, // Default to dark mode
  currentView: 'config' as ViewMode,
  isAddAgentModalOpen: false,
  isExportMenuOpen: false,
  activeDebateId: null,
};

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      ...initialState,

      toggleDarkMode: () =>
        set((state) => {
          const newDarkMode = !state.darkMode;
          // Update DOM
          if (newDarkMode) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
          return { darkMode: newDarkMode };
        }),

      setDarkMode: (enabled) =>
        set(() => {
          // Update DOM
          if (enabled) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
          return { darkMode: enabled };
        }),

      setCurrentView: (view) => set({ currentView: view }),

      openAddAgentModal: () => set({ isAddAgentModalOpen: true }),

      closeAddAgentModal: () => set({ isAddAgentModalOpen: false }),

      toggleExportMenu: () =>
        set((state) => ({ isExportMenuOpen: !state.isExportMenuOpen })),

      closeExportMenu: () => set({ isExportMenuOpen: false }),

      setActiveDebateId: (debateId) => set({ activeDebateId: debateId }),

      reset: () => set({ ...initialState, darkMode: true }), // Keep dark mode on reset
    }),
    {
      name: 'ui-storage', // localStorage key
      partialize: (state) => ({
        // Only persist these fields
        darkMode: state.darkMode,
      }),
    }
  )
);
