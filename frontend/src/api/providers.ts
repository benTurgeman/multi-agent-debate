/**
 * Provider catalog API client
 */

import { apiFetch } from './config';
import type { ProviderCatalogResponse } from '../types';

/**
 * Providers API methods
 */
export const providersApi = {
  /**
   * Get all available LLM providers and their models
   */
  list: async (): Promise<ProviderCatalogResponse> => {
    return apiFetch<ProviderCatalogResponse>('/api/providers');
  },
};
