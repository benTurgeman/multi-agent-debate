/**
 * Persona catalog API client
 */

import { apiFetch } from './config';
import type { PersonaCatalogResponse } from '../types/persona';

/**
 * Personas API methods
 */
export const personasApi = {
  /**
   * Get all available persona templates
   */
  list: async (): Promise<PersonaCatalogResponse> => {
    return apiFetch<PersonaCatalogResponse>('/api/personas');
  },
};
