/**
 * Debates API client
 */

import { apiFetch } from './config';
import type { DebateConfig, DebateState } from '../types';

export interface CreateDebateResponse {
  debate_id: string;
  message: string;
}

export interface StartDebateResponse {
  message: string;
  debate_id: string;
}

export type ExportFormat = 'json' | 'markdown' | 'text';

/**
 * Debates API methods
 */
export const debatesApi = {
  /**
   * Create a new debate
   */
  create: async (config: DebateConfig): Promise<CreateDebateResponse> => {
    return apiFetch<CreateDebateResponse>('/api/debates', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },

  /**
   * Get debate state by ID
   */
  get: async (debateId: string): Promise<DebateState> => {
    return apiFetch<DebateState>(`/api/debates/${debateId}`);
  },

  /**
   * Start a debate
   */
  start: async (debateId: string): Promise<StartDebateResponse> => {
    return apiFetch<StartDebateResponse>(`/api/debates/${debateId}/start`, {
      method: 'POST',
    });
  },

  /**
   * Export debate results
   */
  export: async (debateId: string, format: ExportFormat): Promise<Blob> => {
    const response = await fetch(
      `/api/debates/${debateId}/export?format=${format}`
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    return response.blob();
  },

  /**
   * Download export as file
   */
  downloadExport: async (
    debateId: string,
    format: ExportFormat,
    filename?: string
  ): Promise<void> => {
    const blob = await debatesApi.export(debateId, format);

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || `debate-${debateId}.${format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },
};
