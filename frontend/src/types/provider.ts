/**
 * Provider catalog models - mirrors backend/models/provider_catalog.py
 */

import { ModelProvider } from './llm';

export interface ModelInfo {
  model_id: string;
  display_name: string;
  description: string;
  context_window: number;
  max_output_tokens: number;
  recommended: boolean;
  pricing_tier: string;
}

export interface ProviderInfo {
  provider_id: ModelProvider;
  display_name: string;
  description: string;
  api_key_env_var: string;
  documentation_url: string;
  models: ModelInfo[];
}

export interface ProviderCatalogResponse {
  providers: ProviderInfo[];
}
